from __future__ import annotations

import json
import sqlite3
from typing import Any, Mapping

from standards_bridge.profiles.specification import ContractError, canonical_json, stable_hash, utc_now

REVISION_TABLES = """
CREATE TABLE IF NOT EXISTS mapping_revision_queue(
    queue_id TEXT PRIMARY KEY,
    mapping_id TEXT NOT NULL,
    case_id TEXT NOT NULL,
    from_revision INTEGER NOT NULL,
    to_revision INTEGER NOT NULL,
    status TEXT NOT NULL,
    requested_at TEXT NOT NULL,
    completed_at TEXT,
    result_json TEXT NOT NULL,
    UNIQUE(mapping_id, case_id, to_revision),
    FOREIGN KEY(mapping_id) REFERENCES standard_mappings(mapping_id)
);
CREATE TABLE IF NOT EXISTS comparability_snapshots(
    snapshot_id TEXT PRIMARY KEY,
    mapping_id TEXT NOT NULL,
    mapping_revision INTEGER NOT NULL,
    pair_key TEXT NOT NULL,
    left_case_id TEXT NOT NULL,
    right_case_id TEXT NOT NULL,
    layer TEXT NOT NULL,
    reasons_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_revision_queue_status ON mapping_revision_queue(status, mapping_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_revision ON comparability_snapshots(mapping_id, mapping_revision);
"""

ACTIVE_STATUSES = ("pending", "in_progress")


def prepare_revision_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(REVISION_TABLES)


def queue_mapping_revision(connection: sqlite3.Connection, mapping_id: str,
                           from_revision: int, to_revision: int) -> list[str]:
    """Open revalidation requests only for cases with a real dependency on the mapping.

    A shared mapping therefore propagates one request to every linked market/case,
    while cases linked to other mappings are never touched. Already-signed
    certifications keep their original revision as evidence and are flagged stale
    separately instead of being overwritten.
    """
    prepare_revision_tables(connection)
    case_ids = [row[0] for row in connection.execute(
        "SELECT case_id FROM case_mapping_usage WHERE mapping_id=? ORDER BY case_id", (mapping_id,))]
    now = utc_now()
    queued: list[str] = []
    for case_id in case_ids:
        queue_id = stable_hash({"mapping_id": mapping_id, "case_id": case_id,
                                "from_revision": from_revision, "to_revision": to_revision})
        connection.execute(
            "INSERT OR IGNORE INTO mapping_revision_queue"
            "(queue_id,mapping_id,case_id,from_revision,to_revision,status,requested_at,completed_at,result_json)"
            " VALUES(?,?,?,?,?,?,?,?,?)",
            (queue_id, mapping_id, case_id, from_revision, to_revision, "pending", now, None, "{}"))
        queued.append(case_id)
        connection.execute(
            "UPDATE certifications SET stale=1 WHERE mapping_id=? AND case_id=? AND mapping_revision<?",
            (mapping_id, case_id, to_revision))
    return queued


def open_requests_for_case(connection: sqlite3.Connection, case_id: str) -> list[sqlite3.Row]:
    prepare_revision_tables(connection)
    placeholders = ",".join("?" for _ in ACTIVE_STATUSES)
    return list(connection.execute(
        f"SELECT * FROM mapping_revision_queue WHERE case_id=? AND status IN ({placeholders}) ORDER BY requested_at",
        (case_id, *ACTIVE_STATUSES)))


def record_comparability_snapshot(connection: sqlite3.Connection, mapping_id: str,
                                  mapping_revision: int, pair_rows: list[Mapping[str, Any]]) -> int:
    prepare_revision_tables(connection)
    now = utc_now()
    stored = 0
    for row in pair_rows:
        pair_key = stable_hash({"left": row["left"], "right": row["right"], "mapping_id": mapping_id})
        snapshot_id = stable_hash({"pair_key": pair_key, "layer": row["layer"],
                                   "reasons": row.get("reasons", []), "revision": mapping_revision})
        connection.execute(
            "INSERT OR IGNORE INTO comparability_snapshots"
            "(snapshot_id,mapping_id,mapping_revision,pair_key,left_case_id,right_case_id,layer,reasons_json,created_at)"
            " VALUES(?,?,?,?,?,?,?,?,?)",
            (snapshot_id, mapping_id, mapping_revision, pair_key, row["left"], row["right"],
             row["layer"], canonical_json(row.get("reasons", [])), now))
        stored += 1
    return stored


def complete_revalidation(connection: sqlite3.Connection, mapping_id: str, case_id: str,
                          result: Mapping[str, Any]) -> dict[str, Any]:
    prepare_revision_tables(connection)
    rows = open_requests_for_case(connection, case_id)
    target = [row for row in rows if row["mapping_id"] == mapping_id]
    if not target:
        raise ContractError("no open revalidation request for this case and mapping")
    if not isinstance(result, Mapping) or str(result.get("outcome", "")).strip() == "":
        raise ContractError("revalidation result requires an outcome")
    now = utc_now()
    completed: list[dict[str, Any]] = []
    for row in target:
        status = "passed" if result["outcome"] == "approve" else "failed"
        connection.execute(
            "UPDATE mapping_revision_queue SET status=?,completed_at=?,result_json=? WHERE queue_id=?",
            (status, now, canonical_json(dict(result)), row["queue_id"]))
        completed.append({"queue_id": row["queue_id"], "to_revision": row["to_revision"], "status": status})
    return {"mapping_id": mapping_id, "case_id": case_id, "closed_requests": completed, "completed_at": now}


def _last_two_revisions(connection: sqlite3.Connection, mapping_id: str) -> list[sqlite3.Row]:
    return list(connection.execute(
        "SELECT DISTINCT mapping_revision FROM comparability_snapshots WHERE mapping_id=?"
        " ORDER BY mapping_revision DESC LIMIT 2", (mapping_id,)))


def revision_report(connection: sqlite3.Connection, mapping_id: str) -> dict[str, Any]:
    """What one revision changed: revalidation queue plus comparability-layer diffs."""
    prepare_revision_tables(connection)
    mapping = connection.execute("SELECT * FROM standard_mappings WHERE mapping_id=?", (mapping_id,)).fetchone()
    if mapping is None:
        raise ContractError("unknown mapping")
    queue_rows = list(connection.execute(
        "SELECT * FROM mapping_revision_queue WHERE mapping_id=? ORDER BY case_id,to_revision", (mapping_id,)))
    requests = [dict(row) | {"result": json.loads(row["result_json"])} for row in queue_rows]
    open_requests = [item for item in requests if item["status"] in ACTIVE_STATUSES]
    certifications = [dict(row) for row in connection.execute(
        "SELECT * FROM certifications WHERE mapping_id=? ORDER BY signed_at,certification_id", (mapping_id,))]

    revisions = _last_two_revisions(connection, mapping_id)
    pair_changes: list[dict[str, Any]] = []
    if len(revisions) == 2:
        new_rev, old_rev = revisions[0]["mapping_revision"], revisions[1]["mapping_revision"]
        new_rows = {row["pair_key"]: row for row in connection.execute(
            "SELECT * FROM comparability_snapshots WHERE mapping_id=? AND mapping_revision=?",
            (mapping_id, new_rev))}
        old_rows = {row["pair_key"]: row for row in connection.execute(
            "SELECT * FROM comparability_snapshots WHERE mapping_id=? AND mapping_revision=?",
            (mapping_id, old_rev))}
        for pair_key in sorted(set(new_rows) | set(old_rows)):
            new_row = new_rows.get(pair_key)
            old_row = old_rows.get(pair_key)
            old_layer = old_row["layer"] if old_row else "not_assessed"
            new_layer = new_row["layer"] if new_row else "not_assessed"
            if old_layer == new_layer:
                continue
            pair_changes.append({
                "pair_key": pair_key,
                "left_case_id": (new_row or old_row)["left_case_id"],
                "right_case_id": (new_row or old_row)["right_case_id"],
                "from_layer": old_layer, "to_layer": new_layer,
                "from_reasons": json.loads(old_row["reasons_json"]) if old_row else [],
                "to_reasons": json.loads(new_row["reasons_json"]) if new_row else []})
    return {
        "mapping_id": mapping_id,
        "current_revision": mapping["revision"],
        "revalidation": {
            "total_requests": len(requests),
            "open_requests": len(open_requests),
            "open_case_ids": sorted(item["case_id"] for item in open_requests),
            "passed": sum(item["status"] == "passed" for item in requests),
            "failed": sum(item["status"] == "failed" for item in requests),
            "requests": requests,
        },
        "pair_changes": pair_changes,
        "stale_certifications": [item for item in certifications if item.get("stale")],
        "signed_certifications": certifications,
    }


def pending_revalidation_overview(connection: sqlite3.Connection) -> dict[str, Any]:
    prepare_revision_tables(connection)
    placeholders = ",".join("?" for _ in ACTIVE_STATUSES)
    rows = list(connection.execute(
        f"SELECT * FROM mapping_revision_queue WHERE status IN ({placeholders})"
        " ORDER BY mapping_id,case_id", ACTIVE_STATUSES))
    by_mapping: dict[str, list[str]] = {}
    for row in rows:
        by_mapping.setdefault(row["mapping_id"], []).append(row["case_id"])
    return {"open_request_count": len(rows),
            "by_mapping": {mapping_id: sorted(set(case_ids)) for mapping_id, case_ids in sorted(by_mapping.items())}}

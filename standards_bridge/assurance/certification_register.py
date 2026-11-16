from __future__ import annotations

import json
import sqlite3
from typing import Any

from standards_bridge.profiles.specification import ContractError, canonical_json, stable_hash, utc_now


def prepare_certifications(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE IF NOT EXISTS standard_mappings(
        mapping_id TEXT PRIMARY KEY, source_standard TEXT NOT NULL,
        target_standard TEXT NOT NULL, mapping_json TEXT NOT NULL,
        revision INTEGER NOT NULL, updated_at TEXT NOT NULL
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS case_mapping_usage(
        case_id TEXT NOT NULL, mapping_id TEXT NOT NULL,
        PRIMARY KEY(case_id,mapping_id),
        FOREIGN KEY(mapping_id) REFERENCES standard_mappings(mapping_id)
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS certifications(
        certification_id TEXT PRIMARY KEY, case_id TEXT NOT NULL,
        mapping_id TEXT NOT NULL, mapping_revision INTEGER NOT NULL,
        evidence_hash TEXT NOT NULL, signed_at TEXT NOT NULL,
        FOREIGN KEY(mapping_id) REFERENCES standard_mappings(mapping_id)
    )""")


def register_mapping(connection: sqlite3.Connection, mapping_id: str, source: str,
                     target: str, aliases: dict[str, str]) -> int:
    prepare_certifications(connection)
    if not all(isinstance(value, str) and value.strip() for value in (mapping_id, source, target)):
        raise ContractError("mapping identity and standard pair are required")
    if not isinstance(aliases, dict) or any(not isinstance(key, str) or not isinstance(value, str)
                                            for key, value in aliases.items()):
        raise ContractError("mapping aliases must be text")
    body = canonical_json(aliases)
    existing = connection.execute("SELECT * FROM standard_mappings WHERE mapping_id=?", (mapping_id,)).fetchone()
    if existing:
        if existing["source_standard"] != source or existing["target_standard"] != target:
            raise ContractError("mapping identity belongs to another standard pair")
        if existing["mapping_json"] == body:
            return existing["revision"]
        revision = existing["revision"] + 1
        connection.execute("UPDATE standard_mappings SET mapping_json=?,revision=?,updated_at=? WHERE mapping_id=?",
                           (body, revision, utc_now(), mapping_id))
        return revision
    connection.execute("INSERT INTO standard_mappings VALUES(?,?,?,?,?,?)",
                       (mapping_id, source, target, body, 1, utc_now()))
    return 1


def link_case(connection: sqlite3.Connection, case_id: str, mapping_id: str) -> None:
    prepare_certifications(connection)
    if not connection.execute("SELECT 1 FROM standard_mappings WHERE mapping_id=?", (mapping_id,)).fetchone():
        raise ContractError("unknown mapping")
    connection.execute("INSERT OR IGNORE INTO case_mapping_usage VALUES(?,?)", (case_id, mapping_id))


def sign_case(connection: sqlite3.Connection, certification_id: str, case_id: str,
              mapping_id: str, evidence: dict[str, Any]) -> dict[str, Any]:
    prepare_certifications(connection)
    if not connection.execute("SELECT 1 FROM case_mapping_usage WHERE case_id=? AND mapping_id=?",
                              (case_id, mapping_id)).fetchone():
        raise ContractError("case has no recorded mapping dependency")
    revision = connection.execute("SELECT revision FROM standard_mappings WHERE mapping_id=?", (mapping_id,)).fetchone()[0]
    fingerprint = stable_hash({"case_id": case_id, "mapping_id": mapping_id,
                               "revision": revision, "evidence": evidence})
    old = connection.execute("SELECT * FROM certifications WHERE certification_id=?", (certification_id,)).fetchone()
    if old:
        if (old["case_id"], old["mapping_id"], old["mapping_revision"], old["evidence_hash"]) != (
                case_id, mapping_id, revision, fingerprint):
            raise ContractError("signed certification cannot be overwritten")
        return dict(old)
    connection.execute("INSERT INTO certifications VALUES(?,?,?,?,?,?)",
                       (certification_id, case_id, mapping_id, revision, fingerprint, utc_now()))
    return dict(connection.execute("SELECT * FROM certifications WHERE certification_id=?", (certification_id,)).fetchone())


def mapping_impact(connection: sqlite3.Connection, mapping_id: str) -> dict[str, Any]:
    prepare_certifications(connection)
    row = connection.execute("SELECT * FROM standard_mappings WHERE mapping_id=?", (mapping_id,)).fetchone()
    if row is None:
        raise ContractError("unknown mapping")
    cases = [item[0] for item in connection.execute(
        "SELECT case_id FROM case_mapping_usage WHERE mapping_id=? ORDER BY case_id", (mapping_id,))]
    issued = [dict(item) for item in connection.execute(
        "SELECT * FROM certifications WHERE mapping_id=? ORDER BY signed_at,certification_id", (mapping_id,))]
    return {"mapping_id": mapping_id, "revision": row["revision"], "aliases": json.loads(row["mapping_json"]),
            "affected_cases": cases, "signed_certifications": issued}

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from standards_bridge.profiles.specification import ContractError, Decision, DomainRecord, records_from_fixture, stable_hash
from standards_bridge.assurance.case_ledger import Repository
from standards_bridge.laboratory.certification import advance_for_outcome, decide
from standards_bridge.artifacts.conformance_report import export_bundle, verify_bundle
from standards_bridge.mappings.semantic_bridge import derive_context
from standards_bridge.economics.comparability import (
    assess_pair,
    bridge_quality,
    build_mapping_graph,
    reuse_eligibility,
    stratified_pass_rates,
)


class Application:
    def __init__(self, database: str | Path, context: Mapping[str, Any] | None = None):
        self.repository = Repository(database)
        self.context = dict(context or {})

    def ingest(self, record: DomainRecord) -> DomainRecord:
        current = self.repository.get_record(record.record_id)
        if current is None:
            self.repository.save_record(record)
            return record
        if current.fingerprint == record.fingerprint:
            return current
        replacement = DomainRecord(record.record_id, record.payload, current.state,
                                   current.version + 1, record.occurred_at, record.source)
        self.repository.save_record(replacement, expected_version=current.version)
        return replacement

    def process(self, record: DomainRecord) -> tuple[DomainRecord, Decision]:
        stored = self.ingest(record)
        context = dict(self.context)
        context.update(derive_context(stored, self.repository))
        decision = decide(stored, context)
        self.repository.save_decision(decision)
        advanced = advance_for_outcome(stored, decision)
        if advanced.fingerprint != stored.fingerprint:
            self.repository.save_record(advanced, expected_version=stored.version)
        return advanced, decision

    def run_fixture(self, fixture: Mapping[str, Any], output: str | Path) -> dict[str, Any]:
        records = records_from_fixture(fixture)
        fixture_hash = stable_hash(fixture)
        run_id = self.repository.begin_run(fixture_hash, len(records))
        completed = self.repository.completed_run(run_id)
        if completed is not None:
            return completed
        decisions: dict[str, Decision] = {}
        final_records: list[DomainRecord] = []
        for record in records:
            final_record, decision = self.process(record)
            final_records.append(final_record)
            decisions[record.record_id] = decision
        snapshot = self.repository.snapshot()
        if snapshot["chain_errors"]:
            raise ContractError("audit chain verification failed")
        manifest = export_bundle(output, final_records, decisions, snapshot, self.repository.event_rows())
        result = {"run_id": run_id, "fixture_hash": fixture_hash, "records": len(final_records),
                  "decisions": len(decisions), "manifest": manifest, "snapshot": snapshot}
        self.repository.finish_run(run_id, result)
        return result

    def inspect(self) -> dict[str, Any]:
        return {"snapshot": self.repository.snapshot(), "records": [record.__dict__ for record in self.repository.list_records()],
                "decisions": self.repository.decision_rows(),
                "revalidation": self.repository.pending_revalidation()}

    def register_mapping(self, mapping_id: str, source: str, target: str, aliases: dict[str, str]) -> int:
        return self.repository.register_mapping(mapping_id, source, target, aliases)

    def mapping_impact(self, mapping_id: str) -> dict[str, Any]:
        return self.repository.mapping_impact(mapping_id)

    def _comparability_inputs(self) -> tuple[list[DomainRecord], dict[str, set[str]], dict[tuple[str, str], dict[str, Any]]]:
        records = self.repository.list_records()
        mapping_rows = self.repository.mapping_graph_rows()
        graph = build_mapping_graph(mapping_rows)
        bridges = bridge_quality(mapping_rows)
        return records, graph, bridges

    def compare_cases(self, left_id: str, right_id: str) -> dict[str, Any]:
        """Layer one case pair; never averages unlike units or waiver calibers."""
        left = self.repository.get_record(left_id)
        right = self.repository.get_record(right_id)
        if left is None or right is None:
            raise ContractError("unknown case in comparison")
        _, graph, bridges = self._comparability_inputs()
        return assess_pair(left, right, graph, self.context, bridges)

    def comparability_view(self) -> dict[str, Any]:
        """Stratified pass rates and per-case reuse judgements from current evidence."""
        records, graph, bridges = self._comparability_inputs()
        blocked = self.repository.blocked_revalidation_cases()
        strata = stratified_pass_rates(records, graph, self.context, bridges)
        eligibility = reuse_eligibility(records, graph, self.context, blocked, bridges)
        return {"case_count": len(records),
                "stratified_pass_rates": strata,
                "reuse_eligibility": eligibility,
                "revalidation": self.repository.pending_revalidation()}

    def revalidate_case(self, mapping_id: str, case_id: str, result: dict[str, Any]) -> dict[str, Any]:
        """Close a real revalidation request and re-assess comparisons on the new revision."""
        impact = self.repository.mapping_impact(mapping_id)
        if case_id not in impact["affected_cases"]:
            raise ContractError("case has no dependency on this mapping; it must not be revalidated")
        closed = self.repository.complete_case_revalidation(mapping_id, case_id, result)
        records, graph, bridges = self._comparability_inputs()
        pair_rows = [row for row in reuse_eligibility(records, graph, self.context, bridges=bridges)["pairs"]
                     if case_id in (row["left"], row["right"])]
        self.repository.snapshot_comparability(mapping_id, impact["revision"], pair_rows)
        refreshed = self.comparability_view()
        case_view = refreshed["reuse_eligibility"]["cases"].get(case_id)
        still_blocked = case_id in self.repository.blocked_revalidation_cases()
        if case_view is not None and not still_blocked:
            outcome = closed["closed_requests"][-1]["status"]
            case_view = dict(case_view)
            if outcome == "passed":
                case_view["status"] = "reuse_supported"
                case_view["reasons"] = ["revalidated_on_current_revision"]
            else:
                case_view["status"] = "not_comparable"
                case_view["reasons"] = ["revalidation_failed"]
        return {"closed": closed, "current_revision": impact["revision"],
                "refreshed_eligibility": case_view,
                "revalidation": refreshed["revalidation"]}

    def revision_view(self, mapping_id: str) -> dict[str, Any]:
        """What one revision changed: layer diffs, open revalidations, stale certifications."""
        report = self.repository.revision_report(mapping_id)
        records, graph, bridges = self._comparability_inputs()
        blocked = self.repository.blocked_revalidation_cases()
        report["current_reuse_eligibility"] = reuse_eligibility(
            records, graph, self.context, blocked, bridges)["cases"]
        return report


def load_fixture(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read fixture: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("fixture root must be an object")
    return value


def run(fixture_path: str | Path, database: str | Path, output: str | Path,
        context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return Application(database, context).run_fixture(load_fixture(fixture_path), output)


def verify(database: str | Path, output: str | Path) -> dict[str, Any]:
    repository = Repository(database)
    chain_errors = repository.verify_chain()
    bundle_errors = verify_bundle(output)
    return {"ok": not chain_errors and not bundle_errors, "chain_errors": chain_errors,
            "bundle_errors": bundle_errors, "snapshot": repository.snapshot()}

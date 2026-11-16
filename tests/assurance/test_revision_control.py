from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from standards_bridge.assurance.case_ledger import Repository
from standards_bridge.profiles.specification import ContractError, DomainRecord


class RevisionControlTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.database = Path(temporary.name) / "revisions.sqlite3"
        self.repository = Repository(self.database)
        for case_id in ("case-a", "case-b", "case-c", "case-d"):
            self.repository.save_record(DomainRecord(case_id, {"target_market": "market-1"}))
        self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "temp"})
        self.repository.register_mapping("map-2", "spec-c", "spec-d", {"weight": "mass"})
        self.repository.link_case_mapping("case-a", "map-1")
        self.repository.link_case_mapping("case-b", "map-1")
        self.repository.link_case_mapping("case-c", "map-2")

    def test_revision_propagates_only_along_recorded_dependencies(self):
        self.assertEqual(self.repository.register_mapping(
            "map-1", "spec-a", "spec-b", {"temperature": "ambient"}), 2)
        overview = self.repository.pending_revalidation()
        self.assertEqual(overview["open_request_count"], 2)
        self.assertEqual(overview["by_mapping"], {"map-1": ["case-a", "case-b"]})
        impact = self.repository.mapping_impact("map-1")
        self.assertEqual(impact["open_revalidation_cases"], ["case-a", "case-b"])
        # cases linked only to other mappings are never queued or rerun
        self.assertEqual(self.repository.mapping_impact("map-2")["open_revalidation_cases"], [])

    def test_signed_certification_keeps_old_revision_and_is_flagged_stale(self):
        first = self.repository.sign_case("cert-a", "case-a", "map-1", {"accepted": True})
        self.assertEqual(first["mapping_revision"], 1)
        self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "ambient"})
        impact = self.repository.mapping_impact("map-1")
        retained = impact["signed_certifications"][0]
        self.assertEqual(retained["mapping_revision"], 1)
        self.assertEqual(impact["stale_certification_ids"], ["cert-a"])
        with self.assertRaisesRegex(ContractError, "cannot be overwritten"):
            self.repository.sign_case("cert-a", "case-a", "map-1", {"accepted": True})

    def test_new_signature_is_blocked_until_revalidation_completes(self):
        self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "ambient"})
        with self.assertRaisesRegex(ContractError, "open revalidation requests"):
            self.repository.sign_case("cert-b", "case-b", "map-1", {"accepted": True})
        result = self.repository.complete_case_revalidation("map-1", "case-b", {"outcome": "approve"})
        self.assertEqual(result["closed_requests"][0]["status"], "passed")
        signed = self.repository.sign_case("cert-b", "case-b", "map-1", {"accepted": True})
        self.assertEqual(signed["mapping_revision"], 2)
        self.assertEqual(signed["stale"], 0)

    def test_revalidation_requires_a_real_open_request(self):
        self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "ambient"})
        with self.assertRaisesRegex(ContractError, "no open revalidation request"):
            self.repository.complete_case_revalidation("map-1", "case-c", {"outcome": "approve"})
        with self.assertRaisesRegex(ContractError, "no open revalidation request"):
            self.repository.complete_case_revalidation("map-1", "case-d", {"outcome": "approve"})
        with self.assertRaisesRegex(ContractError, "outcome"):
            self.repository.complete_case_revalidation("map-1", "case-a", {"note": "missing outcome"})

    def test_revision_report_tracks_open_vs_closed_requests(self):
        self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "ambient"})
        self.repository.complete_case_revalidation("map-1", "case-a", {"outcome": "reject"})
        report = self.repository.revision_report("map-1")
        self.assertEqual(report["current_revision"], 2)
        self.assertEqual(report["revalidation"]["total_requests"], 2)
        self.assertEqual(report["revalidation"]["passed"], 0)
        self.assertEqual(report["revalidation"]["failed"], 1)
        self.assertEqual(report["revalidation"]["open_case_ids"], ["case-b"])

    def test_revision_report_detects_comparability_layer_changes(self):
        pair_old = [{"left": "case-a", "right": "case-b", "layer": "comparable", "reasons": []}]
        pair_new = [{"left": "case-a", "right": "case-b", "layer": "not_comparable",
                     "reasons": ["unit_systems_not_convertible"]}]
        self.repository.snapshot_comparability("map-1", 1, pair_old)
        self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "ambient"})
        self.repository.snapshot_comparability("map-1", 2, pair_new)
        report = self.repository.revision_report("map-1")
        self.assertEqual(len(report["pair_changes"]), 1)
        change = report["pair_changes"][0]
        self.assertEqual(change["from_layer"], "comparable")
        self.assertEqual(change["to_layer"], "not_comparable")
        self.assertEqual(change["to_reasons"], ["unit_systems_not_convertible"])

    def test_second_revision_queues_follow_up_requests(self):
        self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "ambient"})
        self.repository.complete_case_revalidation("map-1", "case-a", {"outcome": "approve"})
        self.repository.complete_case_revalidation("map-1", "case-b", {"outcome": "approve"})
        self.assertEqual(self.repository.pending_revalidation()["open_request_count"], 0)
        self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "room_temp"})
        self.assertEqual(self.repository.pending_revalidation()["by_mapping"],
                         {"map-1": ["case-a", "case-b"]})


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from standards_bridge.verification_hub import Application
from standards_bridge.profiles.specification import ContractError, DomainRecord
from standards_bridge.economics.comparability import COMPARABLE, NOT_COMPARABLE


def cross_market_case(case_id: str, market: str, family: str = "safety") -> DomainRecord:
    return DomainRecord(case_id, {
        "target_market": market, "standard_family": family, "schema_version": "v1",
        "unit_system": "metric", "language_pack": "en", "privacy_tier": 2,
        "safety_threshold": 0.8, "evidence_items": 10, "unmapped_fields": 1,
        "waiver_count": 1, "test_pass_rate": 0.8, "local_partner": "lab"})


class RevisionReuseFlowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.application = Application(
            Path(temporary.name) / "flow.sqlite3",
            context={"comparability_min_bridge_aliases": 2})
        for case_id, market in (("case-a", "my"), ("case-b", "th"), ("case-c", "vn")):
            self.application.repository.save_record(cross_market_case(case_id, market))
        # cross-family mapping bridges the two standard families
        self.application.repository.save_record(DomainRecord(
            "case-d", {"target_market": "sg", "standard_family": "privacy", "unit_system": "metric",
                       "evidence_items": 10, "unmapped_fields": 1, "waiver_count": 1,
                       "test_pass_rate": 0.7}))
        self.application.register_mapping("map-shared", "safety", "privacy",
                                          {"temperature": "ambient_temp", "risk": "hazard"})
        for case_id in ("case-a", "case-b", "case-d"):
            self.application.repository.link_case_mapping(case_id, "map-shared")
        self.application.register_mapping("map-other", "ethics", "ethics-core", {"bias": "fairness"})
        self.application.repository.link_case_mapping("case-c", "map-other")

    def test_baseline_comparison_is_comparable_through_mapping_bridge(self):
        row = self.application.compare_cases("case-a", "case-d")
        self.assertEqual(row["layer"], COMPARABLE)
        view = self.application.comparability_view()
        # pooled mean is reported for transparency but eligibility follows layers
        self.assertIn("pooled_mean_pass_rate", view["stratified_pass_rates"])
        self.assertEqual(view["reuse_eligibility"]["cases"]["case-a"]["status"], "reuse_supported")

    def test_alias_shrinking_revision_moves_comparison_and_blocks_reuse_until_revalidated(self):
        before = self.application.compare_cases("case-a", "case-d")
        self.assertEqual(before["layer"], COMPARABLE)
        # capture the revision-1 comparability baseline for the affected mapping
        baseline_pairs = [row for row in self.application.comparability_view()["reuse_eligibility"]["pairs"]
                          if "case-d" in (row["left"], row["right"])]
        self.application.repository.snapshot_comparability("map-shared", 1, baseline_pairs)

        self.application.repository.sign_case("cert-a", "case-a", "map-shared", {"accepted": True})
        # revision keeps the graph edge but drops below the alias adequacy floor
        self.application.register_mapping("map-shared", "safety", "privacy", {"temperature": "ambient_temp"})

        impact = self.application.mapping_impact("map-shared")
        self.assertEqual(impact["affected_cases"], ["case-a", "case-b", "case-d"])
        # unrelated mapping/case is untouched and never queued for rerun
        self.assertEqual(self.application.mapping_impact("map-other")["open_revalidation_cases"], [])

        after = self.application.compare_cases("case-a", "case-d")
        self.assertEqual(after["layer"], NOT_COMPARABLE)
        self.assertIn("mapping_bridge_alias_coverage_insufficient", after["reasons"])

        # dependent cases are held out of fresh reuse judgements while revalidation is open
        view = self.application.comparability_view()
        self.assertEqual(view["revalidation"]["by_mapping"],
                         {"map-shared": ["case-a", "case-b", "case-d"]})
        for case_id in ("case-a", "case-b", "case-d"):
            self.assertEqual(view["reuse_eligibility"]["cases"][case_id]["status"],
                             "revalidation_pending")
        self.assertNotEqual(view["reuse_eligibility"]["cases"]["case-c"]["status"],
                            "revalidation_pending")

        # snapshot the revision-2 assessment so the report can diff the layers
        new_pairs = [row for row in view["reuse_eligibility"]["pairs"]
                     if "case-d" in (row["left"], row["right"])]
        self.application.repository.snapshot_comparability("map-shared", 2, new_pairs)
        report = self.application.revision_view("map-shared")
        changed = [change for change in report["pair_changes"]
                   if {change["left_case_id"], change["right_case_id"]} == {"case-a", "case-d"}]
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]["from_layer"], COMPARABLE)
        self.assertEqual(changed[0]["to_layer"], NOT_COMPARABLE)

        # old certification keeps revision-1 evidence but is flagged stale
        stale = report["stale_certifications"]
        self.assertEqual([item["certification_id"] for item in stale], ["cert-a"])
        self.assertEqual(stale[0]["mapping_revision"], 1)

    def test_revalidation_refreshes_only_the_submitted_case(self):
        self.application.register_mapping("map-shared", "safety", "privacy", {"temperature": "ambient_temp"})
        with self.assertRaisesRegex(ContractError, "must not be revalidated"):
            self.application.revalidate_case("map-shared", "case-c", {"outcome": "approve"})
        outcome = self.application.revalidate_case("map-shared", "case-b", {"outcome": "approve"})
        self.assertEqual(outcome["closed"]["closed_requests"][0]["status"], "passed")
        self.assertEqual(outcome["refreshed_eligibility"]["status"], "reuse_supported")
        remaining = self.application.revision_view("map-shared")["revalidation"]["open_case_ids"]
        self.assertEqual(sorted(remaining), ["case-a", "case-d"])

    def test_failed_revalidation_marks_case_not_comparable(self):
        self.application.register_mapping("map-shared", "safety", "privacy", {"temperature": "ambient_temp"})
        outcome = self.application.revalidate_case("map-shared", "case-b", {"outcome": "reject"})
        self.assertEqual(outcome["closed"]["closed_requests"][0]["status"], "failed")
        self.assertEqual(outcome["refreshed_eligibility"]["status"], "not_comparable")
        self.assertEqual(outcome["refreshed_eligibility"]["reasons"], ["revalidation_failed"])

    def test_case_with_two_mappings_stays_pending_until_both_revalidated(self):
        # case-b also depends on a second mapping; both must clear before reuse resumes
        self.application.register_mapping("map-extra", "ethics", "ethics-core", {"bias": "fairness"})
        self.application.repository.link_case_mapping("case-b", "map-extra")
        self.application.register_mapping("map-shared", "safety", "privacy", {"temperature": "ambient_temp"})
        self.application.register_mapping("map-extra", "ethics", "ethics-core", {"bias": "equity"})
        outcome = self.application.revalidate_case("map-shared", "case-b", {"outcome": "approve"})
        self.assertEqual(outcome["refreshed_eligibility"]["status"], "revalidation_pending")
        outcome_two = self.application.revalidate_case("map-extra", "case-b", {"outcome": "approve"})
        self.assertEqual(outcome_two["refreshed_eligibility"]["status"], "reuse_supported")

    def test_no_comparability_view_change_when_unrelated_mapping_revised(self):
        self.application.register_mapping("map-other", "ethics", "ethics-core", {"bias": "equity"})
        overview = self.application.repository.pending_revalidation()
        self.assertEqual(overview["by_mapping"], {"map-other": ["case-c"]})
        self.assertEqual(self.application.comparability_view()["reuse_eligibility"]["cases"]["case-a"]["status"],
                         "reuse_supported")


if __name__ == "__main__":
    unittest.main()

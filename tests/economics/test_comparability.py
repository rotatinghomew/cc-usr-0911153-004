from __future__ import annotations

import unittest

from standards_bridge.profiles.specification import DomainRecord
from standards_bridge.economics.comparability import (
    COMPARABLE,
    INSUFFICIENT_EVIDENCE,
    NOT_COMPARABLE,
    assess_pair,
    build_mapping_graph,
    reuse_eligibility,
    stratified_pass_rates,
    units_are_compatible,
    waiver_rate,
)


def case(record_id: str, **overrides) -> DomainRecord:
    payload = {"target_market": "my", "standard_family": "safety", "schema_version": "v1",
               "unit_system": "metric", "language_pack": "ms", "privacy_tier": 2,
               "safety_threshold": 0.8, "evidence_items": 10, "unmapped_fields": 1,
               "waiver_count": 1, "test_pass_rate": 0.9, "local_partner": "lab"}
    payload.update(overrides)
    return DomainRecord(record_id, payload)


class ComparabilityAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.graph = build_mapping_graph([
            {"source_standard": "safety", "target_standard": "safety-core"},
            {"source_standard": "privacy", "target_standard": "safety-core"},
        ])

    def test_matching_units_and_caliber_are_comparable(self):
        row = assess_pair(case("a"), case("b", target_market="th"), self.graph)
        self.assertEqual(row["layer"], COMPARABLE)
        self.assertEqual(row["reasons"], [])

    def test_known_unit_conversion_stays_comparable(self):
        left = case("a", unit_system="celsius")
        right = case("b", unit_system="fahrenheit", target_market="th")
        self.assertTrue(units_are_compatible(left, right))
        self.assertEqual(assess_pair(left, right, self.graph)["layer"], COMPARABLE)

    def test_unregistered_unit_system_is_not_comparable(self):
        left = case("a", unit_system="metric")
        right = case("b", unit_system="cubits", target_market="th")
        row = assess_pair(left, right, self.graph)
        self.assertEqual(row["layer"], NOT_COMPARABLE)
        self.assertIn("unit_systems_not_convertible", row["reasons"])

    def test_waiver_caliber_divergence_blocks_comparison(self):
        left = case("a", waiver_count=1)
        right = case("b", waiver_count=8, target_market="th")
        row = assess_pair(left, right, self.graph, {"waiver_rate_tolerance": 0.1})
        self.assertEqual(row["layer"], NOT_COMPARABLE)
        self.assertIn("waiver_caliber_diverges", row["reasons"])

    def test_families_without_mapping_path_are_not_comparable(self):
        graph = build_mapping_graph([{"source_standard": "safety", "target_standard": "safety-core"}])
        left = case("a", standard_family="safety")
        right = case("b", standard_family="privacy", target_market="th")
        row = assess_pair(left, right, graph)
        self.assertEqual(row["layer"], NOT_COMPARABLE)
        self.assertIn("no_mapping_path_between_standard_families", row["reasons"])

    def test_transitive_mapping_path_keeps_families_comparable(self):
        left = case("a", standard_family="safety")
        right = case("b", standard_family="privacy", target_market="th")
        self.assertEqual(assess_pair(left, right, self.graph)["layer"], COMPARABLE)

    def test_missing_evidence_routes_to_insufficient_layer(self):
        weak = case("b", evidence_items=0, test_pass_rate=None, target_market="th")
        row = assess_pair(case("a"), weak, self.graph)
        self.assertEqual(row["layer"], INSUFFICIENT_EVIDENCE)
        self.assertIn("test_pass_rate_missing", row["reasons"])
        self.assertIn("evidence_items_below_floor", row["reasons"])

    def test_waiver_rate_is_normalized_by_evidence(self):
        self.assertAlmostEqual(waiver_rate(case("a", waiver_count=2, evidence_items=10)), 0.2)


class StratifiedPassRateTests(unittest.TestCase):
    def setUp(self):
        self.graph = build_mapping_graph([
            {"source_standard": "safety", "target_standard": "safety-core"},
        ])

    def test_pass_rates_are_only_averaged_inside_comparable_cohort(self):
        records = [
            case("a", unit_system="metric", test_pass_rate=0.8),
            case("b", unit_system="metric", test_pass_rate=0.6, target_market="th"),
            case("c", unit_system="cubits", test_pass_rate=0.2, target_market="vn"),
        ]
        view = stratified_pass_rates(records, self.graph)
        self.assertEqual(view["layers"][COMPARABLE]["case_ids"], ["a", "b"])
        self.assertAlmostEqual(view["layers"][COMPARABLE]["mean_pass_rate"], 0.7)
        self.assertEqual(view["layers"][NOT_COMPARABLE]["case_ids"], ["c"])
        self.assertAlmostEqual(view["layers"][NOT_COMPARABLE]["mean_pass_rate"], 0.2)
        self.assertAlmostEqual(view["pooled_mean_pass_rate"], (0.8 + 0.6 + 0.2) / 3)

    def test_insufficient_evidence_cases_are_excluded_from_hard_layers(self):
        records = [case("a"), case("b", evidence_items=0, test_pass_rate=None, target_market="th")]
        view = stratified_pass_rates(records, self.graph)
        # both cases lack any verified comparable partner, so neither is hard-blocked
        self.assertEqual(sorted(view["layers"][INSUFFICIENT_EVIDENCE]["case_ids"]), ["a", "b"])
        self.assertEqual(view["layers"][NOT_COMPARABLE]["case_ids"], [])

    def test_fully_evidenced_case_with_only_hard_blocks_is_not_comparable(self):
        records = [case("a"), case("b", unit_system="cubits", target_market="th")]
        view = stratified_pass_rates(records, self.graph)
        self.assertEqual(sorted(view["layers"][NOT_COMPARABLE]["case_ids"]), ["a", "b"])
        self.assertEqual(view["layers"][INSUFFICIENT_EVIDENCE]["case_ids"], [])

    def test_empty_portfolio_reports_empty_layers(self):
        view = stratified_pass_rates([], self.graph)
        self.assertEqual({layer: view["layers"][layer]["case_count"] for layer in view["layers"]},
                         {COMPARABLE: 0, NOT_COMPARABLE: 0, INSUFFICIENT_EVIDENCE: 0})


class ReuseEligibilityTests(unittest.TestCase):
    def setUp(self):
        self.graph = build_mapping_graph([
            {"source_standard": "safety", "target_standard": "safety-core"},
        ])

    def test_supported_only_when_comparable_partner_exists(self):
        records = [case("a"), case("b", target_market="th"),
                   case("c", unit_system="cubits", target_market="vn")]
        result = reuse_eligibility(records, self.graph)
        self.assertEqual(result["cases"]["a"]["status"], "reuse_supported")
        self.assertEqual(result["cases"]["b"]["status"], "reuse_supported")
        self.assertEqual(result["cases"]["c"]["status"], "not_comparable")
        self.assertEqual(result["cases"]["a"]["comparable_partners"], ["b"])

    def test_blocked_cases_report_revalidation_pending(self):
        records = [case("a"), case("b", target_market="th")]
        result = reuse_eligibility(records, self.graph, blocked_case_ids={"b"})
        self.assertEqual(result["cases"]["b"]["status"], "revalidation_pending")
        self.assertEqual(result["counts"]["revalidation_pending"], 1)

    def test_singleton_portfolio_is_insufficient_evidence(self):
        result = reuse_eligibility([case("a")], self.graph)
        self.assertEqual(result["cases"]["a"]["status"], "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from standards_bridge.profiles.specification import DomainRecord
from standards_bridge.mappings.semantic_bridge import conformance_profile, convert_unit, map_field, reuse_matrix


class SemanticBridgeTests(unittest.TestCase):
    def record(self, key, market="my"):
        return DomainRecord(key, {"target_market": market, "standard_family": "safety", "schema_version": "2",
            "unit_system": "metric", "language_pack": "ms", "privacy_tier": 2, "safety_threshold": .8,
            "evidence_items": 10, "unmapped_fields": 1, "waiver_count": 1, "test_pass_rate": .9, "local_partner": "lab"})

    def test_unit_and_alias_mapping(self):
        self.assertAlmostEqual(convert_unit(0, "celsius", "fahrenheit"), 32.0)
        self.assertFalse(map_field("patient_id", "subject_id", "x", {"patient_id": "subject_id"}).lossy)

    def test_profiles_and_reuse(self):
        profile = conformance_profile(self.record("a"))
        self.assertGreater(profile["mapping_coverage"], profile["semantic_loss"])
        self.assertEqual(reuse_matrix([self.record("a"), self.record("b", "th")])["market_count"], 2.0)

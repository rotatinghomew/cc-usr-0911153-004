from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from standards_bridge.assurance.case_ledger import Repository
from standards_bridge.profiles.specification import ContractError, DomainRecord


class CertificationRegisterTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.database = Path(temporary.name) / "standards.sqlite3"
        self.repository = Repository(self.database)
        for case_id in ("case-a", "case-b", "case-c"):
            self.repository.save_record(DomainRecord(case_id, {"target_market": "market-1"}))

    def test_shared_mapping_revision_marks_only_dependent_cases(self):
        self.assertEqual(self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "temp"}), 1)
        self.repository.register_mapping("map-2", "spec-c", "spec-d", {"weight": "mass"})
        self.repository.link_case_mapping("case-a", "map-1")
        self.repository.link_case_mapping("case-b", "map-1")
        self.repository.link_case_mapping("case-c", "map-2")
        first = self.repository.sign_case("cert-a", "case-a", "map-1", {"accepted": True})
        self.assertEqual(first["mapping_revision"], 1)
        self.assertEqual(self.repository.register_mapping("map-1", "spec-a", "spec-b", {"temperature": "ambient"}), 2)
        affected = Repository(self.database).mapping_impact("map-1")
        self.assertEqual(affected["affected_cases"], ["case-a", "case-b"])
        self.assertEqual(affected["signed_certifications"][0]["mapping_revision"], 1)
        self.assertEqual(self.repository.mapping_impact("map-2")["affected_cases"], ["case-c"])
        with self.assertRaisesRegex(ContractError, "cannot be overwritten"):
            self.repository.sign_case("cert-a", "case-a", "map-1", {"accepted": True})

    def test_unknown_mapping_or_case_does_not_create_dependency(self):
        with self.assertRaisesRegex(ContractError, "unknown mapping"):
            self.repository.link_case_mapping("case-a", "missing")
        self.repository.register_mapping("map-1", "spec-a", "spec-b", {})
        with self.assertRaisesRegex(ContractError, "unknown case"):
            self.repository.link_case_mapping("missing", "map-1")

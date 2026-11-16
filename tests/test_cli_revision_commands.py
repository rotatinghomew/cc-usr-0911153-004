from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from standards_bridge.cli import main
from standards_bridge.profiles.specification import DomainRecord


class CliRevisionCommandsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.database = str(Path(temporary.name) / "cli.sqlite3")
        self.application_db = self.database
        from standards_bridge.verification_hub import Application
        self.application = Application(self.database)
        for case_id in ("case-a", "case-b"):
            self.application.repository.save_record(DomainRecord(
                case_id, {"target_market": "my", "standard_family": "safety",
                          "unit_system": "metric", "evidence_items": 10,
                          "unmapped_fields": 1, "waiver_count": 1, "test_pass_rate": 0.8}))
        self.application.register_mapping("map-1", "safety", "safety-core", {"a": "alpha"})
        self.application.repository.link_case_mapping("case-a", "map-1")
        self.application.repository.link_case_mapping("case-b", "map-1")

    def _run(self, *argv: str) -> dict:
        import io
        import contextlib
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = main(list(argv))
        self.assertEqual(code, 0)
        return json.loads(buffer.getvalue())

    def test_compare_and_comparability_commands(self):
        row = self._run("compare", "--database", self.database,
                        "--left", "case-a", "--right", "case-b")
        self.assertEqual(row["layer"], "comparable")
        view = self._run("comparability", "--database", self.database)
        self.assertIn("stratified_pass_rates", view)
        self.assertEqual(view["revalidation"]["open_request_count"], 0)

    def test_mapping_revision_revision_and_revalidate_commands(self):
        impact = self._run("mapping", "impact", "--database", self.database, "--mapping-id", "map-1")
        self.assertEqual(impact["affected_cases"], ["case-a", "case-b"])
        registered = self._run("mapping", "register", "--database", self.database,
                               "--mapping-id", "map-1", "--source", "safety",
                               "--target", "safety-core", "--aliases", '{"a": "alpha", "b": "beta"}')
        self.assertEqual(registered["revision"], 2)
        report = self._run("revision", "--database", self.database, "--mapping-id", "map-1")
        self.assertEqual(report["revalidation"]["open_case_ids"], ["case-a", "case-b"])
        outcome = self._run("revalidate", "--database", self.database, "--mapping-id", "map-1",
                            "--case-id", "case-a", "--result", '{"outcome": "approve"}')
        self.assertEqual(outcome["closed"]["closed_requests"][0]["status"], "passed")
        remaining = self._run("revision", "--database", self.database, "--mapping-id", "map-1")
        self.assertEqual(remaining["revalidation"]["open_case_ids"], ["case-b"])

    def test_sign_case_command_blocks_while_revalidation_open(self):
        self._run("mapping", "register", "--database", self.database, "--mapping-id", "map-1",
                  "--source", "safety", "--target", "safety-core", "--aliases", '{"a": "changed"}')
        with self.assertRaises(Exception):
            self._run("sign-case", "--database", self.database, "--certification-id", "cert-1",
                      "--case-id", "case-a", "--mapping-id", "map-1", "--evidence", '{"ok": true}')


if __name__ == "__main__":
    unittest.main()

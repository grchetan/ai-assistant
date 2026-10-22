"""
================================================================================
                    UNIT TESTS: SECURITY & DEVOPS
================================================================================
Verifies Intrusion Detection heuristics, File Integrity baselines,
Static Code Complexity auditing, and SQL schema introspection.
================================================================================
"""

import sys
import os
import unittest
import tempfile
from pathlib import Path

# Ensure root workspace is in sys.path
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from jarvis.security.intrusion_detector import get_intrusion_detector
from jarvis.security.file_integrity_watcher import get_file_integrity_watcher
from jarvis.security.packet_analyzer import get_packet_analyzer
from jarvis.security.wifi_security_auditor import get_wifi_auditor

from jarvis.devops.code_linter_fixer import get_code_auditor
from jarvis.devops.sql_studio import get_sql_studio


class TestSecurityAndDevOps(unittest.TestCase):
    """Unit tests for Cybersecurity and DevOps subsystems."""

    def test_intrusion_detector(self):
        ids = get_intrusion_detector()
        report = ids.get_security_report()
        self.assertIn("status", report)
        self.assertIn(report["status"], ["SECURE", "THREATS_DETECTED"])

    def test_file_integrity_watcher(self):
        fim = get_file_integrity_watcher()
        violations = fim.check_integrity()
        self.assertIsInstance(violations, list)

    def test_packet_analyzer_throughput(self):
        analyzer = get_packet_analyzer()
        speed = analyzer.get_instantaneous_throughput()
        self.assertIn("download_kbps", speed)
        self.assertIn("upload_kbps", speed)

    def test_code_linter_auditor(self):
        auditor = get_code_auditor()
        # Audit a real file from the workspace
        audit_res = auditor.audit_file("main.py")
        self.assertEqual(audit_res["status"], "PASSED")
        self.assertTrue(audit_res["total_functions"] >= 1)

    def test_sql_studio_schema(self):
        studio = get_sql_studio()
        # Check against existing memory DB
        db_path = str(WORKSPACE_DIR / "jarvis" / "data" / "memory.db")
        if os.path.exists(db_path):
            schema = studio.get_table_schema(db_path, "user_facts")
            self.assertIsInstance(schema, list)


if __name__ == "__main__":
    unittest.main()


import unittest

from src.evidence import get_finding_sources
from src.data_loader import load_incidents


class TestFindingSources(unittest.TestCase):

    def setUp(self):
        self.incidents = load_incidents()

    def test_retrieve_finding_and_source(self):
        result = get_finding_sources(
            self.incidents, "TEST-001", "FIND-001"
        )

        self.assertIsNotNone(result)
        self.assertEqual(
            result["finding"]["finding_id"], "FIND-001"
        )
        self.assertEqual(len(result["sources"]), 1)
        self.assertEqual(
            result["sources"][0]["source_id"], "SRC-001"
        )

    def test_unknown_finding_returns_none(self):
        result = get_finding_sources(
            self.incidents, "TEST-001", "FIND-999"
        )
        self.assertIsNone(result)

    def test_unknown_incident_returns_none(self):
        result = get_finding_sources(
            self.incidents, "TEST-999", "FIND-001"
        )
        self.assertIsNone(result)
   
    def test_format_evidence_report(self):
        from src.evidence import format_evidence_report

        result = get_finding_sources(
            self.incidents, "TEST-001", "FIND-001"
        )
        report = format_evidence_report(result)

        self.assertIn("FIND-001", report)
        self.assertIn("Unverified", report)
        self.assertIn("Fictional Test Report A", report)

    def test_format_missing_finding(self):
        from src.evidence import format_evidence_report

        report = format_evidence_report(None)

        self.assertEqual(report, "Finding or incident not found.")

    def test_format_report_without_sources(self):
        from src.evidence import format_evidence_report

        result = {
            "finding": {
                "finding_id": "FIND-003",
                "claim": "A test claim.",
                "evidence_status": "insufficient_evidence",
                "source_ids": [],
            },
            "sources": [],
        }

        report = format_evidence_report(result)

        self.assertIn("No associated sources found.", report)
        self.assertIn("Insufficient Evidence", report)


    if __name__ == "__main__":
         unittest.main()


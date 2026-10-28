import unittest

from src.evidence import (
get_finding_sources,
format_evidence_report,
analyze_evidence_quality,
)
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
    result = get_finding_sources(
        self.incidents, "TEST-001", "FIND-001"
    )
    report = format_evidence_report(result)

    self.assertIn("FIND-001", report)
    self.assertIn("Unverified", report)
    self.assertIn("Fictional Test Report A", report)

 def test_format_missing_finding(self):
    report = format_evidence_report(None)

    self.assertEqual(
        report, "Finding or incident not found."
    )

 def test_format_report_without_sources(self):
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
    self.assertIn("Linked Sources: 0", report)
    self.assertIn("Distinct Publishers: 0", report)

 def test_evidence_quality_with_multiple_publishers(self):
    result = {
        "sources": [
            {"publisher": "Microsoft"},
            {"publisher": "CERT-In"},
            {"publisher": "Microsoft"},
        ]
    }

    analysis = analyze_evidence_quality(result)

    self.assertEqual(analysis["source_count"], 3)
    self.assertEqual(analysis["publisher_count"], 2)
    self.assertEqual(
        analysis["assessment"],
        "Multiple sources and publishers represented",
    )

 def test_evidence_quality_with_one_source(self):
    result = {
        "sources": [
            {"publisher": "Microsoft"},
        ]
    }

    analysis = analyze_evidence_quality(result)

    self.assertEqual(analysis["source_count"], 1)
    self.assertEqual(analysis["publisher_count"], 1)
    self.assertEqual(
        analysis["assessment"],
        "Limited source coverage: only one source linked",
    )

 def test_evidence_quality_with_no_sources(self):
    result = {"sources": []}

    analysis = analyze_evidence_quality(result)

    self.assertEqual(analysis["source_count"], 0)
    self.assertEqual(analysis["publisher_count"], 0)
    self.assertEqual(
        analysis["assessment"],
        "No linked sources available",
    )

 def test_evidence_quality_with_missing_result(self):
    self.assertIsNone(analyze_evidence_quality(None))

 def test_report_includes_evidence_quality_analysis(self):
    result = {
        "incident": {
            "name": "Test Incident",
            "incident_id": "TEST-001",
        },
        "finding": {
            "finding_id": "TEST-F001",
            "claim": "A test claim",
            "evidence_status": "supported",
        },
        "sources": [
            {
                "source_id": "SRC-001",
                "title": "Source One",
                "publisher": "Publisher A",
                "url": "https://example.com/one",
            },
            {
                "source_id": "SRC-002",
                "title": "Source Two",
                "publisher": "Publisher B",
                "url": "https://example.com/two",
            },
        ],
    }

    report = format_evidence_report(result)

    self.assertIn("Evidence Quality Analysis:", report)
    self.assertIn("Linked Sources: 2", report)
    self.assertIn("Distinct Publishers: 2", report)
    self.assertIn(
        "Multiple sources and publishers represented",
        report,
    )


if __name__ == "__main__":
    unittest.main()

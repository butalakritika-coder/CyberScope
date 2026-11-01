
import unittest

from src.evidence import (
    get_finding_sources,
    format_evidence_report,
    analyze_evidence_quality,
    get_incident_techniques,
    compare_incident_techniques,
    format_technique_comparison,
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
        self.assertIn("Evidence Level:", report)
        self.assertIn("Further Review Needed:", report)

    def test_evidence_quality_flags_missing_sources(self):
        result = {"sources": []}

        analysis = analyze_evidence_quality(result)

        self.assertEqual(
            analysis["evidence_level"],
            "No Evidence Linked",
        )
        self.assertTrue(analysis["needs_review"])

    def test_evidence_quality_flags_limited_coverage(self):
        result = {
            "sources": [
                {"publisher": "Microsoft"},
            ]
        }

        analysis = analyze_evidence_quality(result)

        self.assertEqual(
            analysis["evidence_level"],
            "Limited",
        )
        self.assertTrue(analysis["needs_review"])


class TestIncidentTechniqueComparison(unittest.TestCase):

    def test_get_incident_techniques(self):
        incidents = load_incidents()

        techniques = get_incident_techniques(
            incidents, "INC-2017-WANNACRY"
        )

        self.assertEqual(len(techniques), 3)
        self.assertEqual(
            techniques[0]["technique_id"], "T1210"
        )

    def test_get_incident_techniques_for_unknown_incident(self):
        result = get_incident_techniques(
            [], "UNKNOWN-001"
        )

        self.assertIsNone(result)

    def test_get_incident_techniques_when_none_exist(self):
        incidents = [
            {
                "incident_id": "TEST-002",
                "techniques": [],
            }
        ]

        result = get_incident_techniques(
            incidents, "TEST-002"
        )

        self.assertEqual(result, [])

    def test_compare_incident_techniques(self):
        incidents = [
            {
                "incident_id": "INC-001",
                "techniques": [
                    {"technique_id": "T1210"},
                    {"technique_id": "T1486"},
                    {"technique_id": "T1570"},
                ],
            },
            {
                "incident_id": "INC-002",
                "techniques": [
                    {"technique_id": "T1486"},
                    {"technique_id": "T1059"},
                ],
            },
        ]

        result = compare_incident_techniques(
            incidents, "INC-001", "INC-002"
        )

        self.assertEqual(
            result["common_techniques"], {"T1486"}
        )
        self.assertEqual(
            result["unique_to_first"], {"T1210", "T1570"}
        )
        self.assertEqual(
            result["unique_to_second"], {"T1059"}
        )

    def test_compare_incident_with_unknown_id(self):
        incidents = [
            {
                "incident_id": "INC-001",
                "techniques": [
                    {"technique_id": "T1486"}
                ],
            }
        ]

        result = compare_incident_techniques(
            incidents, "INC-001", "UNKNOWN-001"
        )

        self.assertIsNone(result)

    def test_format_technique_comparison(self):
        incidents = [
            {
                "incident_id": "INC-001",
                "techniques": [
                    {
                        "technique_id": "T1486",
                        "name": "Data Encrypted for Impact",
                    },
                    {
                        "technique_id": "T1210",
                        "name": "Exploitation of Remote Services",
                    },
                ],
            },
            {
                "incident_id": "INC-002",
                "techniques": [
                    {
                        "technique_id": "T1486",
                        "name": "Data Encrypted for Impact",
                    },
                    {
                        "technique_id": "T1059",
                        "name": "Command and Scripting Interpreter",
                    },
                ],
            },
        ]

        report = format_technique_comparison(
            incidents, "INC-001", "INC-002"
        )

        self.assertIn("Common Techniques:", report)
        self.assertIn(
            "T1486 - Data Encrypted for Impact", report
        )
        self.assertIn("Unique to First Incident:", report)
        self.assertIn(
            "T1210 - Exploitation of Remote Services", report
        )
        self.assertIn("Unique to Second Incident:", report)
        self.assertIn(
            "T1059 - Command and Scripting Interpreter", report
        )

    def test_format_technique_comparison_invalid_incident(self):
        report = format_technique_comparison(
            [], "INC-001", "INC-002"
        )

        self.assertEqual(
            report, "One or both incidents not found."
        )


if __name__ == "__main__":
    unittest.main()

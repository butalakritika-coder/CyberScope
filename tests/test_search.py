
import unittest

from src.search import search_incidents


class TestSearchIncidents(unittest.TestCase):

    def setUp(self):
        """Prepare fictional incidents for each test."""
        self.incidents = [
       {
    "incident_id": "TEST-001",
    "name": "Example Ransomware Incident",
    "category": "Ransomware",
    "summary": "A fictional incident involving encrypted files.",
    "techniques": [
        {
            "technique_id": "T_TEST",
            "name": "Example Technique",
        }
    ],
},
            {
    "incident_id": "TEST-002",
    "name": "Example Email Incident",
    "category": "Phishing",
    "summary": "A fictional incident involving deceptive emails.",
    "techniques": [],
},
        ]

    def test_search_by_name(self):
        results = search_incidents(self.incidents, "Ransomware")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["incident_id"], "TEST-001")

    def test_search_is_case_insensitive(self):
        results = search_incidents(self.incidents, "rAnSoMwArE")
        self.assertEqual(len(results), 1)

    def test_search_by_category(self):
        results = search_incidents(
            self.incidents, "Phishing", fields=["category"]
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["incident_id"], "TEST-002")

    def test_search_by_summary(self):
        results = search_incidents(
            self.incidents, "encrypted files", fields=["summary"]
        )
        self.assertEqual(results[0]["incident_id"], "TEST-001")

    def test_search_by_technique(self):
        results = search_incidents(
            self.incidents, "Example Technique", fields=["techniques"]
        )
        self.assertEqual(results[0]["incident_id"], "TEST-001")

    def test_empty_query_returns_no_results(self):
        self.assertEqual(search_incidents(self.incidents, "   "), [])

    def test_unmatched_query_returns_no_results(self):
        self.assertEqual(
            search_incidents(self.incidents, "nonexistent"), []
        )

    def test_search_specific_field(self):
        # "Phishing" is in the category, not the name.
        results = search_incidents(
            self.incidents, "Phishing", fields=["name"]
        )
        self.assertEqual(results, [])

    def test_unsupported_field_raises_error(self):
        with self.assertRaises(ValueError):
            search_incidents(
                self.incidents, "test", fields=["passwords"]
            )


if __name__ == "__main__":
    unittest.main()


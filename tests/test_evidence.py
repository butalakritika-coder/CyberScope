
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


if __name__ == "__main__":
    unittest.main()


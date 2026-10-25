
import unittest

from src.data_loader import load_incidents, validate_incidents


class TestValidateIncidents(unittest.TestCase):

    def setUp(self):
        """Create a small valid dataset for testing."""
        self.valid_incident = {
            "incident_id": "TEST-001",
            "name": "Test Incident",
            "category": "Ransomware",
            "summary": "A fictional incident used for testing.",
            "findings": [
                {
                    "finding_id": "FIND-001",
                    "claim": "A fictional claim for testing.",
                    "evidence_status": "unverified",
                    "source_ids": ["SRC-001"],
                }
            ],
            "techniques": [],
            "sources": [
                {
                    "source_id": "SRC-001",
                    "title": "Test Source",
                    "publisher": "Test Publisher",
                    "url": None,
                    "published_date": None,
                    "source_type": "synthetic_test_data",
                }
            ],
        }

    def test_valid_incident_passes(self):
        errors = validate_incidents([self.valid_incident])
        self.assertEqual(errors, [])

    def test_missing_required_field_is_detected(self):
        incident = self.valid_incident.copy()
        del incident["name"]

        errors = validate_incidents([incident])

        self.assertTrue(any("missing 'name'" in error for error in errors))

    def test_duplicate_incident_id_is_detected(self):
        second_incident = self.valid_incident.copy()

        errors = validate_incidents([
            self.valid_incident,
            second_incident,
        ])

        self.assertTrue(
            any("Duplicate incident_id" in error for error in errors)
        )

    def test_duplicate_finding_id_is_detected(self):
        incident = self.valid_incident.copy()
        incident["findings"] = [
            {
                "finding_id": "FIND-001",
                "claim": "First fictional claim.",
                "evidence_status": "unverified",
                "source_ids": ["SRC-001"],
            },
            {
                "finding_id": "FIND-001",
                "claim": "Second fictional claim.",
                "evidence_status": "unverified",
                "source_ids": ["SRC-001"],
            },
        ]

        errors = validate_incidents([incident])

        self.assertTrue(
            any("Duplicate finding_id" in error for error in errors)
        )

    def test_unknown_source_reference_is_detected(self):
        incident = self.valid_incident.copy()
        incident["findings"] = [
            {
                "finding_id": "FIND-001",
                "claim": "A fictional claim.",
                "evidence_status": "unverified",
                "source_ids": ["SRC-999"],
            }
        ]

        errors = validate_incidents([incident])

        self.assertTrue(
            any("unknown source: SRC-999" in error for error in errors)
        )

    def test_invalid_evidence_status_is_detected(self):
        incident = self.valid_incident.copy()
        incident["findings"] = [
            {
                "finding_id": "FIND-001",
                "claim": "A fictional claim.",
                "evidence_status": "probably_true",
                "source_ids": ["SRC-001"],
            }
        ]

        errors = validate_incidents([incident])

        self.assertTrue(
            any("invalid evidence_status" in error for error in errors)
        )

    def test_load_incidents_reads_dataset(self):
        incidents = load_incidents()

        self.assertIsInstance(incidents, list)
        self.assertGreater(len(incidents), 0)


    def test_technique_with_unknown_source(self):
        incidents = [
            {
                "incident_id": "TEST-TECH",
                "name": "Test Incident",
                "category": "Ransomware",
                "summary": "A fictional test incident.",
                "findings": [],
                "techniques": [
                    {
                        "technique_id": "T1234",
                        "name": "Example Technique",
                        "source_ids": ["SRC-999"],
                    }
                ],
                "sources": [],
            }
        ]

        errors = validate_incidents(incidents)

        self.assertTrue(
            any("references unknown source: SRC-999" in error
                for error in errors)
        )


if __name__ == "__main__":
    unittest.main()


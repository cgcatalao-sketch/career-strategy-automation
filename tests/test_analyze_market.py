import csv
import tempfile
import unittest
from pathlib import Path

from src.analyze_market import analyse, read_discovered_opportunities, read_snapshot


class MarketAnalysisTests(unittest.TestCase):
    def test_aggregate_counts_are_reproducible(self):
        vacancies = [
            {
                "record_id": "V001",
                "company": "Example A",
                "job_title": "Executive Assistant",
                "location": "Europe",
                "work_model": "Remote",
                "role_family": "P1",
                "recurring_keywords": "communication, stakeholder management",
            },
            {
                "record_id": "V002",
                "company": "Example B",
                "job_title": "Operations Coordinator",
                "location": "Netherlands",
                "work_model": "Hybrid",
                "role_family": "P2",
                "recurring_keywords": "communication, process improvement",
            },
        ]
        capabilities = [
            {"search_term": "communication", "capability": "Communication"},
            {"search_term": "stakeholder", "capability": "Stakeholder management"},
        ]
        evidence = [
            {"record_id": "V001", "communication": "1", "stakeholder": "1"},
            {"record_id": "V002", "communication": "1", "stakeholder": "0"},
        ]
        result = analyse(vacancies, evidence, capabilities)
        self.assertEqual(result["sample_size"], 2)
        self.assertEqual(result["remote_count"], 1)
        self.assertEqual(result["capabilities"][0]["count"], 2)

    def test_private_columns_are_rejected(self):
        headers = [
            "record_id", "company", "job_title", "location", "work_model",
            "role_family", "recurring_keywords", "personal_assessment",
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsafe.csv"
            with path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=headers)
                writer.writeheader()
            with self.assertRaisesRegex(ValueError, "Privacy schema check failed"):
                read_snapshot(path)

    def test_private_application_status_is_rejected_from_public_log(self):
        headers = [
            "opportunity_id", "discovered_on", "company", "job_title",
            "department", "locations", "work_model", "match_level",
            "recommendation", "discovery_source", "public_job_url",
            "match_evidence", "application_status",
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsafe_opportunities.csv"
            with path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=headers)
                writer.writeheader()
            with self.assertRaisesRegex(ValueError, "Opportunity schema check failed"):
                read_discovered_opportunities(path)


if __name__ == "__main__":
    unittest.main()

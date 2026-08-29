import json
import tempfile
import unittest
from pathlib import Path

from src.analyze_jobs import analyse, score_job


PROFILE = {
    "target_roles": ["executive assistant"],
    "priority_keywords": ["documentation", "automation"],
    "preferred_work_modes": ["remote"],
    "preferred_regions": ["emea"],
    "weights": {
        "target_role": 35,
        "keyword_coverage": 45,
        "work_mode": 15,
        "region": 5,
    },
}


class JobAnalysisTests(unittest.TestCase):
    def test_complete_match_scores_100(self):
        job = {
            "job_id": "T1",
            "company": "Example",
            "role": "Executive Assistant",
            "region": "EMEA",
            "work_mode": "Remote",
            "description": "Documentation and automation",
        }
        result = score_job(job, PROFILE)
        self.assertEqual(result["fit_score"], 100.0)

    def test_results_are_ranked_highest_first(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "profile.json").write_text(json.dumps(PROFILE), encoding="utf-8")
            (root / "jobs.csv").write_text(
                "job_id,company,role,region,work_mode,description\n"
                "1,Low,Other,Other,On-site,General support\n"
                "2,High,Executive Assistant,EMEA,Remote,Documentation and automation\n",
                encoding="utf-8",
            )
            results = analyse(root / "jobs.csv", root / "profile.json")
        self.assertEqual(results[0]["company"], "High")
        self.assertGreater(results[0]["fit_score"], results[1]["fit_score"])


if __name__ == "__main__":
    unittest.main()

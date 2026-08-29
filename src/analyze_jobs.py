"""Score job opportunities against transparent career-strategy criteria."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def normalise(value: str) -> str:
    """Return lowercase, whitespace-normalised text for comparison."""
    return " ".join(value.lower().split())


def contains_any(text: str, options: list[str]) -> bool:
    normalised_text = normalise(text)
    return any(normalise(option) in normalised_text for option in options)


def score_job(job: dict[str, str], profile: dict[str, Any]) -> dict[str, Any]:
    """Calculate a 0-100 fit score and preserve the evidence behind it."""
    weights = profile["weights"]
    role_match = contains_any(job["role"], profile["target_roles"])
    work_mode_match = normalise(job["work_mode"]) in {
        normalise(item) for item in profile["preferred_work_modes"]
    }
    region_match = normalise(job["region"]) in {
        normalise(item) for item in profile["preferred_regions"]
    }

    searchable_text = f'{job["role"]} {job["description"]}'
    matched_keywords = [
        keyword
        for keyword in profile["priority_keywords"]
        if normalise(keyword) in normalise(searchable_text)
    ]
    keyword_ratio = len(matched_keywords) / len(profile["priority_keywords"])

    score = (
        weights["target_role"] * int(role_match)
        + weights["keyword_coverage"] * keyword_ratio
        + weights["work_mode"] * int(work_mode_match)
        + weights["region"] * int(region_match)
    )

    return {
        **job,
        "fit_score": round(score, 1),
        "matched_keywords": "; ".join(matched_keywords),
        "role_match": role_match,
        "work_mode_match": work_mode_match,
        "region_match": region_match,
    }


def analyse(input_path: Path, profile_path: Path) -> list[dict[str, Any]]:
    with profile_path.open(encoding="utf-8") as profile_file:
        profile = json.load(profile_file)
    with input_path.open(encoding="utf-8", newline="") as input_file:
        jobs = list(csv.DictReader(input_file))
    return sorted(
        (score_job(job, profile) for job in jobs),
        key=lambda item: (-item["fit_score"], item["company"], item["role"]),
    )


def write_ranked_jobs(results: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "job_id", "company", "role", "region", "work_mode", "fit_score",
        "matched_keywords", "role_match", "work_mode_match", "region_match",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


def write_actions(results: list[dict[str, Any]], output_path: Path) -> None:
    top_jobs = results[:3]
    lines = [
        "# Priority actions",
        "",
        "Generated from the highest-scoring opportunities in the sample dataset.",
        "",
    ]
    for index, job in enumerate(top_jobs, start=1):
        evidence = job["matched_keywords"] or "no priority keywords"
        lines.extend([
            f'## {index}. Review {job["role"]} at {job["company"]}',
            "",
            f'- Fit score: **{job["fit_score"]}/100**',
            f'- Evidence: {evidence}',
            "- Next step: validate requirements and tailor application evidence.",
            "",
        ])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/sample_jobs.csv"))
    parser.add_argument("--profile", type=Path, default=Path("config/profile.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = analyse(args.input, args.profile)
    write_ranked_jobs(results, args.output_dir / "ranked_jobs.csv")
    write_actions(results, args.output_dir / "priority_actions.md")
    print(f"Analysed {len(results)} jobs. Outputs written to {args.output_dir}.")


if __name__ == "__main__":
    main()

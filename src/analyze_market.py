"""Generate aggregate market intelligence from a sanitised vacancy snapshot."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


PUBLIC_FIELDS = {
    "record_id",
    "company",
    "job_title",
    "location",
    "work_model",
    "role_family",
    "recurring_keywords",
}

OPPORTUNITY_FIELDS = {
    "opportunity_id",
    "discovered_on",
    "company",
    "job_title",
    "department",
    "locations",
    "work_model",
    "match_level",
    "recommendation",
    "discovery_source",
    "public_job_url",
    "match_evidence",
}


def normalise(value: str) -> str:
    return " ".join(value.casefold().split())


def read_snapshot(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        fields = set(reader.fieldnames or [])
        if fields != PUBLIC_FIELDS:
            unexpected = sorted(fields - PUBLIC_FIELDS)
            missing = sorted(PUBLIC_FIELDS - fields)
            raise ValueError(
                f"Privacy schema check failed. Unexpected={unexpected}; missing={missing}"
            )
        return list(reader)


def read_keyword_evidence(
    path: Path, capabilities: list[dict[str, str]]
) -> list[dict[str, str]]:
    expected_fields = {"record_id"} | {
        item["search_term"] for item in capabilities
    }
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        fields = set(reader.fieldnames or [])
        if fields != expected_fields:
            unexpected = sorted(fields - expected_fields)
            missing = sorted(expected_fields - fields)
            raise ValueError(
                f"Evidence schema check failed. Unexpected={unexpected}; missing={missing}"
            )
        return list(reader)


def read_discovered_opportunities(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        fields = set(reader.fieldnames or [])
        if fields != OPPORTUNITY_FIELDS:
            unexpected = sorted(fields - OPPORTUNITY_FIELDS)
            missing = sorted(OPPORTUNITY_FIELDS - fields)
            raise ValueError(
                f"Opportunity schema check failed. Unexpected={unexpected}; missing={missing}"
            )
        return list(reader)


def analyse(
    vacancies: list[dict[str, str]],
    evidence: list[dict[str, str]],
    capabilities: list[dict[str, str]],
) -> dict[str, Any]:
    sample_size = len(vacancies)
    if len(evidence) != sample_size:
        raise ValueError("Vacancy and evidence row counts do not match")
    vacancy_ids = {row["record_id"] for row in vacancies}
    evidence_ids = {row["record_id"] for row in evidence}
    if vacancy_ids != evidence_ids:
        raise ValueError("Vacancy and evidence record IDs do not match")
    role_families = Counter(row["role_family"] for row in vacancies)
    work_models = Counter(row["work_model"] for row in vacancies)
    remote_count = sum("remote" in normalise(row["work_model"]) for row in vacancies)

    capability_counts = []
    for item in capabilities:
        count = sum(int(row[item["search_term"]]) for row in evidence)
        capability_counts.append(
            {
                "search_term": item["search_term"],
                "capability": item["capability"],
                "count": count,
                "share": count / sample_size if sample_size else 0,
            }
        )

    capability_counts.sort(key=lambda item: (-item["count"], item["capability"]))
    return {
        "sample_size": sample_size,
        "remote_count": remote_count,
        "role_families": dict(sorted(role_families.items())),
        "work_models": dict(sorted(work_models.items())),
        "capabilities": capability_counts,
    }


def write_summary(analysis: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "metric": "sample",
            "segment": "vacancies",
            "count": analysis["sample_size"],
            "share": 1.0 if analysis["sample_size"] else 0,
        },
        {
            "metric": "work_model",
            "segment": "remote_or_remote_first",
            "count": analysis["remote_count"],
            "share": analysis["remote_count"] / analysis["sample_size"]
            if analysis["sample_size"]
            else 0,
        },
    ]
    rows.extend(
        {
            "metric": "role_family",
            "segment": family,
            "count": count,
            "share": count / analysis["sample_size"] if analysis["sample_size"] else 0,
        }
        for family, count in analysis["role_families"].items()
    )
    rows.extend(
        {
            "metric": "capability",
            "segment": item["capability"],
            "count": item["count"],
            "share": item["share"],
        }
        for item in analysis["capabilities"]
    )
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(
            output, fieldnames=["metric", "segment", "count", "share"]
        )
        writer.writeheader()
        writer.writerows(rows)


def write_findings(analysis: dict[str, Any], path: Path) -> None:
    top = analysis["capabilities"][:3]
    lines = [
        "# Evidence-based positioning actions",
        "",
        f'Generated from a sanitised snapshot of **{analysis["sample_size"]} real public vacancies** collected on 23 August 2026.',
        "",
    ]
    for index, item in enumerate(top, start=1):
        percent = item["share"] * 100
        lines.extend(
            [
                f'## {index}. Emphasise {item["capability"]}',
                "",
                f'- Market evidence: found in **{item["count"]} of {analysis["sample_size"]} vacancies ({percent:.1f}%)**.',
                "- Action: connect this capability to a concise, verifiable professional example.",
                "",
            ]
        )
    lines.extend(
        [
            "## Human-review boundary",
            "",
            "These findings guide positioning and search language. They do not score employers, predict hiring outcomes or replace review of eligibility and role context.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_discovery_log(opportunities: list[dict[str, str]], path: Path) -> None:
    lines = [
        "# Strong opportunities discovered by the workflow",
        "",
        "This public log records high-value outcomes from the continuing monitoring process. Application details remain private.",
        "",
    ]
    for item in opportunities:
        lines.extend(
            [
                f'## {item["company"]} — {item["job_title"]}',
                "",
                f'- Discovered: {item["discovered_on"]}',
                f'- Work model: {item["work_model"]}',
                f'- Public recommendation: **{item["recommendation"]}**',
                f'- Match evidence: {item["match_evidence"]}',
                f'- [Official vacancy]({item["public_job_url"]})',
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=Path("data/public_vacancy_snapshot.csv")
    )
    parser.add_argument(
        "--capabilities",
        type=Path,
        default=Path("config/market_capabilities.json"),
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("data/public_keyword_evidence.csv"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument(
        "--opportunities",
        type=Path,
        default=Path("data/discovered_opportunities.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    vacancies = read_snapshot(args.input)
    with args.capabilities.open(encoding="utf-8") as source:
        capabilities = json.load(source)
    evidence = read_keyword_evidence(args.evidence, capabilities)
    result = analyse(vacancies, evidence, capabilities)
    opportunities = read_discovered_opportunities(args.opportunities)
    write_summary(result, args.output_dir / "market_summary.csv")
    write_findings(result, args.output_dir / "positioning_actions.md")
    write_discovery_log(opportunities, args.output_dir / "discovery_log.md")
    print(
        f'Analysed {result["sample_size"]} public vacancy records; '
        f'{result["remote_count"]} are remote or remote-first; '
        f'{len(opportunities)} strong monitored opportunity recorded.'
    )


if __name__ == "__main__":
    main()

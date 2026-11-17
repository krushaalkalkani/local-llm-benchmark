"""
Temperature study: same prompts × 5 runs at temp 0.0 and 0.7.

Measures:
- exact-match rate across the 5 runs (whole JSON equal after normalize)
- field disagreement rate (fraction of fields that are not identical across runs)
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from assistant.extract import extract_job
from assistant.schemas import ExtractSuccess, JobPosting

ROOT = Path(__file__).resolve().parents[2]
JOBS_PATH = ROOT / "configs" / "prompts" / "temp_study_jobs.json"
OUT_PATH = ROOT / "reports" / "temperature_study.json"
MODELS_YAML = ROOT / "configs" / "models.yaml"


def _default_model() -> str:
    data = yaml.safe_load(MODELS_YAML.read_text(encoding="utf-8"))
    return str(data["default_model"])


def _normalize(posting: JobPosting) -> dict[str, Any]:
    """Stable dict for equality checks (sorted skill lists)."""
    data = posting.model_dump()
    data["required_skills"] = sorted(s.lower() for s in data["required_skills"])
    data["nice_to_have_skills"] = sorted(s.lower() for s in data["nice_to_have_skills"])
    return data


def _field_disagreement(runs: list[dict[str, Any]]) -> float:
    """
    For each top-level field, 1 if not all runs agree, else 0.
    Return the mean across fields (0 = all agree, 1 = every field disagrees).
    """
    if not runs:
        return 0.0
    keys = list(runs[0].keys())
    disagree = 0
    for key in keys:
        values = [json.dumps(r.get(key), sort_keys=True, default=str) for r in runs]
        if len(set(values)) > 1:
            disagree += 1
    return disagree / len(keys) if keys else 0.0


def _exact_match_rate(runs: list[dict[str, Any]]) -> float:
    """Fraction of run-pairs that match, via most-common dump frequency."""
    if not runs:
        return 0.0
    dumps = [json.dumps(r, sort_keys=True) for r in runs]
    most = Counter(dumps).most_common(1)[0][1]
    return most / len(runs)


def run_temperature_study(
    *,
    model: str | None = None,
    runs_per_temp: int = 5,
    temperatures: tuple[float, ...] = (0.0, 0.7),
) -> dict[str, Any]:
    chosen = model or _default_model()
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    report: dict[str, Any] = {
        "model": chosen,
        "runs_per_temp": runs_per_temp,
        "jobs": [j["id"] for j in jobs],
        "by_temperature": {},
    }

    for temp in temperatures:
        job_rows: list[dict[str, Any]] = []
        exact_rates: list[float] = []
        disagree_rates: list[float] = []
        first_try_ok = 0
        total_attempts = 0

        for job in jobs:
            normalized_runs: list[dict[str, Any]] = []
            for _ in range(runs_per_temp):
                result = extract_job(job["text"], chosen, temperature=temp)
                total_attempts += 1
                if isinstance(result, ExtractSuccess):
                    if result.valid_first_try:
                        first_try_ok += 1
                    normalized_runs.append(_normalize(result.data))
                else:
                    # Failed extraction counts as a unique "miss" for variance.
                    normalized_runs.append({"__error__": result.error})

            emr = _exact_match_rate(normalized_runs)
            fdr = _field_disagreement(normalized_runs)
            exact_rates.append(emr)
            disagree_rates.append(fdr)
            job_rows.append(
                {
                    "id": job["id"],
                    "exact_match_rate": round(emr, 3),
                    "field_disagreement": round(fdr, 3),
                    "sample": normalized_runs[0] if normalized_runs else None,
                }
            )

        report["by_temperature"][str(temp)] = {
            "mean_exact_match_rate": round(sum(exact_rates) / len(exact_rates), 3),
            "mean_field_disagreement": round(
                sum(disagree_rates) / len(disagree_rates), 3
            ),
            "valid_first_try_rate": round(first_try_ok / total_attempts, 3)
            if total_attempts
            else 0.0,
            "per_job": job_rows,
        }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def format_study_table(report: dict[str, Any]) -> str:
    lines = [
        "| Temperature | Run-to-run exact match | Field disagreement |",
        "|---|---|---|",
    ]
    for temp, block in report["by_temperature"].items():
        lines.append(
            f"| {temp} | {block['mean_exact_match_rate']:.3f} | "
            f"{block['mean_field_disagreement']:.3f} |"
        )
    return "\n".join(lines)

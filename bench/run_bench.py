"""
Run every configured model over the eval set.

Writes reports/results.csv (one row per model × job).
"""

from __future__ import annotations

import csv
import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

import psutil
import yaml

from assistant.extract import extract_job
from assistant.schemas import ExtractSuccess
from bench.score import score_posting

ROOT = Path(__file__).resolve().parents[1]
JOBS_PATH = ROOT / "bench" / "prompts" / "jobs.jsonl"
MODELS_YAML = ROOT / "configs" / "models.yaml"
RESULTS_CSV = ROOT / "reports" / "results.csv"
HARDWARE_JSON = ROOT / "reports" / "hardware.json"


def load_jobs() -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for line in JOBS_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            jobs.append(json.loads(line))
    return jobs


def load_models() -> list[str]:
    data = yaml.safe_load(MODELS_YAML.read_text(encoding="utf-8"))
    return [str(m["name"]) for m in data["models"]]


def hardware_info() -> dict[str, Any]:
    mem_gb = round(psutil.virtual_memory().total / (1024**3), 1)
    chip = platform.processor() or platform.machine()
    # On Apple Silicon, platform.processor() is often empty; try sysctl.
    try:
        out = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
        ).strip()
        if out:
            chip = out
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return {
        "chip": chip,
        "ram_gb": mem_gb,
        "machine": platform.machine(),
        "macos": platform.mac_ver()[0] or platform.platform(),
        "python": platform.python_version(),
    }


def ollama_model_memory_mb() -> float:
    """
    Memory reported by `ollama ps` (better on Apple Silicon than process RSS).

    SIZE looks like "2.6 GB" or "800 MB". Sums all loaded models.
    """
    try:
        out = subprocess.check_output(["ollama", "ps"], text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0.0

    total_mb = 0.0
    lines = out.strip().splitlines()
    if len(lines) < 2:
        return 0.0
    for line in lines[1:]:
        parts = line.split()
        # NAME ID SIZE UNIT PROCESSOR ...
        if len(parts) < 4:
            continue
        try:
            value = float(parts[2])
        except ValueError:
            continue
        unit = parts[3].upper()
        if unit.startswith("G"):
            total_mb += value * 1024
        elif unit.startswith("M"):
            total_mb += value
        elif unit.startswith("K"):
            total_mb += value / 1024
    return round(total_mb, 1)


def ensure_model_loaded(model: str) -> float:
    """
    Force-load a model with a tiny chat; return load wall time in seconds.
    """
    import ollama

    t0 = time.perf_counter()
    ollama.chat(
        model=model,
        messages=[{"role": "user", "content": "ping"}],
        options={"temperature": 0, "num_predict": 1},
    )
    return round(time.perf_counter() - t0, 2)


def run_bench(
    *,
    temperature: float = 0.0,
    limit: int | None = None,
    models: list[str] | None = None,
) -> Path:
    jobs = load_jobs()
    if limit is not None:
        jobs = jobs[:limit]
    model_list = models if models is not None else load_models()
    hw = hardware_info()
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    HARDWARE_JSON.write_text(json.dumps(hw, indent=2), encoding="utf-8")

    fieldnames = [
        "model",
        "job_id",
        "ok",
        "valid_first_try",
        "attempts",
        "ttft_ms",
        "tokens_per_second",
        "total_latency_ms",
        "prompt_tokens",
        "output_tokens",
        "process_rss_mb",
        "ollama_rss_mb",
        "load_time_s",
        "field_accuracy",
        "required_skills_f1",
        "nice_to_have_skills_f1",
        "title",
        "company",
        "seniority",
        "location",
        "remote",
        "years_experience",
        "salary",
    ]

    rows: list[dict[str, Any]] = []
    print(f"Hardware: {hw}")
    print(f"Jobs: {len(jobs)}  Models: {model_list}")

    for model in model_list:
        print(f"\n=== Loading {model} ===")
        load_time_s = ensure_model_loaded(model)
        peak_ollama = ollama_model_memory_mb()
        print(f"load_time_s={load_time_s}  ollama_mem_mb≈{peak_ollama}")

        for i, job in enumerate(jobs, start=1):
            print(f"[{model}] {i}/{len(jobs)} {job['id']} ...", flush=True)
            result = extract_job(job["text"], model, temperature=temperature)
            peak_ollama = max(peak_ollama, ollama_model_memory_mb())

            pred = None
            metrics: dict[str, Any] = {}
            ok = False
            valid_first = False
            attempts = 0
            if isinstance(result, ExtractSuccess):
                ok = True
                valid_first = result.valid_first_try
                attempts = result.attempts
                pred = result.data.model_dump()
                metrics = result.metrics
            else:
                attempts = result.attempts

            scores = score_posting(pred, job["expected"])
            row = {
                "model": model,
                "job_id": job["id"],
                "ok": ok,
                "valid_first_try": valid_first,
                "attempts": attempts,
                "ttft_ms": metrics.get("ttft_ms"),
                "tokens_per_second": metrics.get("tokens_per_second"),
                "total_latency_ms": metrics.get("total_latency_ms"),
                "prompt_tokens": metrics.get("prompt_tokens"),
                "output_tokens": metrics.get("output_tokens"),
                "process_rss_mb": metrics.get("peak_rss_mb"),
                "ollama_rss_mb": peak_ollama,
                "load_time_s": load_time_s,
                "field_accuracy": scores["field_accuracy"],
                "required_skills_f1": scores["required_skills_f1"],
                "nice_to_have_skills_f1": scores["nice_to_have_skills_f1"],
                "title": scores.get("title"),
                "company": scores.get("company"),
                "seniority": scores.get("seniority"),
                "location": scores.get("location"),
                "remote": scores.get("remote"),
                "years_experience": scores.get("years_experience"),
                "salary": scores.get("salary"),
            }
            rows.append(row)

    with RESULTS_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows -> {RESULTS_CSV}")
    return RESULTS_CSV


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run local LLM extraction benchmark")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only run the first N jobs (smoke test).",
    )
    parser.add_argument(
        "--model",
        action="append",
        default=None,
        help="Model tag to run (repeatable). Default: all from configs/models.yaml.",
    )
    args = parser.parse_args()
    run_bench(limit=args.limit, models=args.model)


if __name__ == "__main__":
    main()

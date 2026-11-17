"""
Build reports/benchmark_report.md + charts from reports/results.csv.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS_CSV = ROOT / "reports" / "results.csv"
HARDWARE_JSON = ROOT / "reports" / "hardware.json"
REPORT_MD = ROOT / "reports" / "benchmark_report.md"
CHART_SPEED = ROOT / "reports" / "chart_speed.png"
CHART_QUALITY = ROOT / "reports" / "chart_quality.png"
CHART_MEMORY = ROOT / "reports" / "chart_memory.png"


def _load() -> tuple[pd.DataFrame, dict]:
    if not RESULTS_CSV.exists():
        raise SystemExit(f"Missing {RESULTS_CSV}. Run: make bench (or uv run python -m bench.run_bench)")
    df = pd.read_csv(RESULTS_CSV)
    hw = {}
    if HARDWARE_JSON.exists():
        hw = json.loads(HARDWARE_JSON.read_text(encoding="utf-8"))
    return df, hw


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("model", sort=False)
    summary = pd.DataFrame(
        {
            "n": g.size(),
            "json_valid_1st": g["valid_first_try"].mean(),
            "json_ok": g["ok"].mean(),
            "field_accuracy": g["field_accuracy"].mean(),
            "required_skills_f1": g["required_skills_f1"].mean(),
            "ttft_ms": g["ttft_ms"].mean(),
            "tokens_per_s": g["tokens_per_second"].mean(),
            "latency_ms": g["total_latency_ms"].mean(),
            "peak_ollama_mb": g["ollama_rss_mb"].max(),
            "load_time_s": g["load_time_s"].first(),
        }
    ).reset_index()
    return summary


def pick_recommendation(summary: pd.DataFrame) -> str:
    """
    Simple rule for this Mac laptop task:
    prefer highest field_accuracy; break ties with higher tokens/s;
    if still tied, prefer lower peak RAM.
    """
    s = summary.copy()
    s = s.sort_values(
        by=["field_accuracy", "tokens_per_s", "peak_ollama_mb"],
        ascending=[False, False, True],
    )
    best = s.iloc[0]
    return (
        f"For this job-extraction task on this machine, pick **{best['model']}**: "
        f"field accuracy {best['field_accuracy']:.1%}, "
        f"{best['tokens_per_s']:.1f} tok/s, "
        f"peak Ollama memory ≈ {best['peak_ollama_mb']:.0f} MB, "
        f"first-try JSON validity {best['json_valid_1st']:.1%}."
    )


def make_charts(summary: pd.DataFrame) -> None:
    models = summary["model"].tolist()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(models, summary["tokens_per_s"], color="#2f6f4e")
    ax.set_ylabel("Tokens / second")
    ax.set_title("Speed by model")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(CHART_SPEED, dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = range(len(models))
    width = 0.35
    ax.bar([i - width / 2 for i in x], summary["field_accuracy"], width, label="Field accuracy", color="#1f4e79")
    ax.bar([i + width / 2 for i in x], summary["json_valid_1st"], width, label="JSON valid (1st try)", color="#c47b2b")
    ax.set_xticks(list(x))
    ax.set_xticklabels(models, rotation=15)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Rate")
    ax.set_title("Quality by model")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_QUALITY, dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(models, summary["peak_ollama_mb"], color="#6b3fa0")
    ax.set_ylabel("Peak Ollama memory (MB)")
    ax.set_title("Memory by model")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(CHART_MEMORY, dpi=140)
    plt.close(fig)


def write_report(summary: pd.DataFrame, hw: dict, recommendation: str) -> None:
    lines: list[str] = []
    lines.append("# Local LLM Benchmark Report")
    lines.append("")
    lines.append("## Setup")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append(f"| Chip | {hw.get('chip', 'unknown')} |")
    lines.append(f"| RAM | {hw.get('ram_gb', '?')} GB |")
    lines.append(f"| macOS | {hw.get('macos', 'unknown')} |")
    lines.append(f"| Machine | {hw.get('machine', '')} |")
    lines.append("| Task | Job posting → structured JSON (`JobPosting`) |")
    lines.append("| Temperature | 0.0 |")
    lines.append(f"| Eval set | {int(summary['n'].iloc[0])} prompts in `bench/prompts/jobs.jsonl` |")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("- Each model is force-loaded once (`ollama run …`), then run on every prompt.")
    lines.append("- Extraction uses Ollama `format=<JSON Schema>` + Pydantic validation + one retry.")
    lines.append("- **JSON valid (1st try):** share of prompts valid without retry.")
    lines.append("- **Field accuracy:** mean of per-field scores (exact/soft match for scalars, F1 for skill lists).")
    lines.append("- **Peak RAM:** max `ollama ps` SIZE during that model's run (unified memory on Apple Silicon).")
    lines.append("- **TTFT / tok/s:** from the extraction client metrics (non-streaming call: TTFT ≈ total latency).")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append(
        "| Model | Peak RAM (MB) | Load (s) | TTFT (ms) | Tokens/s | JSON valid (1st) | Field accuracy |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for _, r in summary.iterrows():
        lines.append(
            f"| {r['model']} | {r['peak_ollama_mb']:.0f} | {r['load_time_s']:.1f} | "
            f"{r['ttft_ms']:.0f} | {r['tokens_per_s']:.1f} | "
            f"{r['json_valid_1st']:.1%} | {r['field_accuracy']:.1%} |"
        )
    lines.append("")
    lines.append("## Charts")
    lines.append("")
    lines.append("![Speed](chart_speed.png)")
    lines.append("")
    lines.append("![Quality](chart_quality.png)")
    lines.append("")
    lines.append("![Memory](chart_memory.png)")
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(recommendation)
    lines.append("")
    lines.append("## Reproduce")
    lines.append("")
    lines.append("```bash")
    lines.append("make bench")
    lines.append("```")
    lines.append("")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_MD}")


def main() -> None:
    df, hw = _load()
    summary = summarize(df)
    make_charts(summary)
    rec = pick_recommendation(summary)
    write_report(summary, hw, rec)
    print(summary.to_string(index=False))
    print("\n" + rec)


if __name__ == "__main__":
    main()

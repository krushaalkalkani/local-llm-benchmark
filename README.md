# Offline Local AI Assistant + Benchmark Study

Private local assistant on Ollama: chat, structured job extraction, and a 3-model benchmark on this Mac.

## Hardware

| Field | Value |
|---|---|
| Chip | Apple M4 |
| RAM | 16 GB |
| macOS | 27.2.1 |

## Setup

```bash
uv sync
uv run python scripts/setup.py   # needs Wi-Fi once to pull models
```

## Phase 1 — chat + metrics

```bash
uv run assistant chat
uv run assistant serve --port 8001   # if 8000 is busy
```

## Phase 2 — structured extract + temperature study

```bash
uv run assistant extract --file samples/sample_job.txt
uv run assistant temp-study
```

| Temperature | Run-to-run exact match | Field disagreement |
|---|---|---|
| 0.0 | 1.000 | 0.000 |
| 0.7 | 0.467 | 0.407 |

*(llama3.2:3b, 3 sample jobs × 5 runs. At temperature 0 the JSON is stable; at 0.7 it varies.)*

## Phase 3 — model comparison (the main deliverable)

35 hand-labeled job postings in `bench/prompts/jobs.jsonl`. Each of the 3 models is scored on speed, memory, JSON validity, and field accuracy.

```bash
make bench
# same as:
#   uv run python -m bench.run_bench
#   uv run python -m bench.report
```

Outputs:
- `reports/results.csv`
- `reports/benchmark_report.md`
- `reports/chart_*.png`

### Results (Apple M4, 16 GB, 35 prompts, temp 0.0)

| Model | Peak RAM (MB) | TTFT (ms) | Tokens/s | JSON valid (1st) | Field accuracy |
|---|---:|---:|---:|---:|---:|
| llama3.2:3b | 2662 | 2392 | 33.4 | 100.0% | 68.0% |
| phi4-mini | 3174 | 3757 | 24.5 | 100.0% | 61.0% |
| mistral:7b | 5120 | 11091 | 12.5 | 100.0% | 73.9% |

**Recommendation:** For max field accuracy on this Mac, pick `mistral:7b`. For a faster / lighter default day-to-day, pick `llama3.2:3b` (about 2.7× tok/s, half the RAM, only ~6 points lower accuracy).

## Project site

Marketing page for this project lives in `web/` (Next.js). Deploy from that folder on Vercel (`rootDirectory: web`).

```bash
cd web && npm run dev
```

## Project layout

```
configs/                 # models + prompts
samples/sample_job.txt
scripts/setup.py
src/assistant/           # chat, extract, CLI, API
bench/
  prompts/jobs.jsonl     # eval set + expected JSON
  run_bench.py
  score.py
  report.py
reports/                 # generated CSV, markdown report, charts
web/                     # single-page project site
Makefile                 # `make bench`
```

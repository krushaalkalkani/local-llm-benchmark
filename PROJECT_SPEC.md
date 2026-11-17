# Project 2 — Offline Local AI Assistant + Small-Model Benchmark Study

> **For Claude (the builder):** Build this phase by phase. After each phase, stop, show how to run it, and explain what was built in simple language — the owner (Krushal) is learning through this project. Everything must run **fully offline on a Mac laptop** after models are downloaded. Record hardware details (chip, RAM, macOS) in every benchmark report.

## 1. What we are building
A **private, offline assistant** powered by small open-source models (3–8B parameters) running locally through **Ollama**, plus a rigorous **benchmark report** comparing models on speed, memory and output quality.

**Default use case: offline "Job Description → structured data" assistant.** The user pastes a messy job posting; the assistant returns validated JSON (title, company, seniority, location, remote, required skills, nice-to-have skills, years of experience, salary range). Why: privacy-friendly, a clear right answer to evaluate against, and it connects to the owner's job-tools work. A second mode: free-form Q&A chat for general use.

## 2. Why it matters
Many companies can't send data to external APIs (privacy regulation, latency, cost at scale, edge devices). Most candidates have zero hands-on experience with local inference trade-offs. Model selection backed by data is a real, recurring engineering decision.

## 3. Tech stack
| Layer | Choice |
|---|---|
| Runtime | Ollama |
| Models | `llama3.2:3b`, `phi4-mini`, `mistral:7b` (optionally `qwen3:4b`/`qwen3:8b`) — verify exact tags with `ollama list`/the Ollama library |
| Language | Python 3.11+, `uv` |
| Client | `ollama` Python package (or HTTP API) |
| Validation | Pydantic v2 |
| Interface | CLI (Typer) + FastAPI wrapper |
| Metrics | `psutil` for memory; timing via streaming tokens |
| Reports | pandas + matplotlib → Markdown report |

## 4. Architecture
```
 CLI / FastAPI ─► Assistant
                    ├─ prompt builder (versioned prompts)
                    ├─ Ollama client (streaming) ──► local model
                    ├─ JSON schema enforcement (Ollama `format` param + Pydantic)
                    ├─ retry once on invalid output → graceful failure
                    └─ metrics logger (TTFT, tokens/sec, total latency, memory)

 bench/ ─► runs every model × prompt × temperature × quantization ─► results.csv ─► report.md + charts
```

## 5. Suggested repo structure
```
local-llm-assistant/
├── README.md
├── pyproject.toml
├── configs/{models.yaml, prompts/}
├── src/assistant/
│   ├── client.py        # Ollama wrapper with streaming + timing
│   ├── schemas.py       # Pydantic JobPosting model
│   ├── extract.py       # structured extraction + validate + retry
│   ├── chat.py
│   ├── cli.py
│   └── api.py
├── bench/
│   ├── prompts/         # 30–50 standardized test prompts + expected JSON
│   ├── run_bench.py
│   ├── score.py         # quality scoring
│   └── report.py
├── reports/             # generated benchmark reports + charts
└── tests/
```

## 6. Phases

### Phase 1 — Run locally and measure
Tasks:
1. Setup script: check Ollama is installed, pull the chosen models.
2. CLI chat + FastAPI `POST /chat` with streaming.
3. Measure per request: **time to first token (TTFT)**, **tokens/second**, **total latency**, prompt & output token counts.
4. Log every request to `logs/requests.jsonl`.

Acceptance: `assistant chat` works with Wi-Fi off; metrics printed after every response.

### Phase 2 — Structure and determinism
Tasks:
1. Pydantic `JobPosting` schema; use Ollama's structured output (`format=<json schema>`).
2. Validate with Pydantic; on failure, **re-prompt once** including the validation error; if it fails again, return a clean error object (never crash, never return broken JSON).
3. Track: JSON validity rate (first try), validity after retry, field-level accuracy.
4. **Temperature study:** run the same prompts 5× at temperature 0 and 0.7; measure output variance (exact-match rate across runs, field disagreement rate). Document findings.

Acceptance: 100% of returned outputs are either valid JSON or a clean error; temperature study table in README.

### Phase 3 — Model comparison study (the star deliverable)
Tasks:
1. Standardized eval set: **30–50 job postings** with hand-written expected JSON (`bench/prompts/`).
2. Benchmark 3 models on the same hardware: peak memory, load time, TTFT, tokens/sec, JSON validity, field accuracy (exact match for scalars, F1 for skill lists).
3. **Stretch — quantization:** compare GGUF Q4 vs Q5 (vs Q8 if RAM allows) for at least one model; plot quality vs speed.
4. Generate `reports/benchmark_report.md`: setup, method, results tables, charts, recommendation ("for this task on an M-series Mac, pick X because…").

Acceptance: report is reproducible with one command (`make bench`).

## 7. Results tables (fill with real numbers)
| Model | Quant | Peak RAM | TTFT (ms) | Tokens/s | JSON valid (1st try) | Field accuracy |
|---|---|---|---|---|---|---|
| llama3.2:3b | | | | | | |
| phi4-mini | | | | | | |
| mistral:7b | | | | | | |

| Temperature | Run-to-run exact match | Field disagreement |
|---|---|---|
| 0.0 | | |
| 0.7 | | |

## 8. Definition of done
- [ ] Works fully offline
- [ ] Schema-enforced output with validation + single retry + graceful failure
- [ ] Temperature variance study
- [ ] 3-model benchmark with real numbers, charts and a recommendation
- [ ] (Stretch) quantization trade-off study
- [ ] README with hardware specs, results, lessons learned

## 9. Resume bullet template
- Built an offline LLM assistant on Ollama with Pydantic-validated structured output and automatic retry, achieving **X%** valid JSON with no external API calls.
- Benchmarked 3 small models (3–7B) and 2 quantization levels across 40 standardized prompts; documented speed/memory/quality trade-offs (e.g. **Y tok/s vs Z% accuracy**) and recommended a model with data.

## 10. Interview questions this prepares you for
- Why run models locally? What are the trade-offs?
- What is TTFT and why does it matter for UX?
- What does quantization do and what does it cost you?
- How do you get reliable structured output from an LLM?
- What does temperature actually change?

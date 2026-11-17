"""Structured job extraction: Ollama format=schema + Pydantic validate + one retry."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from assistant.client import ROOT, chat_once
from assistant.schemas import ExtractError, ExtractResult, ExtractSuccess, JobPosting

PROMPT_PATH = ROOT / "configs" / "prompts" / "extract_job.txt"
EXTRACT_LOG = ROOT / "logs" / "extracts.jsonl"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def _schema_for_ollama() -> dict[str, Any]:
    """JSON Schema Ollama uses to constrain the model output."""
    return JobPosting.model_json_schema()


def _parse_and_validate(raw: str) -> JobPosting:
    data = json.loads(raw)
    return JobPosting.model_validate(data)


def extract_job(
    job_text: str,
    model: str,
    *,
    temperature: float = 0.0,
) -> ExtractResult:
    """
    Extract a JobPosting from free-form text.

    Attempt 1: system prompt + job text, with Ollama `format=<schema>`.
    Attempt 2 (only if validation fails): include the validation error and retry once.
    Always returns ExtractSuccess or ExtractError — never raises for bad model JSON.
    """
    system = load_system_prompt()
    schema = _schema_for_ollama()
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": f"Extract structured fields from this job posting:\n\n{job_text}",
        },
    ]

    raw_last = ""
    valid_first_try = False
    metrics_blob: dict[str, Any] = {}

    for attempt in (1, 2):
        result = chat_once(
            messages,
            model,
            temperature=temperature,
            format=schema,
            log_kind="extract",
        )
        raw_last = result.text.strip()
        metrics_blob = asdict(result.metrics)

        try:
            posting = _parse_and_validate(raw_last)
        except (json.JSONDecodeError, ValidationError) as exc:
            if attempt == 1:
                # Re-prompt once with the error so the model can fix the shape.
                messages = [
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": (
                            f"Extract structured fields from this job posting:\n\n{job_text}"
                        ),
                    },
                    {"role": "assistant", "content": raw_last},
                    {
                        "role": "user",
                        "content": (
                            "Your previous JSON failed validation. "
                            f"Fix it and return ONLY valid JSON.\n\nError:\n{exc}"
                        ),
                    },
                ]
                continue

            err = ExtractError(
                error=f"Validation failed after retry: {exc}",
                attempts=2,
                raw_last_output=raw_last,
            )
            _log_extract(job_text, err, temperature=temperature, model=model)
            return err

        valid_first_try = attempt == 1
        success = ExtractSuccess(
            data=posting,
            attempts=attempt,
            valid_first_try=valid_first_try,
            metrics=metrics_blob,
        )
        _log_extract(job_text, success, temperature=temperature, model=model)
        return success

    err = ExtractError(
        error="Extraction exhausted without a result",
        attempts=2,
        raw_last_output=raw_last,
    )
    _log_extract(job_text, err, temperature=temperature, model=model)
    return err


def _log_extract(
    job_text: str,
    result: ExtractResult,
    *,
    temperature: float,
    model: str,
) -> None:
    EXTRACT_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "temperature": temperature,
        "job_text_chars": len(job_text),
        "ok": result.ok,
        "attempts": result.attempts,
    }
    if isinstance(result, ExtractSuccess):
        record["valid_first_try"] = result.valid_first_try
        record["data"] = result.data.model_dump()
        record["metrics"] = result.metrics
    else:
        record["error"] = result.error
        record["raw_last_output"] = result.raw_last_output

    with EXTRACT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def validity_summary(log_path: Path | None = None) -> dict[str, Any]:
    """Summarize first-try vs after-retry validity from extracts.jsonl."""
    path = log_path or EXTRACT_LOG
    if not path.exists():
        return {"total": 0, "ok": 0, "valid_first_try": 0, "valid_after_retry": 0}

    total = ok = first = after_retry = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        total += 1
        if row.get("ok"):
            ok += 1
            if row.get("valid_first_try"):
                first += 1
            else:
                after_retry += 1

    return {
        "total": total,
        "ok": ok,
        "valid_first_try": first,
        "valid_after_retry": after_retry,
        "ok_rate": (ok / total) if total else 0.0,
        "first_try_rate": (first / total) if total else 0.0,
    }

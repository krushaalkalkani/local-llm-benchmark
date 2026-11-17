"""Ollama client with streaming replies and per-request timing."""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import ollama
import psutil

# Project root: .../02-local-llm-benchmark (src/assistant/client.py -> parents[2])
ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = ROOT / "logs" / "requests.jsonl"


@dataclass
class Metrics:
    """Numbers we care about for every reply."""

    model: str
    ttft_ms: float  # time to first token (milliseconds)
    tokens_per_second: float
    total_latency_ms: float
    prompt_tokens: int
    output_tokens: int
    peak_rss_mb: float  # this process's memory; model RAM lives in Ollama


@dataclass
class ChatResult:
    """Full reply plus the metrics for that call."""

    text: str
    metrics: Metrics


def stream_chat(
    messages: list[dict[str, str]],
    model: str,
    *,
    temperature: float = 0.7,
    format: dict[str, Any] | str | None = None,
) -> Iterator[str | Metrics]:
    """
    Stream tokens from Ollama, then yield one Metrics object at the end.

    TTFT = wall time from request start until the first text chunk.
    tokens/sec = output tokens / generation time after the first token.
    `format` is passed through to Ollama (JSON schema or "json").
    """
    process = psutil.Process()
    peak_rss = process.memory_info().rss
    t0 = time.perf_counter()
    ttft_ms: float | None = None
    pieces: list[str] = []

    prompt_tokens = 0
    output_tokens = 0

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature},
    }
    if format is not None:
        kwargs["format"] = format

    stream = ollama.chat(**kwargs)

    for chunk in stream:
        peak_rss = max(peak_rss, process.memory_info().rss)

        # Final chunk often has usage counts and empty content.
        if getattr(chunk, "done", False):
            prompt_tokens = int(getattr(chunk, "prompt_eval_count", None) or 0)
            output_tokens = int(getattr(chunk, "eval_count", None) or 0)

        content = ""
        message = getattr(chunk, "message", None)
        if message is not None:
            content = getattr(message, "content", None) or ""
        if not content and isinstance(chunk, dict):
            content = (chunk.get("message") or {}).get("content") or ""

        if content:
            if ttft_ms is None:
                ttft_ms = (time.perf_counter() - t0) * 1000
            pieces.append(content)
            yield content

    t1 = time.perf_counter()
    total_ms = (t1 - t0) * 1000
    if ttft_ms is None:
        ttft_ms = total_ms

    # Generation window starts when the first token arrives.
    gen_seconds = max((t1 - t0) - (ttft_ms / 1000), 1e-6)
    if output_tokens <= 0:
        # Fallback if the server did not send eval_count.
        output_tokens = max(len("".join(pieces).split()), 0)
    tokens_per_second = output_tokens / gen_seconds if output_tokens else 0.0

    metrics = Metrics(
        model=model,
        ttft_ms=round(ttft_ms, 1),
        tokens_per_second=round(tokens_per_second, 2),
        total_latency_ms=round(total_ms, 1),
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        peak_rss_mb=round(peak_rss / (1024 * 1024), 1),
    )
    yield metrics


def chat(
    messages: list[dict[str, str]],
    model: str,
    *,
    temperature: float = 0.7,
    on_token: Any | None = None,
    format: dict[str, Any] | str | None = None,
) -> ChatResult:
    """Run a chat request; optionally call on_token(str) for each chunk."""
    pieces: list[str] = []
    metrics: Metrics | None = None

    for item in stream_chat(
        messages, model, temperature=temperature, format=format
    ):
        if isinstance(item, Metrics):
            metrics = item
        else:
            pieces.append(item)
            if on_token is not None:
                on_token(item)

    if metrics is None:
        raise RuntimeError("Ollama stream ended without metrics")

    text = "".join(pieces)
    log_request(
        messages=messages,
        response=text,
        metrics=metrics,
        temperature=temperature,
    )
    return ChatResult(text=text, metrics=metrics)


def chat_once(
    messages: list[dict[str, str]],
    model: str,
    *,
    temperature: float = 0.0,
    format: dict[str, Any] | str | None = None,
    log_kind: str = "chat",
) -> ChatResult:
    """
    Non-streaming call (better for structured JSON).

    Still records TTFT as total latency when the whole reply arrives at once.
    """
    process = psutil.Process()
    peak_rss = process.memory_info().rss
    t0 = time.perf_counter()

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if format is not None:
        kwargs["format"] = format

    response = ollama.chat(**kwargs)
    t1 = time.perf_counter()
    peak_rss = max(peak_rss, process.memory_info().rss)

    text = ""
    message = getattr(response, "message", None)
    if message is not None:
        text = getattr(message, "content", None) or ""
    elif isinstance(response, dict):
        text = (response.get("message") or {}).get("content") or ""

    prompt_tokens = int(getattr(response, "prompt_eval_count", None) or 0)
    output_tokens = int(getattr(response, "eval_count", None) or 0)
    total_ms = (t1 - t0) * 1000
    gen_seconds = max(total_ms / 1000, 1e-6)
    tokens_per_second = output_tokens / gen_seconds if output_tokens else 0.0

    metrics = Metrics(
        model=model,
        ttft_ms=round(total_ms, 1),  # non-streaming: first token ≈ full reply
        tokens_per_second=round(tokens_per_second, 2),
        total_latency_ms=round(total_ms, 1),
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        peak_rss_mb=round(peak_rss / (1024 * 1024), 1),
    )
    log_request(
        messages=messages,
        response=text,
        metrics=metrics,
        temperature=temperature,
        kind=log_kind,
    )
    return ChatResult(text=text, metrics=metrics)


def log_request(
    *,
    messages: list[dict[str, str]],
    response: str,
    metrics: Metrics,
    temperature: float,
    kind: str = "chat",
) -> None:
    """Append one JSON line to logs/requests.jsonl."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "temperature": temperature,
        "messages": messages,
        "response": response,
        **asdict(metrics),
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def format_metrics(m: Metrics) -> str:
    """Human-readable metrics block for the terminal."""
    return (
        f"\n--- metrics ---\n"
        f"model:            {m.model}\n"
        f"TTFT:             {m.ttft_ms:.1f} ms\n"
        f"tokens/sec:       {m.tokens_per_second:.2f}\n"
        f"total latency:    {m.total_latency_ms:.1f} ms\n"
        f"prompt tokens:    {m.prompt_tokens}\n"
        f"output tokens:    {m.output_tokens}\n"
        f"process RSS:      {m.peak_rss_mb:.1f} MB\n"
        f"---------------"
    )

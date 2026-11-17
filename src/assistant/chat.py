"""Thin chat helpers used by the CLI and API."""

from __future__ import annotations

from collections.abc import Callable, Iterator

from assistant.client import ChatResult, Metrics, chat, log_request, stream_chat


def run_turn(
    user_text: str,
    history: list[dict[str, str]],
    model: str,
    *,
    temperature: float = 0.7,
    on_token: Callable[[str], None] | None = None,
) -> ChatResult:
    """Add the user message, call the model, append the assistant reply."""
    history.append({"role": "user", "content": user_text})
    result = chat(history, model, temperature=temperature, on_token=on_token)
    history.append({"role": "assistant", "content": result.text})
    return result


def stream_turn(
    user_text: str,
    history: list[dict[str, str]],
    model: str,
    *,
    temperature: float = 0.7,
) -> Iterator[str | Metrics]:
    """Stream one turn; updates history when the Metrics object arrives."""
    history.append({"role": "user", "content": user_text})
    pieces: list[str] = []
    for item in stream_chat(history, model, temperature=temperature):
        if isinstance(item, Metrics):
            text = "".join(pieces)
            history.append({"role": "assistant", "content": text})
            # stream_chat does not log; we log once the reply is complete.
            log_request(
                messages=history[:-1],  # up through the user message
                response=text,
                metrics=item,
                temperature=temperature,
            )
            yield item
        else:
            pieces.append(item)
            yield item

"""FastAPI wrapper: POST /chat (stream) and POST /extract (structured JSON)."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from assistant.chat import stream_turn
from assistant.cli import load_default_model
from assistant.client import Metrics
from assistant.extract import extract_job

app = FastAPI(title="Local LLM Assistant", version="0.2.0")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    model: Optional[str] = None
    temperature: float = 0.7
    history: list[dict[str, str]] = Field(default_factory=list)


class ExtractRequest(BaseModel):
    job_text: str = Field(..., min_length=1)
    model: Optional[str] = None
    temperature: float = 0.0


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
def chat_endpoint(body: ChatRequest) -> StreamingResponse:
    """
    Stream NDJSON lines:
      {"type":"token","content":"..."}
      {"type":"metrics", ...metrics fields...}
    """
    model = body.model or load_default_model()
    history = list(body.history)

    def event_stream():
        for item in stream_turn(
            body.message,
            history,
            model,
            temperature=body.temperature,
        ):
            if isinstance(item, Metrics):
                payload = {"type": "metrics", **item.__dict__}
            else:
                payload = {"type": "token", "content": item}
            yield json.dumps(payload, ensure_ascii=False) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@app.post("/extract")
def extract_endpoint(body: ExtractRequest) -> JSONResponse:
    """Return validated JobPosting JSON, or a clean error object."""
    model = body.model or load_default_model()
    result = extract_job(body.job_text, model, temperature=body.temperature)
    status = 200 if result.ok else 422
    return JSONResponse(content=result.model_dump(), status_code=status)

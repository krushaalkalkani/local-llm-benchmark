"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { MODELS, SAMPLE_JSON, SAMPLE_POST } from "../lib/data";

// Roughly 4 characters per token — close enough to show relative speed.
const CHARS_PER_TOKEN = 4;
const TOTAL_TOKENS = Math.ceil(SAMPLE_JSON.length / CHARS_PER_TOKEN);

function finishMs(ttftMs: number, tokPerSec: number) {
  return ttftMs + (TOTAL_TOKENS / tokPerSec) * 1000;
}

const LONGEST = Math.max(...MODELS.map((m) => finishMs(m.ttftMs, m.tokPerSec)));
const AXIS_MS = Math.ceil(LONGEST / 5000) * 5000;

export default function Race() {
  const [speed, setSpeed] = useState<1 | 3>(3);
  const [elapsed, setElapsed] = useState(0); // in model time (ms)
  const [runId, setRunId] = useState(0);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const start = performance.now();
    const tick = (now: number) => {
      const t = reduced ? LONGEST : (now - start) * speed;
      setElapsed(Math.min(t, LONGEST));
      if (t < LONGEST) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
    };
  }, [speed, runId]);

  const replay = useCallback(() => setRunId((r) => r + 1), []);

  return (
    <div className="race">
      <div className="race-input">
        <p className="race-label">Input: job post jd_001</p>
        <p className="race-post">{SAMPLE_POST}</p>
      </div>

      <div className="timeline" aria-label="Timeline of each model's extraction">
        {MODELS.map((m) => {
          const end = finishMs(m.ttftMs, m.tokPerSec);
          const waitPct = (m.ttftMs / AXIS_MS) * 100;
          const genPct = ((end - m.ttftMs) / AXIS_MS) * 100;
          const nowWait = Math.min(elapsed, m.ttftMs);
          const nowGen = Math.max(0, Math.min(elapsed, end) - m.ttftMs);
          const done = elapsed >= end;
          return (
            <div key={m.id} className={`tl-row model-${m.id}`}>
              <span className="tl-name">{m.name}</span>
              <span className="tl-track">
                <span className="tl-wait" style={{ width: `${waitPct}%` }}>
                  <span style={{ width: `${(nowWait / m.ttftMs) * 100}%` }} />
                </span>
                <span className="tl-gen" style={{ left: `${waitPct}%`, width: `${genPct}%` }}>
                  <span style={{ width: `${(nowGen / (end - m.ttftMs)) * 100}%` }} />
                </span>
              </span>
              <span className="tl-end tabular" data-done={done || undefined}>
                {done ? `${(end / 1000).toFixed(1)} s` : "…"}
              </span>
            </div>
          );
        })}
        <div className="tl-axis" aria-hidden>
          <span />
          <span className="tl-ticks">
            {Array.from({ length: AXIS_MS / 5000 + 1 }, (_, i) => (
              <span key={i} style={{ left: `${(i * 5000 * 100) / AXIS_MS}%` }}>{i * 5} s</span>
            ))}
          </span>
          <span />
        </div>
        <div className="tl-legend">
          <span><i className="tl-key-wait" /> Waiting for first token</span>
          <span><i className="tl-key-gen" /> Generating JSON</span>
        </div>
      </div>

      <div className="race-lanes">
        {MODELS.map((m) => {
          const genMs = Math.max(0, elapsed - m.ttftMs);
          const tokens = Math.min(TOTAL_TOKENS, Math.floor((genMs / 1000) * m.tokPerSec));
          const shown = SAMPLE_JSON.slice(0, tokens * CHARS_PER_TOKEN);
          const done = tokens >= TOTAL_TOKENS;
          const waiting = elapsed < m.ttftMs;
          return (
            <div key={m.id} className={`lane lane-${m.id}`} data-done={done || undefined}>
              <div className="lane-head">
                <span className="lane-name">{m.name}</span>
                <span className="lane-clock tabular">{(Math.min(elapsed, finishMs(m.ttftMs, m.tokPerSec)) / 1000).toFixed(1)} s</span>
              </div>
              <pre className="lane-body" aria-hidden>
                {waiting ? <span className="lane-wait">Loading prompt… first token at {(m.ttftMs / 1000).toFixed(1)} s</span> : shown}
                {!waiting && !done && <span className="caret" />}
              </pre>
              <div className="lane-foot">
                {done ? (
                  <>
                    <span>Valid JSON</span>
                    <span className="tabular">{m.accuracy.toFixed(1)}% field accuracy</span>
                  </>
                ) : (
                  <>
                    <span className="tabular">{tokens} / {TOTAL_TOKENS} tokens</span>
                    <span className="tabular">{m.tokPerSec} tok/s</span>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="race-controls">
        <p className="race-note">
          Each lane replays the extraction at that model&rsquo;s measured average speed. Field accuracy is the
          average across all 35 posts.
        </p>
        <div className="race-buttons">
          <div className="seg" role="group" aria-label="Playback speed">
            <button type="button" aria-pressed={speed === 3} onClick={() => setSpeed(3)}>3× speed</button>
            <button type="button" aria-pressed={speed === 1} onClick={() => setSpeed(1)}>Real time</button>
          </div>
          <button type="button" className="btn-plain" onClick={replay}>
            Replay
          </button>
        </div>
      </div>
    </div>
  );
}

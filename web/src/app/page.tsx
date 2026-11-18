import Race from "../components/Race";
import { MODELS, REPO, REPORT, type ModelResult } from "../lib/data";

type Metric = {
  title: string;
  hint: string;
  value: (m: ModelResult) => number;
  format: (v: number) => string;
  lowerIsBetter?: boolean;
};

const METRICS: Metric[] = [
  { title: "Field accuracy", hint: "Higher is better", value: (m) => m.accuracy, format: (v) => `${v.toFixed(1)}%` },
  { title: "Tokens per second", hint: "Higher is better", value: (m) => m.tokPerSec, format: (v) => v.toFixed(1) },
  { title: "Time to first token", hint: "Lower is better", value: (m) => m.ttftMs / 1000, format: (v) => `${v.toFixed(1)} s`, lowerIsBetter: true },
  { title: "Peak memory", hint: "Lower is better", value: (m) => m.ramMb / 1024, format: (v) => `${v.toFixed(1)} GB`, lowerIsBetter: true },
];

const PIPELINE = [
  ["Define the schema", "A Pydantic JobPosting model: title, company, seniority, location, remote policy, skills, experience and salary."],
  ["Constrain the model", "The JSON Schema is passed to Ollama’s format option, so the model can only emit that shape."],
  ["Validate", "The response is parsed and checked by Pydantic before anything downstream sees it."],
  ["Retry once", "If validation fails, the model gets one more try with the exact error message in the prompt."],
  ["Fail cleanly", "Still invalid? The caller gets a structured failure object instead of broken JSON."],
];

function GitHubIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden>
      <path d="M8 0C3.58 0 0 3.58 0 8a8 8 0 0 0 5.47 7.59c.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.5 7.5 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
    </svg>
  );
}

function MetricChart({ metric }: { metric: Metric }) {
  const values = MODELS.map(metric.value);
  const max = Math.max(...values);
  const best = metric.lowerIsBetter ? Math.min(...values) : max;
  return (
    <figure className="metric">
      <figcaption>
        <span className="metric-title">{metric.title}</span>
        <span className="metric-hint">{metric.hint}</span>
      </figcaption>
      <ul>
        {MODELS.map((m) => {
          const v = metric.value(m);
          return (
            <li key={m.id} className={`bar-row model-${m.id}`}>
              <span className="bar-label">{m.name}</span>
              <span className="bar-track">
                <span className="bar" style={{ width: `${(v / max) * 100}%` }} />
              </span>
              <span className="bar-value tabular" data-best={v === best || undefined}>
                {metric.format(v)}
              </span>
            </li>
          );
        })}
      </ul>
    </figure>
  );
}

export default function Home() {
  return (
    <>
      <div className="hero-band" id="top">
      <header className="wrap topbar">
        <nav className="topnav">
          <a href="#results">Results</a>
          <a href="#how">How it works</a>
          <a href={REPO} target="_blank" rel="noreferrer" className="btn btn-light">
            <GitHubIcon /> View on GitHub
          </a>
        </nav>
      </header>

        <section className="wrap hero">
          <h1>Which local LLM should read job posts on a 16&nbsp;GB MacBook?</h1>
          <p className="lede">
            I ran llama3.2:3b, phi4-mini and mistral:7b fully offline on an Apple M4 and scored each one on turning
            35 hand-labeled job posts into validated JSON. Here is the same extraction, replayed at each
            model&rsquo;s measured speed.
          </p>
          <Race />
        </section>
      </div>

      <main>
        <section id="results" className="wrap section">
          <div className="section-head">
            <h2>Results</h2>
            <p>
              35 posts, temperature 0, same prompt for every model. All three returned valid JSON on the first
              try every time, so the differences are in accuracy, speed and memory.
            </p>
          </div>
          <div className="metrics">
            {METRICS.map((metric) => (
              <MetricChart key={metric.title} metric={metric} />
            ))}
          </div>

          <div className="verdict">
            <div className="pick model-mistral">
              <p className="pick-when">When accuracy matters</p>
              <p className="pick-model">mistral:7b</p>
              <p>Highest field accuracy at 73.9%, but it waits 11 seconds before the first token and needs 5 GB.</p>
            </div>
            <div className="pick model-llama">
              <p className="pick-when">For everyday use</p>
              <p className="pick-model">llama3.2:3b</p>
              <p>About 2.7× the tokens per second on half the memory, for roughly 6 points less accuracy.</p>
            </div>
          </div>
        </section>

        <section className="wrap section">
          <div className="section-head">
            <h2>Why temperature 0</h2>
            <p>
              I ran llama3.2:3b five times on each of three posts and checked whether the JSON came back
              identical.
            </p>
          </div>
          <div className="temps">
            {[
              { t: "0.0", match: 1.0, dis: 0.0 },
              { t: "0.7", match: 0.467, dis: 0.407 },
            ].map((row) => (
              <div key={row.t} className="temp">
                <p className="temp-t">Temperature {row.t}</p>
                <p className="temp-num tabular">{Math.round(row.match * 100)}%</p>
                <p className="temp-desc">of repeat runs returned identical JSON</p>
                <span className="temp-track">
                  <span style={{ width: `${row.match * 100}%` }} />
                </span>
                <p className="temp-sub tabular">{Math.round(row.dis * 100)}% of fields disagreed between runs</p>
              </div>
            ))}
          </div>
        </section>

        <section id="how" className="wrap section">
          <div className="section-head">
            <h2>How the extraction stays valid</h2>
            <p>Everything runs through Ollama on the laptop. Once the models are pulled, Wi-Fi can be off.</p>
          </div>
          <ol className="pipeline">
            {PIPELINE.map(([title, body]) => (
              <li key={title}>
                <p className="step-title">{title}</p>
                <p>{body}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className="wrap section run">
          <div>
            <h2>Run it yourself</h2>
            <p>
              Needs Ollama and uv. The setup script pulls all three models; after that the benchmark writes a CSV,
              charts and a Markdown report to <code>reports/</code>.
            </p>
            <div className="run-links">
              <a href={REPO} target="_blank" rel="noreferrer" className="btn btn-dark">
                <GitHubIcon /> View on GitHub
              </a>
              <a href={REPORT} target="_blank" rel="noreferrer" className="btn btn-line">
                Read the full report
              </a>
            </div>
          </div>
          <pre className="terminal">
            <code>
              <span className="prompt">$</span> uv sync{"\n"}
              <span className="prompt">$</span> uv run python scripts/setup.py{"\n"}
              <span className="prompt">$</span> make bench{"\n"}
              <span className="comment"># try the assistant</span>{"\n"}
              <span className="prompt">$</span> uv run assistant extract --file samples/sample_job.txt
            </code>
          </pre>
        </section>
      </main>

      <footer className="wrap footer">
        <p>Measured on an Apple M4 MacBook with 16 GB of unified memory, macOS 27.2.1.</p>
        <p>
          <a href={REPO} target="_blank" rel="noreferrer">Source on GitHub</a>
        </p>
      </footer>
    </>
  );
}

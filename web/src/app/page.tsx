import Image from "next/image";
import HeroArt from "../components/HeroArt";

const REPO = "https://github.com/krushaalkalkani/local-llm-benchmark";
const REPORT = `${REPO}/blob/main/reports/benchmark_report.md`;
const SITE = "https://local-llm-benchmark-krushals-projects.vercel.app";

const results = [
  {
    model: "llama3.2:3b",
    ram: "2.7 GB",
    ttft: "2,392",
    tok: "33.4",
    valid: "100%",
    acc: "68.0%",
    note: "Best daily default",
  },
  {
    model: "phi4-mini",
    ram: "3.2 GB",
    ttft: "3,757",
    tok: "24.5",
    valid: "100%",
    acc: "61.0%",
    note: "Middle weight",
  },
  {
    model: "mistral:7b",
    ram: "5.1 GB",
    ttft: "11,091",
    tok: "12.5",
    valid: "100%",
    acc: "73.9%",
    note: "Highest accuracy",
  },
];

function GitHubIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden>
      <path d="M8 0C3.58 0 0 3.58 0 8a8 8 0 0 0 5.47 7.59c.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.5 7.5 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
    </svg>
  );
}

export default function Home() {
  return (
    <main>
      {/* Top bar with actions */}
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-5 sm:px-8">
        <div className="flex items-center gap-3">
          <span className="live-dot" aria-hidden />
          <p className="mono text-[11px] tracking-[0.2em] text-[var(--mute)]">
            KRUSHAL KALKANI · LOCAL BENCH
          </p>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <a className="btn btn-ink" href={REPO} target="_blank" rel="noreferrer">
            <GitHubIcon />
            GitHub
          </a>
          <a className="btn btn-outline" href={REPORT} target="_blank" rel="noreferrer">
            Full report
          </a>
        </div>
      </div>

      {/* HERO — one full-bleed stage */}
      <section className="mx-auto max-w-6xl px-5 sm:px-8">
        <div className="hero-stage">
          <HeroArt />
          <div className="relative z-10 flex h-full min-h-[min(88vh,820px)] flex-col justify-end p-6 sm:p-10 lg:max-w-[58%] lg:justify-center lg:p-14">
            <p className="rise mono text-[11px] tracking-[0.24em] text-[var(--lime)]">
              OFFLINE · APPLE M4 · 16 GB
            </p>
            <h1 className="rise-2 mt-4 text-[clamp(3.4rem,10vw,6.4rem)] font-bold leading-[0.9] tracking-[-0.05em]">
              LOCAL
              <br />
              BENCH
            </h1>
            <p className="rise-3 mt-5 max-w-md text-lg leading-snug text-[#d7d3c8] sm:text-xl">
              Measured offline. Picked with data — not vibes.
            </p>
            <p className="rise-3 mt-3 max-w-md text-sm leading-relaxed text-[#9aa39a]">
              Private Ollama assistant: messy job posts → validated JSON, then a
              rigorous 3-model bake-off on one Mac.
            </p>
            <div className="rise-3 mt-8 flex flex-wrap gap-3">
              <a className="btn btn-lime" href="#results">
                See the numbers
              </a>
              <a className="btn btn-ghost" href={REPO} target="_blank" rel="noreferrer">
                <GitHubIcon />
                Star on GitHub
              </a>
              <a className="btn btn-ghost" href={REPORT} target="_blank" rel="noreferrer">
                Read report
              </a>
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-6xl px-5 pb-24 sm:px-8">
        {/* SYSTEM */}
        <section className="section">
          <p className="section-kicker">01 · What you get</p>
          <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight sm:text-5xl">
            A private assistant that refuses broken JSON.
          </h2>
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-[var(--mute)]">
            Schema-constrained Ollama output. Pydantic validation. One retry with
            the error message. Clean failure object if it still fails. Wi-Fi can
            be off after models are pulled.
          </p>
          <div className="mt-10 grid gap-6 sm:grid-cols-3">
            {[
              ["Chat + API", "CLI streaming and FastAPI /chat with TTFT + tok/s"],
              ["Extract", "JobPosting schema · format=JSON · single retry"],
              ["Bench", "35 labeled prompts · 3 models · charts + recommendation"],
            ].map(([title, body]) => (
              <div key={title} className="stat-block">
                <p className="text-xl font-semibold">{title}</p>
                <p className="mt-2 text-[var(--mute)]">{body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* RESULTS */}
        <section id="results" className="section">
          <p className="section-kicker">02 · The bake-off</p>
          <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight sm:text-5xl">
            35 prompts. Three models. One machine.
          </h2>
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-[var(--mute)]">
            Temperature 0.0. Every model hit 100% first-try JSON validity. Accuracy
            is where they split.
          </p>

          <div className="table-wrap mt-10">
            <table>
              <thead>
                <tr>
                  <th>Model</th>
                  <th>Peak RAM</th>
                  <th>TTFT</th>
                  <th>Tok/s</th>
                  <th>JSON</th>
                  <th>Field acc.</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {results.map((row) => (
                  <tr key={row.model}>
                    <td className="font-semibold">{row.model}</td>
                    <td className="mono">{row.ram}</td>
                    <td className="mono">{row.ttft} ms</td>
                    <td className="mono">{row.tok}</td>
                    <td className="mono">{row.valid}</td>
                    <td className="mono font-semibold text-[var(--ok)]">{row.acc}</td>
                    <td className="mono text-xs text-[var(--mute)]">{row.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {[
              ["/charts/chart_speed.png", "Speed"],
              ["/charts/chart_quality.png", "Quality"],
              ["/charts/chart_memory.png", "Memory"],
            ].map(([src, label]) => (
              <figure key={src} className="border border-[var(--ink)] bg-white/50 p-3">
                <Image
                  src={src}
                  alt={`${label} chart`}
                  width={800}
                  height={450}
                  className="h-auto w-full"
                />
                <figcaption className="mono mt-3 text-xs tracking-wide text-[var(--mute)]">
                  {label}
                </figcaption>
              </figure>
            ))}
          </div>
        </section>

        {/* TEMP */}
        <section className="section">
          <p className="section-kicker">03 · Temperature study</p>
          <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight sm:text-5xl">
            Same prompt. Different chaos.
          </h2>
          <div className="mt-10 grid gap-8 sm:grid-cols-2">
            <div className="border border-[var(--ink)] bg-[var(--steel)] p-6 text-[#f4f2ec]">
              <p className="mono text-xs tracking-[0.18em] text-[var(--lime)]">TEMP 0.0</p>
              <p className="mt-4 text-5xl font-bold tracking-tight">1.000</p>
              <p className="mt-2 text-[#b7b3a8]">exact match across runs</p>
              <p className="mono mt-4 text-sm text-[#9aa39a]">field disagreement 0.000</p>
            </div>
            <div className="border border-[var(--ink)] bg-[var(--bg-2)] p-6">
              <p className="mono text-xs tracking-[0.18em] text-[var(--mute)]">TEMP 0.7</p>
              <p className="mt-4 text-5xl font-bold tracking-tight">0.467</p>
              <p className="mt-2 text-[var(--mute)]">exact match across runs</p>
              <p className="mono mt-4 text-sm text-[var(--mute)]">field disagreement 0.407</p>
            </div>
          </div>
        </section>

        {/* DECISION + CTA */}
        <section className="section">
          <p className="section-kicker">04 · Call</p>
          <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight sm:text-5xl">
            Accuracy wants mistral. Speed wants llama.
          </h2>
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-[var(--mute)]">
            On this M4 / 16GB machine: pick <strong className="text-[var(--ink)]">mistral:7b</strong> when
            field quality matters, or <strong className="text-[var(--ink)]">llama3.2:3b</strong> when you
            want ~2.7× tokens/sec and half the RAM.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <a className="btn btn-lime" href={REPO} target="_blank" rel="noreferrer">
              <GitHubIcon />
              Open GitHub repo
            </a>
            <a className="btn btn-ink" href={REPORT} target="_blank" rel="noreferrer">
              Open benchmark report
            </a>
            <a className="btn btn-outline" href="#results">
              Back to numbers
            </a>
          </div>
          <p className="mono mt-8 text-sm text-[var(--mute)]">
            Reproduce locally → <span className="text-[var(--ink)]">make bench</span>
          </p>
        </section>

        <footer className="mt-24 border-t border-[var(--line)] pt-8 text-sm text-[var(--mute)]">
          <p className="mono text-[11px] tracking-[0.16em]">
            ONE PROJECT · ONE SITE · {SITE.replace("https://", "")}
          </p>
          <p className="mt-3 max-w-xl">
            Apple M4 · 16 GB · macOS 27.2.1 · Fully offline after model pull.
          </p>
        </footer>
      </div>
    </main>
  );
}

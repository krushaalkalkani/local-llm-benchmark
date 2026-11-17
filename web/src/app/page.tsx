import Image from "next/image";
import HeroArt from "../components/HeroArt";

const REPO = "https://github.com/krushaalkalkani/local-llm-benchmark";

const results = [
  {
    model: "llama3.2:3b",
    ram: "2.7 GB",
    ttft: "2392",
    tok: "33.4",
    valid: "100%",
    acc: "68.0%",
  },
  {
    model: "phi4-mini",
    ram: "3.2 GB",
    ttft: "3757",
    tok: "24.5",
    valid: "100%",
    acc: "61.0%",
  },
  {
    model: "mistral:7b",
    ram: "5.1 GB",
    ttft: "11091",
    tok: "12.5",
    valid: "100%",
    acc: "73.9%",
  },
];

export default function Home() {
  return (
    <main className="mx-auto max-w-6xl px-5 pb-24 pt-8 sm:px-8">
      <header className="mb-10 flex items-baseline justify-between gap-4">
        <p className="mono text-xs tracking-[0.22em] text-[var(--muted)]">
          KRUSHAL KALKANI · AI/ML
        </p>
        <a
          href={REPO}
          className="mono text-xs tracking-wide text-[var(--forest)] underline-offset-4 hover:underline"
        >
          GitHub
        </a>
      </header>

      {/* HERO — one composition */}
      <section className="grid min-h-[78vh] grid-cols-1 items-stretch gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:gap-12">
        <div className="flex flex-col justify-center">
          <h1 className="animate-rise font-semibold tracking-[-0.04em] text-[clamp(3.2rem,9vw,5.6rem)] leading-[0.92] text-[var(--ink)]">
            LOCAL
            <br />
            BENCH
          </h1>
          <p className="animate-rise-delay mt-6 max-w-md text-xl font-medium leading-snug text-[var(--forest-deep)] sm:text-2xl">
            Measured offline. Picked with data.
          </p>
          <p className="animate-rise-delay-2 mt-4 max-w-md text-base leading-relaxed text-[var(--muted)]">
            A private Ollama assistant that turns messy job posts into validated
            JSON — then benchmarks three small models on an Apple M4.
          </p>
          <div className="animate-rise-delay-2 mt-8 flex flex-wrap gap-3">
            <a
              href="#results"
              className="bg-[var(--forest)] px-5 py-3 text-sm font-semibold text-[var(--paper)] transition hover:bg-[var(--forest-deep)]"
            >
              See the numbers
            </a>
            <a
              href={REPO}
              className="border border-[var(--ink)] px-5 py-3 text-sm font-semibold text-[var(--ink)] transition hover:bg-[var(--ink)] hover:text-[var(--paper)]"
            >
              View source
            </a>
          </div>
        </div>
        <div className="animate-rise-delay min-h-[340px]">
          <HeroArt />
        </div>
      </section>

      {/* WHAT IT DOES */}
      <section className="mt-28 border-t border-[var(--line)] pt-14">
        <p className="mono text-xs tracking-[0.2em] text-[var(--muted)]">01 · SYSTEM</p>
        <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight sm:text-4xl">
          Job text in. Structured truth out. No cloud API.
        </h2>
        <p className="mt-5 max-w-2xl text-lg leading-relaxed text-[var(--muted)]">
          Paste a messy posting. Ollama returns JSON constrained by schema.
          Pydantic validates it. One automatic retry on failure. If it still
          fails, you get a clean error object — never broken JSON.
        </p>
        <div className="mono mt-10 grid gap-6 border border-[var(--line)] bg-[var(--panel)] p-6 text-sm leading-7 sm:grid-cols-3">
          <p>
            <span className="block text-[var(--muted)]">Runtime</span>
            Ollama · Python · Typer · FastAPI
          </p>
          <p>
            <span className="block text-[var(--muted)]">Guardrails</span>
            JSON Schema format + Pydantic v2
          </p>
          <p>
            <span className="block text-[var(--muted)]">Metrics</span>
            TTFT · tok/s · latency · memory
          </p>
        </div>
      </section>

      {/* RESULTS */}
      <section id="results" className="mt-28 border-t border-[var(--line)] pt-14">
        <p className="mono text-xs tracking-[0.2em] text-[var(--muted)]">02 · BENCHMARK</p>
        <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight sm:text-4xl">
          Same 35 prompts. Three models. One Mac.
        </h2>
        <p className="mt-5 max-w-2xl text-lg leading-relaxed text-[var(--muted)]">
          Temperature 0.0. Field accuracy mixes exact/soft scalar match with F1
          on skill lists. All three hit 100% first-try JSON validity.
        </p>

        <div className="mt-10 overflow-x-auto border border-[var(--line)]">
          <table className="w-full min-w-[640px] border-collapse text-left text-sm">
            <thead className="bg-[var(--paper-2)]">
              <tr className="mono text-xs tracking-wide text-[var(--muted)]">
                <th className="px-4 py-3 font-medium">Model</th>
                <th className="px-4 py-3 font-medium">Peak RAM</th>
                <th className="px-4 py-3 font-medium">TTFT (ms)</th>
                <th className="px-4 py-3 font-medium">Tokens/s</th>
                <th className="px-4 py-3 font-medium">JSON valid</th>
                <th className="px-4 py-3 font-medium">Field acc.</th>
              </tr>
            </thead>
            <tbody>
              {results.map((row) => (
                <tr key={row.model} className="border-t border-[var(--line)]">
                  <td className="px-4 py-3 font-semibold">{row.model}</td>
                  <td className="mono px-4 py-3">{row.ram}</td>
                  <td className="mono px-4 py-3">{row.ttft}</td>
                  <td className="mono px-4 py-3">{row.tok}</td>
                  <td className="mono px-4 py-3">{row.valid}</td>
                  <td className="mono px-4 py-3 text-[var(--forest)]">{row.acc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-12 grid gap-10 md:grid-cols-3">
          {[
            { src: "/charts/chart_speed.png", alt: "Tokens per second by model" },
            { src: "/charts/chart_quality.png", alt: "Quality rates by model" },
            { src: "/charts/chart_memory.png", alt: "Peak memory by model" },
          ].map((chart) => (
            <figure key={chart.src} className="border border-[var(--line)] bg-white/40 p-3">
              <Image
                src={chart.src}
                alt={chart.alt}
                width={800}
                height={450}
                className="h-auto w-full"
              />
              <figcaption className="mono mt-3 text-xs text-[var(--muted)]">
                {chart.alt}
              </figcaption>
            </figure>
          ))}
        </div>
      </section>

      {/* TEMPERATURE */}
      <section className="mt-28 border-t border-[var(--line)] pt-14">
        <p className="mono text-xs tracking-[0.2em] text-[var(--muted)]">03 · DETERMINISM</p>
        <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight sm:text-4xl">
          Temperature is not a vibe setting.
        </h2>
        <p className="mt-5 max-w-2xl text-lg leading-relaxed text-[var(--muted)]">
          Same jobs, five runs each. At 0.0 the JSON matched every time. At 0.7,
          exact-match collapsed and fields disagreed.
        </p>
        <div className="mt-10 grid gap-8 sm:grid-cols-2">
          <div className="border-l-2 border-[var(--forest)] pl-5">
            <p className="mono text-xs text-[var(--muted)]">TEMP 0.0</p>
            <p className="mt-2 text-4xl font-semibold tracking-tight">1.000</p>
            <p className="mt-1 text-[var(--muted)]">run-to-run exact match</p>
            <p className="mono mt-3 text-sm">field disagreement 0.000</p>
          </div>
          <div className="border-l-2 border-[var(--signal)] pl-5">
            <p className="mono text-xs text-[var(--muted)]">TEMP 0.7</p>
            <p className="mt-2 text-4xl font-semibold tracking-tight">0.467</p>
            <p className="mt-1 text-[var(--muted)]">run-to-run exact match</p>
            <p className="mono mt-3 text-sm">field disagreement 0.407</p>
          </div>
        </div>
      </section>

      {/* PICK */}
      <section className="mt-28 border-t border-[var(--line)] pt-14">
        <p className="mono text-xs tracking-[0.2em] text-[var(--muted)]">04 · DECISION</p>
        <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight sm:text-4xl">
          On this M4 laptop, the pick depends on the constraint.
        </h2>
        <p className="mt-5 max-w-2xl text-lg leading-relaxed text-[var(--muted)]">
          <span className="font-semibold text-[var(--ink)]">mistral:7b</span> wins
          field accuracy (73.9%).{" "}
          <span className="font-semibold text-[var(--ink)]">llama3.2:3b</span> is
          the better daily default — about 2.7× faster tokens and half the RAM,
          with only ~6 points less accuracy.
        </p>
        <p className="mono mt-8 text-sm text-[var(--muted)]">
          Reproduce: <span className="text-[var(--ink)]">make bench</span>
        </p>
      </section>

      <footer className="mt-28 border-t border-[var(--line)] pt-8 text-sm text-[var(--muted)]">
        <p className="mono text-xs tracking-[0.16em]">
          HARDWARE · Apple M4 · 16 GB · macOS 27.2.1 · arm64
        </p>
        <p className="mt-3 max-w-xl">
          Built to show local inference trade-offs with receipts — not vibes.
          Source and full markdown report live in the repository.
        </p>
        <p className="mt-6">
          <a href={REPO} className="text-[var(--forest)] underline-offset-4 hover:underline">
            github.com/krushaalkalkani/local-llm-benchmark
          </a>
        </p>
      </footer>
    </main>
  );
}

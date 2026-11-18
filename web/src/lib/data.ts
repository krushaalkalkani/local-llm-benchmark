export const REPO = "https://github.com/krushaalkalkani/local-llm-benchmark";
export const REPORT = `${REPO}/blob/main/reports/benchmark_report.md`;

export type ModelId = "llama" | "phi" | "mistral";

export type ModelResult = {
  id: ModelId;
  name: string;
  ramMb: number;
  ttftMs: number;
  tokPerSec: number;
  jsonValid: number;
  accuracy: number;
};

// From reports/benchmark_report.md — Apple M4, 16 GB, 35 prompts, temperature 0.0
export const MODELS: ModelResult[] = [
  { id: "llama", name: "llama3.2:3b", ramMb: 2662, ttftMs: 2392, tokPerSec: 33.4, jsonValid: 100, accuracy: 68.0 },
  { id: "phi", name: "phi4-mini", ramMb: 3174, ttftMs: 3757, tokPerSec: 24.5, jsonValid: 100, accuracy: 61.0 },
  { id: "mistral", name: "mistral:7b", ramMb: 5120, ttftMs: 11091, tokPerSec: 12.5, jsonValid: 100, accuracy: 73.9 },
];

// jd_001 from bench/prompts/jobs.jsonl
export const SAMPLE_POST =
  "Senior Python Engineer at Acme Corp — San Francisco, CA (Hybrid). 5+ years experience. Required: Python, FastAPI, PostgreSQL, AWS. Nice to have: Kubernetes, Terraform. Salary $150k–$180k USD/year.";

export const SAMPLE_JSON = JSON.stringify(
  {
    title: "Senior Python Engineer",
    company: "Acme Corp",
    seniority: "senior",
    location: "San Francisco, CA",
    remote: "hybrid",
    required_skills: ["Python", "FastAPI", "PostgreSQL", "AWS"],
    nice_to_have_skills: ["Kubernetes", "Terraform"],
    years_experience: 5,
    salary: { min_amount: 150000, max_amount: 180000, currency: "USD", period: "year" },
  },
  null,
  2,
);

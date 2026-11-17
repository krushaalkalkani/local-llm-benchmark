.PHONY: bench extract-sample setup

setup:
	uv sync
	uv run python scripts/setup.py

# Full Phase 3 benchmark: run all models × eval set, then write report + charts.
bench:
	uv sync
	uv run python -m bench.run_bench
	uv run python -m bench.report

extract-sample:
	uv run assistant extract --file samples/sample_job.txt

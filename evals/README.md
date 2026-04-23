# Eval Harness

This directory contains the shared eval harness metadata and reports.

- `suites.manifest.json`: default suite definition and required pass threshold.
- includes safety domain coverage for `air-traffic-mini` constrained decision paths.
- `reports/`: generated run reports from `scripts/run_evals.py`.
- category folders (`scenarios/`, `regression/`, `safety/`, `benchmarks/`) are reserved for future case expansion.

Run the suite with:

```bash
make evals
```

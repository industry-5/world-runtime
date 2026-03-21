# Developer Quickstart

This guide is the fastest path from clone to confidence for contributors and evaluators working from the repo.

For repo context and first-read orientation, start at [`README.md`](../README.md).

## Prerequisites

- Python `3.10+`
- `pip`/`pip3`
- Repository checked out locally

Install developer dependencies:

```bash
make install
```

## First Successful Run

Run this path first:

```bash
make install
make validate
make workflow-quickstart
```

Optional API/SDK smoke path:

```bash
make api-server
make sdk-example
```

Optional showcase demo path:

```bash
python3 -m api.http_server --host 127.0.0.1 --port 8080
python3 labs/world_game_studio_next/server.py --host 127.0.0.1 --port 8093 --upstream http://127.0.0.1:8080
```

Expected outcomes:

- `make validate` passes the schema + test baseline.
- `make workflow-quickstart` produces a reasoning summary and draft proposal.
- API/SDK smoke path returns a session and policy result.
- Studio Next demo path opens the primary showcase surface backed by `adapters/world_game` runtime methods.

## What To Run Next

Use this path when you are moving beyond the first smoke run:

1. Install dependencies: `make install`
2. Baseline confidence: `make validate`
3. Behavior and fixture checks as needed: `make examples`, `make adapters`, `make evals`
4. Compatibility checks when touching protocol/API surfaces: `make protocol-compat`, `make public-api-compat`
5. Full RC gate before merge or release-critical changes: `make m25-validate`

## Task-to-Command Map

| If you need to... | Run |
| --- | --- |
| Install dependencies | `make install` |
| Run schema + tests baseline | `make validate` |
| Run test suite only | `make test` |
| Run eval harness | `make evals` |
| Run operator quickstart workflow | `make workflow-quickstart` |
| Run proposal-review workflow | `make workflow-proposal` |
| Run simulation-analysis workflow | `make workflow-simulation` |
| Run failure-recovery workflow | `make workflow-failure` |
| Check protocol compatibility | `make protocol-compat` |
| Check public API + SDK compatibility | `make public-api-compat` |
| Validate extension contracts | `make extension-contracts` |
| Validate connector adapters/plugins | `make connectors` and `make connector-plugins` |
| Run full RC gate | `make m25-validate` |

For the complete command surface, see [`Makefile`](../Makefile).

## Troubleshooting and Recovery

### Dependency install failures

- Confirm Python version: `python3 --version`
- Retry install: `make install`
- If environment is stale, clear caches and reinstall:
  - `make clean`
  - `make install`

### Schema/test baseline failures (`make validate`)

- Isolate schema failures: `make schemas`
- Isolate tests: `make test-verbose`
- Re-run baseline after fixes: `make validate`

### Eval harness failures (`make evals`)

- Re-run with clean baseline first: `make validate`
- Check adapter/domain-specific constraints with targeted runs (for example `make air-traffic-evals`)
- Re-run full evals after fixing scenario/adapter regressions: `make evals`

## Read Next

- Architecture: [`ARCHITECTURE.md`](../ARCHITECTURE.md)
- Showcase walkthrough: [`playbooks/world-game-studio-next-demo.md`](../playbooks/world-game-studio-next-demo.md)
- Operator workflows: [`playbooks/operator-quickstart.md`](../playbooks/operator-quickstart.md)
- Observability diagnostics: [`playbooks/operator-observability-diagnostics.md`](../playbooks/operator-observability-diagnostics.md)
- Extension contracts: [`docs/EXTENSION_CONTRACTS.md`](./EXTENSION_CONTRACTS.md)
- Partner extension onboarding: [`docs/PARTNER_ONBOARDING.md`](./PARTNER_ONBOARDING.md)
- Compatibility matrix: [`docs/COMPATIBILITY_MATRIX.md`](./COMPATIBILITY_MATRIX.md)

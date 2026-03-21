# World Runtime

World Runtime is a v1.0 release-candidate runtime and build harness for systems built around:

- explicit world state
- append-only events
- deterministic state projection
- simulation of possible futures
- policy-driven orchestration
- agent-facing runtime interfaces

This repository is intentionally harness-first and repo-first so operators, contributors, and coding agents can inspect, validate, and evolve the runtime safely.

## Current status

As of 2026-03-09 (America/Chicago), the repository is at v1.0 release-candidate gate completion (M25).

- Runtime package version file: `0.1.0`
- Latest tagged release candidate: `v1.0.0-rc.1` (dated 2026-03-09)
- Latest release milestone notes: [`CHANGELOG.md`](CHANGELOG.md)
- Detailed implementation and evidence status: [`STATUS.md`](STATUS.md)
- RC go/no-go criteria and gate matrix: [`docs/RELEASE_READINESS_CHECKLIST.md`](docs/RELEASE_READINESS_CHECKLIST.md)

## Core concepts

- World graph: entities, relationships, and projected state
- Event engine: append-only event history
- Projection engine: deterministic state rebuild from events
- Policy engine: explicit guardrails and approval boundaries
- Simulation engine: isolated what-if scenario branches
- Reasoning layer: LLM-assisted interpretation and proposal generation
- App Server: stable runtime surface for tools and clients

For architecture depth, see [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Quickstart (first run)

Canonical contributor onboarding guide:
[`docs/developer-quickstart.md`](docs/developer-quickstart.md)

```bash
make install
make validate
make workflow-quickstart
make evals
make m25-validate
```

## Command groups

### Validate runtime

- `make validate`
- `make evals`
- `make protocol-compat`
- `make public-api-compat`
- `make m25-validate`

### Run operator workflows

- `make workflow-quickstart`
- `make workflow-proposal`
- `make workflow-simulation`
- `make workflow-failure`

### Deploy, integration stacks, and connectors

- `make deploy-local`
- `make deploy-dev`
- `make integration-stacks`
- `make connectors`
- `make connector-plugins`

### Public API and SDK

- `make api-server`
- `make sdk-example`
- API contract: [`api/PUBLIC_API_V1.md`](api/PUBLIC_API_V1.md)
- SDK usage: [`sdk/README.md`](sdk/README.md)

For the complete command surface, see [`Makefile`](Makefile).

## Where to go next

- Contributor onboarding (canonical): [`docs/developer-quickstart.md`](docs/developer-quickstart.md)
- Operator workflows: [`playbooks/operator-quickstart.md`](playbooks/operator-quickstart.md), [`playbooks/`](playbooks/)
- API and SDK integration: [`api/PUBLIC_API_V1.md`](api/PUBLIC_API_V1.md), [`sdk/README.md`](sdk/README.md)
- Extension partner onboarding: [`docs/EXTENSION_CONTRACTS.md`](docs/EXTENSION_CONTRACTS.md), [`docs/PARTNER_ONBOARDING.md`](docs/PARTNER_ONBOARDING.md), [`docs/COMPATIBILITY_MATRIX.md`](docs/COMPATIBILITY_MATRIX.md)
- Architecture and system model: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Reference deployment workflows: [`playbooks/reference-deployment-local.md`](playbooks/reference-deployment-local.md), [`playbooks/reference-deployment-dev.md`](playbooks/reference-deployment-dev.md)
- Observability and diagnostics: `make observability`, `make provenance-audit`, [`playbooks/operator-observability-diagnostics.md`](playbooks/operator-observability-diagnostics.md)
- Product direction and milestone sequencing: [`ROADMAP.md`](ROADMAP.md)

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

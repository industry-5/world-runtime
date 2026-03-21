# World Runtime

_Last updated: 2026-03-12 (America/Chicago)_

World Runtime is a harness-first runtime and build repo for systems built around explicit world state, append-only events, deterministic projection, simulation of possible futures, policy-governed orchestration, and agent-facing runtime interfaces.

The repository is intentionally repo-native and agent-runnable: operators, contributors, and coding agents should be able to inspect it, validate it, and extend it without relying on hidden context.

World Runtime is a product of **INDUSTRY 5, Inc.**

## What This Is

World Runtime is for teams building systems that need:

- explicit world state
- append-only event history
- deterministic replay and projection
- policy-governed decisions
- simulation before action

It is best suited for operator-facing, agent-facing, and governance-heavy systems where consequences cascade and decisions need evidence.

## Stability And Support

- Current release posture: **v1.0 release candidate**
- Stable/support-committed surfaces: App Server protocol, Public API `/v1`, Python SDK starter, persistence migrations, and extension contracts documented in the compatibility/support docs
- Experimental surfaces: `labs/`, showcase assets, and any repo area described as draft, starter, or exploratory
- Public support posture: **best-effort**
- Public collaboration posture: **Issues enabled, PRs welcome**

Maintainers may decline features or changes that do not fit project direction, support capacity, or release posture.

## Current Release Posture

- Milestone state: **M0-M25 complete**
- Current phase: **v1.0 release candidate**
- Current tagged release candidate: `v1.0.0-rc.1` (2026-03-09)
- Repository package version file: `VERSION` -> `1.0.0-rc.1`
- Versioning note: the repository version file and the tagged release candidate are aligned for the public RC phase.

For release evidence and operational status, see [STATUS.md](STATUS.md), [CHANGELOG.md](CHANGELOG.md), and [docs/RELEASE_READINESS_CHECKLIST.md](docs/RELEASE_READINESS_CHECKLIST.md).

## Start Here

If you are...

- Building or contributing: start with [docs/developer-quickstart.md](docs/developer-quickstart.md)
- Operating the runtime: start with [playbooks/operator-quickstart.md](playbooks/operator-quickstart.md)
- Integrating through supported surfaces: start with [api/PUBLIC_API_V1.md](api/PUBLIC_API_V1.md) and [sdk/README.md](sdk/README.md)
- Extending the runtime with adapters/plugins: start with [docs/EXTENSION_CONTRACTS.md](docs/EXTENSION_CONTRACTS.md) and [docs/PARTNER_ONBOARDING.md](docs/PARTNER_ONBOARDING.md)
- Trying to understand the overall documentation surface: start with [docs/README.md](docs/README.md)

## Quick Command Bundle

```bash
make install
make validate
make workflow-quickstart
make evals
make m25-validate
```

Use these more targeted commands as needed:

- Runtime validation: `make test`, `make validate`, `make protocol-compat`, `make public-api-compat`
- Operator workflows: `make workflow-quickstart`, `make workflow-proposal`, `make workflow-simulation`, `make workflow-failure`
- Deployments and integrations: `make deploy-local`, `make deploy-dev`, `make integration-stacks`, `make connectors`, `make connector-plugins`
- Public API and SDK smoke path: `make api-server`, `make sdk-example`

For the full command surface, see [Makefile](Makefile).

## First Successful Run

If you are evaluating the repo for the first time, start here:

```bash
make install
make validate
make workflow-quickstart
```

If you want the supported external integration path after that:

```bash
make api-server
make sdk-example
```

## Core Concepts

- World graph: entities, relationships, and projected state
- Event engine: append-only event history
- Projection engine: deterministic state rebuild from events
- Policy engine: explicit guardrails and approval boundaries
- Simulation engine: isolated what-if scenario branches
- Reasoning layer: LLM-assisted interpretation and proposal generation
- App Server: stable runtime surface for tools and clients

For the full system model, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Docs Map

- Docs hub: [docs/README.md](docs/README.md)
- Status snapshot and evidence: [STATUS.md](STATUS.md)
- Release narrative: [CHANGELOG.md](CHANGELOG.md)
- Strategic roadmap and milestone history: [ROADMAP.md](ROADMAP.md)
- Operator runbooks: [playbooks/](playbooks/)
- API and SDK: [api/PUBLIC_API_V1.md](api/PUBLIC_API_V1.md), [sdk/README.md](sdk/README.md)
- Extension docs: [docs/EXTENSION_CONTRACTS.md](docs/EXTENSION_CONTRACTS.md), [docs/COMPATIBILITY_MATRIX.md](docs/COMPATIBILITY_MATRIX.md), [docs/PARTNER_ONBOARDING.md](docs/PARTNER_ONBOARDING.md)

## Repository Map

- `core/`: runtime kernel, policy, simulation, reasoning, connectors, observability
- `api/`: supported external HTTP/API surface
- `adapters/`: domain adapters and domain-local package docs
- `playbooks/`: action-oriented operator and release runbooks
- `docs/`: contributor, partner, compatibility, support, and release docs
- `examples/`: fixtures, scenarios, clients, and authoring examples
- `labs/`: experimental and prototype clients, runnable demos, and exploratory tooling; not part of the stable support commitment unless stated otherwise

## Domain Package Rollup

- The root docs track only rollup state for domain packages.
- The most active domain package today is `adapter-world-game`, whose detailed package history lives in [adapters/world_game/ROADMAP.md](adapters/world_game/ROADMAP.md) and [adapters/world_game/STATUS.md](adapters/world_game/STATUS.md).
- `world_game_few` remains the compatibility/demo surface while `adapter-world-game` carries richer package-local planning and authoring flows.

## Community And Help

- For contribution expectations, see [CONTRIBUTING.md](CONTRIBUTING.md)
- For support posture and stable vs experimental surfaces, see [docs/SUPPORT_POLICY.md](docs/SUPPORT_POLICY.md)
- For security reporting, see [SECURITY.md](SECURITY.md)
- For maintainer/community workflow expectations, see [docs/MAINTAINER_TRIAGE.md](docs/MAINTAINER_TRIAGE.md)

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

# World Runtime

_Last updated: 2026-03-23 (America/Chicago)_

World Runtime is a runtime and build repo for systems that need explicit world state, append-only events, deterministic replay, simulation before action, and policy-governed decisions.

It is built for teams creating operator-facing, governance-heavy, or agent-facing systems where consequences cascade and decisions need evidence.

The repository is intentionally repo-native and agent-runnable: operators, contributors, and coding agents should be able to inspect it, validate it, and extend it without hidden context.

World Runtime is a product of **INDUSTRY 5, Inc.**

## What It Helps You Build

World Runtime is a good fit when you need:

- explicit world state
- append-only event history
- deterministic replay and projection
- policy-governed decisions
- simulation before action

The public domain adapter scenario program currently centers on:

- implemented standalone public proof paths:
  - `adapter-supply-network`
  - `adapter-air-traffic`
  - `adapter-semantic-system`
  - `adapter-power-grid`
  - `adapter-city-ops`
  - `adapter-lab-science`
  - `adapter-market-micro`
  - `adapter-multiplayer-game`
  - `adapter-autonomous-vehicle`
  - `adapter-multi-agent-ai`
  - `adapter-open-agent-world`
- implemented overlay track under `adapters/`:
  - `adapter-digital-twin` (host-bound across `power_grid` and `city_ops`)

The public export also keeps the wider runtime, API, SDK starter, examples, schemas, scripts, tests, and selected operator/developer docs so the repository remains runnable and inspectable.

## What Is Stable

- Current release posture: **v1.0 GA**
- Stable/support-committed surfaces: App Server protocol, Public API `/v1`, Python SDK starter, persistence migrations, and extension contracts
- Experimental surfaces: starter/example materials and any adapter track not explicitly promoted
- Public support posture: **best-effort**
- Public collaboration posture: **Issues enabled, PRs welcome**

Maintainers may decline features or changes that do not fit project direction, support capacity, or release posture.

For the detailed compatibility and support posture, see [docs/SUPPORT_POLICY.md](docs/SUPPORT_POLICY.md).

## Start Here

If you are evaluating the repo for the first time:

```bash
make install
make validate
make workflow-quickstart
```

If you want the supported HTTP and SDK path after that:

```bash
make api-server
make sdk-example
```

If you are...

- Evaluating the public adapter portfolio: start with [docs/what-you-can-build.md](docs/what-you-can-build.md) and [adapters/README.md](adapters/README.md)
- Building or contributing: start with [docs/developer-quickstart.md](docs/developer-quickstart.md)
- Operating the runtime: start with [playbooks/operator-quickstart.md](playbooks/operator-quickstart.md)
- Integrating through supported surfaces: start with [api/PUBLIC_API_V1.md](api/PUBLIC_API_V1.md) and [sdk/README.md](sdk/README.md)
- Extending the runtime: start with [docs/EXTENSION_CONTRACTS.md](docs/EXTENSION_CONTRACTS.md) and [docs/PARTNER_ONBOARDING.md](docs/PARTNER_ONBOARDING.md)
- Exploring the public adapter portfolio: start with [docs/what-you-can-build.md](docs/what-you-can-build.md) and [adapters/README.md](adapters/README.md)

## Core Concepts

- World graph: entities, relationships, and projected state
- Event engine: append-only event history
- Projection engine: deterministic state rebuild from events
- Policy engine: explicit guardrails and approval boundaries
- Simulation engine: isolated what-if scenario branches
- Reasoning layer: LLM-assisted interpretation and proposal generation
- App Server: stable runtime surface for tools and clients

For the full system model, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Release Snapshot

- Current phase: **v1.0 GA**
- Current release: `v1.0.0` (2026-03-22)
- Repository package version: `VERSION` -> `1.0.0`

## Docs Map

- Docs hub: [docs/README.md](docs/README.md)
- Public adapter portfolio narrative: [docs/what-you-can-build.md](docs/what-you-can-build.md)
- Adapter portfolio overview: [adapters/README.md](adapters/README.md)
- Operator runbooks: [playbooks/](playbooks/)
- API and SDK: [api/PUBLIC_API_V1.md](api/PUBLIC_API_V1.md), [sdk/README.md](sdk/README.md)
- Extension docs: [docs/EXTENSION_CONTRACTS.md](docs/EXTENSION_CONTRACTS.md), [docs/COMPATIBILITY_MATRIX.md](docs/COMPATIBILITY_MATRIX.md), [docs/PARTNER_ONBOARDING.md](docs/PARTNER_ONBOARDING.md)

## Repository Map

- `core/`: runtime kernel, policy, simulation, reasoning, connectors, observability
- `api/`: supported external HTTP/API surface
- `adapters/`: public domain adapter program docs plus package-local package docs
- `playbooks/`: action-oriented operator and release runbooks
- `docs/`: contributor, partner, compatibility, support, and release docs
- `examples/`: fixtures, scenarios, clients, and authoring examples

## Community And Help

- For contribution expectations, see [CONTRIBUTING.md](CONTRIBUTING.md)
- For support posture and stable vs experimental surfaces, see [docs/SUPPORT_POLICY.md](docs/SUPPORT_POLICY.md)
- For security reporting, see [SECURITY.md](SECURITY.md)
- For maintainer/community workflow expectations, see [docs/MAINTAINER_TRIAGE.md](docs/MAINTAINER_TRIAGE.md)

Internal build-process files such as roadmap ledgers, changelogs, and thread handoff prompts are intentionally omitted from this public export.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

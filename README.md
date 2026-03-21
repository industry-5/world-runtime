# World Runtime

_Last updated: 2026-03-14 (America/Chicago)_

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

Representative public examples in this repo include:

- `adapter-supply-network` for disruption, replay, and operator workflows
- `adapter-air-traffic` for safety-constrained decisions
- the World Game showcase stack:
  - `labs/world_game_studio_next` as the primary showcase and demo surface
  - `adapters/world_game` as the domain/runtime source of truth behind that experience

## What Is Stable

- Current release posture: **v1.0 release candidate**
- Stable/support-committed surfaces: App Server protocol, Public API `/v1`, Python SDK starter, persistence migrations, and extension contracts
- Experimental surfaces: `labs/`, showcase/storytelling assets, and starter/example materials unless explicitly promoted
- Public support posture: **best-effort**
- Public collaboration posture: **Issues enabled, PRs welcome**

Maintainers may decline features or changes that do not fit project direction, support capacity, or release posture.

For the detailed compatibility and support posture, see [docs/SUPPORT_POLICY.md](docs/SUPPORT_POLICY.md).

## Two Public Lenses

- `world-runtime` is the cautious public infrastructure story: a `v1.0.0-rc.1` runtime with best-effort support and stable commitments around the App Server protocol, Public API `/v1`, Python SDK starter, persistence migrations, and extension contracts.
- The World Game showcase stack is the polished demo story:
  - `labs/world_game_studio_next` is the primary showcase surface for demos, workshops, and new UX work
  - `adapters/world_game` is the domain package and runtime authority that powers that showcase
- The showcase stack is not the support baseline for the whole repo; the root docs describe the runtime commitment, while lab-local and package-local docs carry the deeper showcase narrative.

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

If you want the primary showcase and demo path after that:

```bash
python3 -m api.http_server --host 127.0.0.1 --port 8080
python3 labs/world_game_studio_next/server.py --host 127.0.0.1 --port 8093 --upstream http://127.0.0.1:8080
```

If you are...

- Evaluating the showcase experience: start with [playbooks/world-game-studio-next-demo.md](playbooks/world-game-studio-next-demo.md)
- Building or contributing: start with [docs/developer-quickstart.md](docs/developer-quickstart.md)
- Operating the runtime: start with [playbooks/operator-quickstart.md](playbooks/operator-quickstart.md)
- Integrating through supported surfaces: start with [api/PUBLIC_API_V1.md](api/PUBLIC_API_V1.md) and [sdk/README.md](sdk/README.md)
- Extending the runtime: start with [docs/EXTENSION_CONTRACTS.md](docs/EXTENSION_CONTRACTS.md) and [docs/PARTNER_ONBOARDING.md](docs/PARTNER_ONBOARDING.md)
- Navigating the whole docs surface: start with [docs/README.md](docs/README.md)

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

- Current phase: **v1.0 release candidate**
- Current tagged release candidate: `v1.0.0-rc.1` (2026-03-09)
- Repository package version: `VERSION` -> `1.0.0-rc.1`

For release evidence and operational status, see [STATUS.md](STATUS.md), [CHANGELOG.md](CHANGELOG.md), and [docs/RELEASE_READINESS_CHECKLIST.md](docs/RELEASE_READINESS_CHECKLIST.md).

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
- The World Game showcase stack currently pairs:
  - `labs/world_game_studio_next` as the primary showcase surface
  - `adapters/world_game` as the domain/runtime source of truth
- The most active domain package today is `adapter-world-game`, whose detailed package history lives in [adapters/world_game/ROADMAP.md](adapters/world_game/ROADMAP.md) and [adapters/world_game/STATUS.md](adapters/world_game/STATUS.md).
- `labs/world_game_studio` has been retired after stabilization and is no longer part of the active showcase path.

## Community And Help

- For contribution expectations, see [CONTRIBUTING.md](CONTRIBUTING.md)
- For support posture and stable vs experimental surfaces, see [docs/SUPPORT_POLICY.md](docs/SUPPORT_POLICY.md)
- For security reporting, see [SECURITY.md](SECURITY.md)
- For maintainer/community workflow expectations, see [docs/MAINTAINER_TRIAGE.md](docs/MAINTAINER_TRIAGE.md)

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

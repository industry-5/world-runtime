# What You Can Build with World Runtime

_Last updated: 2026-03-22 (America/Chicago)_

World Runtime is for teams building systems that need to understand the world they operate in, not just move tasks between screens.

Use it when you need explicit world state, append-only events, deterministic replay, simulation before action, and policy-governed decisions with evidence.

This guide is vision-led. It separates what the repo already proves from adjacent opportunities the runtime is well-suited to support next.

Useful entry points:

- Docs hub: [docs/README.md](README.md)
- Repo front door: [README.md](../README.md)

## Why This Category Exists

Ordinary workflow tools are good at routing tasks. World Runtime is built for systems where the state of the world itself matters: entities, relationships, events, projections, proposals, branches, and governed decisions.

| Typical workflow software | World Runtime |
| --- | --- |
| Moves work between people and screens | Models the operating world, then governs action inside it |
| State is often implicit across forms, tickets, and service boundaries | World state is explicit and rebuildable from append-only events |
| History shows activity, but not always causality or consequence | Replay and projection explain how current state was reached |
| Approvals are often process steps | Policy can deny, warn, or require approval before mutation |

## What You Can Build Now

These are the strongest public proof paths in the repo today.

### Supply network planning and disruption response

Model suppliers, routes, inventory, and delays as explicit world state. Rebuild history, compare reroute strategies, and keep what-if analysis separate from canonical state.

Proof in repo:

- strongest proof: replay, projection, and simulation tradeoffs
- constraint profile: medium policy, high branching and consequence tracing
- maintained references: [playbooks/adapter-supply-network.md](../playbooks/adapter-supply-network.md), [examples/scenarios/supply-network-mini/proposal.json](../examples/scenarios/supply-network-mini/proposal.json)

### Safety-constrained air traffic coordination

Use policy-first controls where unsafe decisions must be denied or escalated and where evidence matters before action can be approved.

Proof in repo:

- strongest proof: hard safety outcomes under time pressure
- constraint profile: very high policy, explicit deny and require-approval paths
- maintained references: [playbooks/adapter-air-traffic.md](../playbooks/adapter-air-traffic.md), [tests/test_air_traffic_domain.py](../tests/test_air_traffic_domain.py)

## What Else This Unlocks

These are adjacent opportunities, not claims that a packaged public demo already exists in this repo today.

- Cross-organization incident coordination with shared state and consequence-aware action paths
- Governed semantic and knowledge operations with approval-gated meaning changes
- Evidence-heavy compliance and review systems with runtime-native provenance
- Agent-native planning where humans and policy still govern the right to act

## Capability Map

If your product needs several of these capabilities at once, you are likely in World Runtime territory.

| Runtime capability | Why it matters | Current repo proof |
| --- | --- | --- |
| Explicit world state | Model entities, relationships, and projected state instead of hiding truth inside screens | [ARCHITECTURE.md](../ARCHITECTURE.md), [supply fixture events](../examples/scenarios/supply-network-mini/events.json) |
| Replay and projection | Explain how current state was reached and rebuild it deterministically | [supply playbook](../playbooks/adapter-supply-network.md), [replay tests](../tests/test_event_replay_basics.py) |
| Simulation branches | Compare alternatives before commitment without mutating canonical state | [simulation tests](../tests/test_simulation_engine.py), [operator simulation playbook](../playbooks/operator-simulation-analysis.md) |
| Policy gating | Deny, warn, or require approval before unsafe or non-compliant action happens | [air traffic playbook](../playbooks/adapter-air-traffic.md), [Public API v1](../api/PUBLIC_API_V1.md) |
| Agent-native orchestration | Let tools and agents interpret, propose, and coordinate without bypassing policy | [repo overview](../README.md), [App Server protocol](../APP_SERVER_PROTOCOL.md) |

## How To Evaluate Or Adopt

### Evaluator

- [README.md](../README.md)
- [docs/README.md](README.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)

### Builder

- [docs/developer-quickstart.md](developer-quickstart.md)
- [api/PUBLIC_API_V1.md](../api/PUBLIC_API_V1.md)
- [sdk/README.md](../sdk/README.md)

### Operator

- [playbooks/operator-quickstart.md](../playbooks/operator-quickstart.md)
- [playbooks/operator-proposal-review.md](../playbooks/operator-proposal-review.md)
- [playbooks/operator-simulation-analysis.md](../playbooks/operator-simulation-analysis.md)

### Extender

- [docs/EXTENSION_CONTRACTS.md](EXTENSION_CONTRACTS.md)
- [docs/PARTNER_ONBOARDING.md](PARTNER_ONBOARDING.md)
- [docs/COMPATIBILITY_MATRIX.md](COMPATIBILITY_MATRIX.md)

## Support And Reality Check

World Runtime has a clear public support posture.

Stable and support-committed:

- App Server protocol
- Public API `/v1`
- Python SDK starter
- Persistence migrations
- Extension contracts

Experimental or best-effort:

- starter templates and exploratory examples unless promoted
- release-candidate-only workflows that may still be refined

For the authoritative support boundary, read [docs/SUPPORT_POLICY.md](SUPPORT_POLICY.md).

## Next Step

If you are evaluating product fit, start with the [docs hub](README.md).

If you already know the category is right, jump into the [developer quickstart](developer-quickstart.md) and the [supported API surfaces](../api/PUBLIC_API_V1.md).

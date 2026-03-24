# What You Can Build with World Runtime

_Last updated: 2026-03-23 (America/Chicago)_

World Runtime is for teams building systems that need to understand the world they operate in, not just move tasks between screens.

Use it when you need explicit world state, append-only events, deterministic replay, simulation before action, and policy-governed decisions with evidence.

This guide frames the repo through the public domain adapter scenario program: compact domain bundles that prove the runtime under realistic tension.
The current portfolio is promotion-hardened for downstream public export: eleven standalone proof paths plus one host-bound overlay track.

Useful entry points:

- Docs hub: [docs/README.md](README.md)
- Repo front door: [README.md](../README.md)
- Adapter series docs: [adapters/README.md](../adapters/README.md)

## Why This Category Exists

Ordinary workflow tools are good at routing tasks. World Runtime is built for systems where the state of the world itself matters: entities, relationships, events, projections, proposals, branches, and governed decisions.

| Typical workflow software | World Runtime |
| --- | --- |
| Moves work between people and screens | Models the operating world, then governs action inside it |
| State is often implicit across forms, tickets, and service boundaries | World state is explicit and rebuildable from append-only events |
| History shows activity, but not always causality or consequence | Replay and projection explain how current state was reached |
| Approvals are often process steps | Policy can deny, warn, or require approval before mutation |

## Implemented Public Proof Paths Today

These are the strongest implemented public tracks in the repo today.

### Supply network planning and disruption response

Model suppliers, routes, inventory, and delays as explicit world state. Rebuild history, compare reroute strategies, and keep what-if analysis separate from canonical state.

Proof in repo:

- strongest proof: replay, projection, and simulation tradeoffs
- constraint profile: medium policy, high branching and consequence tracing
- current artifacts: [playbooks/adapter-supply-network.md](../playbooks/adapter-supply-network.md), [adapters/supply_network/README.md](../adapters/supply_network/README.md)

### Safety-constrained air traffic coordination

Use policy-first controls where unsafe decisions must be denied or escalated and where evidence matters before action can be approved.

Proof in repo:

- strongest proof: hard safety outcomes under time pressure
- constraint profile: very high policy, explicit deny and require-approval paths
- current artifacts: [playbooks/adapter-air-traffic.md](../playbooks/adapter-air-traffic.md), [adapters/air_traffic/README.md](../adapters/air_traffic/README.md)

### Governed semantic coherence and meaning change

Model terms, definitions, and mappings as explicit world state so meaning changes stay reviewable, provenance-visible, and policy-governed.

Proof in repo:

- strongest proof: governed meaning changes with provenance and semantic alternatives
- constraint profile: high governance, explicit deny and require-approval paths
- current artifacts: [playbooks/adapter-semantic-system.md](../playbooks/adapter-semantic-system.md), [adapters/semantic_system/README.md](../adapters/semantic_system/README.md)

### Power-grid balancing and contingency response

Model balancing authorities, transmission constraints, and staged interruption decisions as explicit world state so cascading infrastructure choices remain simulation-backed and reviewable.

Proof in repo:

- strongest proof: cascading simulation with least-bad contingency tradeoffs
- constraint profile: high infrastructure governance, explicit deny and require-approval paths
- current artifacts: [playbooks/adapter-power-grid.md](../playbooks/adapter-power-grid.md), [adapters/power_grid/README.md](../adapters/power_grid/README.md)

### Cross-agency city operations incident coordination

Model agencies, transit, utilities, and response zones as one shared operating world so civic incidents stay coordinated, approval-visible, and evidence-backed.

Proof in repo:

- strongest proof: cross-agency coordination with resident-impact tradeoffs
- constraint profile: high coordination, explicit deny and require-approval paths
- current artifacts: [playbooks/adapter-city-ops.md](../playbooks/adapter-city-ops.md), [adapters/city_ops/README.md](../adapters/city_ops/README.md)

### Regulated lab science evidence and release governance

Model sample batches, instrument runs, evidence chains, and deviation review as explicit world state so regulated releases stay provenance-visible and approval-governed.

Proof in repo:

- strongest proof: evidence integrity with supervised release alternatives
- constraint profile: high provenance, explicit deny, warn, and require-approval paths
- current artifacts: [playbooks/adapter-lab-science.md](../playbooks/adapter-lab-science.md), [adapters/lab_science/README.md](../adapters/lab_science/README.md)

### Market micro exposure control and inventory pressure

Model venues, books, inventory pressure, and risk limits as explicit world state so market interventions remain reviewable, simulation-backed, and desk-governed.

Proof in repo:

- strongest proof: high-intensity exposure controls with deny/allow/review alternatives
- constraint profile: high event intensity, explicit deny, warn, and require-approval paths
- current artifacts: [playbooks/adapter-market-micro.md](../playbooks/adapter-market-micro.md), [adapters/market_micro/README.md](../adapters/market_micro/README.md)

### Multiplayer shared-state reconciliation and fairness control

Model contested match state, shard authority, and rollback bounds as explicit world state so simultaneous player intents stay reviewable, simulation-backed, and live-ops governed.

Proof in repo:

- strongest proof: shared-state reconciliation under concurrent update pressure
- constraint profile: high contention, explicit deny, warn, and require-approval paths
- current artifacts: [playbooks/adapter-multiplayer-game.md](../playbooks/adapter-multiplayer-game.md), [adapters/multiplayer_game/README.md](../adapters/multiplayer_game/README.md)

### Autonomous vehicle motion planning and supervised intervention

Model vehicles, road segments, occluded hazards, and teleassist decisions as explicit world state so dynamic motion plans stay safety-limited, reviewable, and simulation-backed.

Proof in repo:

- strongest proof: motion-safety interventions under occlusion and teleassist pressure
- constraint profile: hard physical safety, explicit deny, warn, and require-approval paths
- current artifacts: [playbooks/adapter-autonomous-vehicle.md](../playbooks/adapter-autonomous-vehicle.md), [adapters/autonomous_vehicle/README.md](../adapters/autonomous_vehicle/README.md)

### Multi-agent AI coordination, branch review, and governed delegation

Model agent teams, shared context, and review boards as explicit world state so delegated plans stay reviewable, simulation-backed, and policy-governed under branching pressure.

Proof in repo:

- strongest proof: delegated coordination under branch-review pressure
- constraint profile: high governance, explicit deny, warn, and require-approval paths
- current artifacts: [playbooks/adapter-multi-agent-ai.md](../playbooks/adapter-multi-agent-ai.md), [adapters/multi_agent_ai/README.md](../adapters/multi_agent_ai/README.md)

### Open-agent-world shared commons intervention and stewardship

Model world zones, agent cohorts, governance beacons, and resource pools as explicit world state so emergent conflicts stay intervention-ready, approval-visible, and bounded by explicit oversight.

Proof in repo:

- strongest proof: shared-world governance under emergent conflict pressure
- constraint profile: high intervention pressure, explicit deny, warn, and require-approval paths
- current artifacts: [playbooks/adapter-open-agent-world.md](../playbooks/adapter-open-agent-world.md), [adapters/open_agent_world/README.md](../adapters/open_agent_world/README.md)

## Implemented Overlay Track

This track is part of the public adapter-series roadmap and is now implemented as a runtime-authoritative overlay package under `adapters/`.

| Scenario | What you could build | Primary proof | Current program state |
| --- | --- | --- | --- |
| `digital-twin-mini` | Host-bound overlay twins attached to other domains | Overlay simulation and host binding | Implemented; host-bound across `power_grid` then `city_ops` |

Current artifacts: [playbooks/adapter-digital-twin.md](../playbooks/adapter-digital-twin.md), [adapters/digital_twin/README.md](../adapters/digital_twin/README.md)

## How The Portfolio Is Packaged

The standard non-overlay scenario bundle keeps the public adapter portfolio comparable across domains.

The standard non-overlay public scenario-bundle contract is:

- `README.md`
- `entities.json`
- `relationships.json`
- `events.json`
- `proposal.json`
- `decision.json`
- `simulation.json`
- `policy.json`
- `rule.json`
- `projection.json`

Adapter-local supplemental proofs can add extra files beside that baseline when a domain needs deeper evidence, but the shared contract keeps the public tracks comparable.

The overlay bundle contract used by `digital-twin-mini` keeps the same runtime artifact set and adds:

- `host_bindings.json`

`digital-twin-mini` is the implemented overlay exception rather than a standalone showcase domain.

## How To Evaluate Or Adopt

### Evaluator

- [README.md](../README.md)
- [docs/README.md](README.md)
- [adapters/README.md](../adapters/README.md)

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
- future adapter additions or post-promotion follow-up work unless explicitly promoted

For the authoritative support boundary, read [docs/SUPPORT_POLICY.md](SUPPORT_POLICY.md).

## Next Step

If you are evaluating product fit, start with the [docs hub](README.md) and [adapters/README.md](../adapters/README.md).

If you already know the category is right, jump into the [developer quickstart](developer-quickstart.md) and the [supported API surfaces](../api/PUBLIC_API_V1.md).

# Supply Network Public Adapter Roadmap

_Last updated: 2026-03-23 (America/Chicago)_

## Goal

Keep `adapter-supply-network` as the public operational orchestration proof for disruption response, replay, projection, and simulation-before-action.

## Milestones

### SN-M0 - Bootstrap and hygiene

Status: Completed (2026-03-23)

Objective:

- seed package-local governance docs and align the package with the public adapter program process shape

### SN-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Status: Completed (2026-03-23)

Objective:

- normalize and verify the existing adapter assets on disk as a package-local `M1` slice

Acceptance highlights:

- package-local docs truthfully describe the current supply-network adapter surface
- the existing adapter contract, schemas, policy, and minimal scenario stay aligned
- registry/example/test expectations for the package are explicit

### SN-M2 - Domain tension and policy proof

Status: Completed (2026-03-23)

Objective:

- deepen the supply-network policy and rerouting tension proof so the package can demonstrate meaningful operational tradeoffs

Delivered:

- alternate reroute tradeoffs are now explicit through `reroute_options.json`, enriched decision/simulation artifacts, and `tests/test_supply_network_domain.py`
- package docs now treat tradeoff review as package-local proof instead of leaving the track framed as only a minimal legacy scenario

### SN-M3 - Replay, simulation, playbook, and docs completion

Status: Completed (2026-03-23)

Objective:

- finish replay/simulation/package-doc parity and contributor/operator guidance for the public supply-network track

Delivered:

- replay/simulation artifacts, playbook guidance, and package docs are now aligned around the implemented public supply-network slice
- kickoff/history docs now advance cleanly to the next package milestone without implying promotion hardening is already done

### SN-M4 - Promotion hardening

Status: Completed (2026-03-23)

Objective:

- harden the package for downstream public promotion readiness

Delivered:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package-local current-state docs now record the completed `SN-M4` hardening pass without widening stable App Server, HTTP API, or SDK surfaces

## Package Notes

- The package is now promotion-hardened through `SN-M4`; future work should be scoped as post-promotion follow-through or a newly declared milestone.
- Root docs should stay rollup-only while package-local docs carry milestone detail.

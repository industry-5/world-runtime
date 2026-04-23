# Air Traffic Public Adapter Roadmap

_Last updated: 2026-03-23 (America/Chicago)_

## Goal

Keep `adapter-air-traffic` as the safety-constrained public adapter proof for hard constraints, approvals, urgency, and simulation-before-action.

## Milestones

### AT-M0 - Bootstrap and hygiene

Status: Completed (2026-03-23)

Objective:

- seed package-local governance docs and align the package with the public adapter program process shape

### AT-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Status: Completed (2026-03-23)

Objective:

- normalize and verify the existing adapter assets on disk as a package-local `M1` slice

Acceptance highlights:

- package-local docs truthfully describe the current air-traffic adapter surface
- the existing adapter contract, schemas, policy, and minimal scenario stay aligned
- registry/example/test expectations for the package are explicit

### AT-M2 - Domain tension and policy proof

Status: Completed (2026-03-23)

Objective:

- deepen the safety-tension and approval proof so constrained air-traffic decisions are package-locally documented and validated

Delivered:

- package-local policy proof is now explicit through `conflicting_proposals.json` plus `tests/test_air_traffic_domain.py`
- package docs now treat constrained alternative review as a first-class air-traffic proof surface instead of legacy carryover detail

### AT-M3 - Replay, simulation, playbook, and docs completion

Status: Completed (2026-03-23)

Objective:

- finish replay/simulation/package-doc parity and contributor/operator guidance for the public air-traffic track

Delivered:

- replay/simulation artifacts, playbook guidance, and package-local docs are now aligned around the implemented public slice
- kickoff/history docs now advance cleanly to the next package milestone without implying promotion hardening is already done

### AT-M4 - Promotion hardening

Status: Completed (2026-03-23)

Objective:

- harden the package for downstream public promotion readiness

Delivered:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package-local current-state docs now record the completed `AT-M4` hardening pass without widening stable App Server, HTTP API, or SDK surfaces

## Package Notes

- The package is now promotion-hardened through `AT-M4`; future work should be scoped as post-promotion follow-through or a newly declared milestone.
- Root docs should stay rollup-only while package-local docs carry milestone detail.

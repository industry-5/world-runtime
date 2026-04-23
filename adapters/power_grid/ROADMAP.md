# Power Grid Public Adapter Roadmap

_Last updated: 2026-03-23 (America/Chicago)_

## Goal

Establish `adapter-power-grid` as the public critical-infrastructure proof for balancing, contingencies, and cascading simulation.

## Milestones

### PG-M0 - Bootstrap and hygiene

Status: Completed (2026-03-23)

### PG-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Status: Completed (2026-03-23)

Objective:

- establish the first public power-grid adapter slice and minimal `power-grid-mini` scenario bundle

Delivered:

- `adapter.py`, schemas, default policy, and the minimal public scenario bundle now exist on the shared adapter contract
- registry/example/test surfaces recognize the package as an implemented public track

### PG-M2 - Domain tension and policy proof

Status: Completed (2026-03-23)

Objective:

- prove least-bad contingency response, interruption approval pressure, and explicit power-grid alternatives

Delivered:

- `contingency_options.json` now carries contingency-response alternatives beside the shared bundle baseline
- `tests/test_power_grid_domain.py` validates deny/allow/require-approval behavior for the package-local power-grid proof path

### PG-M3 - Replay, simulation, playbook, and docs completion

Status: Completed (2026-03-23)

Objective:

- complete replay/simulation/package-doc parity and contributor/operator guidance

Delivered:

- replay/simulation artifacts, playbook guidance, and package docs are now aligned around the implemented public power-grid slice
- kickoff/history docs now advance cleanly to the next package milestone without implying promotion hardening is already done

### PG-M4 - Promotion hardening

Status: Completed (2026-03-23)

Objective:

- harden the package for downstream public promotion readiness

Delivered:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package-local current-state docs now record the completed `PG-M4` hardening pass without widening stable App Server, HTTP API, or SDK surfaces

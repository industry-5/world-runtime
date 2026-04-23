# Multiplayer Game Public Adapter Roadmap

_Last updated: 2026-03-23 (America/Chicago)_

## Goal

Establish `adapter-multiplayer-game` as the public shared-state concurrency proof for simultaneous actor updates and synchronization pressure.

## Milestones

### MPG-M0 - Bootstrap and hygiene

Status: Completed (2026-03-23)

### MPG-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Status: Completed (2026-03-23)

Objective:

- establish the first public multiplayer-game adapter slice and minimal `multiplayer-game-mini` scenario bundle

Delivered:

- `adapter.py`, schemas, default policy, and the minimal public scenario bundle now exist on the shared adapter contract
- registry/example/test surfaces recognize the package as an implemented public track

### MPG-M2 - Domain tension and policy proof

Status: Completed (2026-03-23)

Objective:

- prove contested-state resolution alternatives, rollback pressure, and approval-required live synchronization choices

Delivered:

- `resolution_options.json` now carries concurrency-resolution alternatives beside the shared bundle baseline
- `tests/test_multiplayer_game_domain.py` validates deny/allow/require-approval behavior for the package-local proof path

### MPG-M3 - Replay, simulation, playbook, and docs completion

Status: Completed (2026-03-23)

Objective:

- complete replay/simulation/package-doc parity and contributor/operator guidance

Delivered:

- replay/simulation artifacts, playbook guidance, and package docs are now aligned around the implemented public multiplayer-game slice
- kickoff/history docs now advance cleanly to the next package milestone without implying promotion hardening is already done

### MPG-M4 - Promotion hardening

Status: Completed (2026-03-23)

Objective:

- harden the package for downstream public promotion readiness

Delivered:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package-local current-state docs now record the completed `MPG-M4` hardening pass without widening stable App Server, HTTP API, or SDK surfaces

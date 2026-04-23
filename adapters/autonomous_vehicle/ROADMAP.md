# Autonomous Vehicle Public Adapter Roadmap

_Last updated: 2026-03-23 (America/Chicago)_

## Goal

Establish `adapter-autonomous-vehicle` as the public hard-constraint mobility proof for dynamic planning and safety-limited interventions.

## Milestones

### AV-M0 - Bootstrap and hygiene

Status: Completed (2026-03-23)

### AV-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Status: Completed (2026-03-23)

Objective:

- establish the first public autonomous-vehicle adapter slice and minimal `autonomous-vehicle-mini` scenario bundle

Delivered:

- `adapter.py`, schemas, default policy, and the minimal public scenario bundle now exist on the shared adapter contract
- registry/example/test surfaces recognize the package as an implemented public track

### AV-M2 - Domain tension and policy proof

Status: Completed (2026-03-23)

Objective:

- prove motion-safety alternatives, intervention pressure, and approval-required creep decisions under occlusion

Delivered:

- `maneuver_options.json` now carries motion-safety alternatives beside the shared bundle baseline
- `tests/test_autonomous_vehicle_domain.py` validates deny/allow/require-approval behavior for the package-local proof path

### AV-M3 - Replay, simulation, playbook, and docs completion

Status: Completed (2026-03-23)

Objective:

- complete replay/simulation/package-doc parity and contributor/operator guidance

Delivered:

- replay/simulation artifacts, playbook guidance, and package docs are now aligned around the implemented public autonomous-vehicle slice
- kickoff/history docs now advance cleanly to the next package milestone without implying promotion hardening is already done

### AV-M4 - Promotion hardening

Status: Completed (2026-03-23)

Objective:

- harden the package for downstream public promotion readiness

Delivered:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package-local current-state docs now record the completed `AV-M4` hardening pass without widening stable App Server, HTTP API, or SDK surfaces

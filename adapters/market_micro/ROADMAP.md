# Market Micro Public Adapter Roadmap

_Last updated: 2026-03-23 (America/Chicago)_

## Goal

Establish `adapter-market-micro` as the public high-intensity market sandbox for exposure, conflict, and risk-limit proofs.

## Milestones

### MM-M0 - Bootstrap and hygiene

Status: Completed (2026-03-23)

### MM-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Status: Completed (2026-03-23)

Objective:

- establish the first public market-micro adapter slice and minimal `market-micro-mini` scenario bundle

Delivered:

- `adapter.py`, schemas, default policy, and the minimal public scenario bundle now exist on the shared adapter contract
- registry/example/test surfaces recognize the package as an implemented public track

### MM-M2 - Domain tension and policy proof

Status: Completed (2026-03-23)

Objective:

- prove supervised de-risking alternatives, exposure pressure, and approval-required inventory interventions

Delivered:

- `risk_options.json` now carries market-risk alternatives beside the shared bundle baseline
- `tests/test_market_micro_domain.py` validates deny/allow/require-approval behavior for the package-local proof path

### MM-M3 - Replay, simulation, playbook, and docs completion

Status: Completed (2026-03-23)

Objective:

- complete replay/simulation/package-doc parity and contributor/operator guidance

Delivered:

- replay/simulation artifacts, playbook guidance, and package docs are now aligned around the implemented public market-micro slice
- kickoff/history docs now advance cleanly to the next package milestone without implying promotion hardening is already done

### MM-M4 - Promotion hardening

Status: Completed (2026-03-23)

Objective:

- harden the package for downstream public promotion readiness

Delivered:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package-local current-state docs now record the completed `MM-M4` hardening pass without widening stable App Server, HTTP API, or SDK surfaces

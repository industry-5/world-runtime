# Multi-Agent AI Public Adapter Roadmap

_Last updated: 2026-03-23 (America/Chicago)_

## Goal

Establish `adapter-multi-agent-ai` as the public agent-coordination proof for proposal, branching, conflict, and governed review.

## Milestones

### MA-M0 - Bootstrap and hygiene

Status: Completed (2026-03-23)

### MA-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Status: Completed (2026-03-23)

Objective:

- establish the first public multi-agent AI adapter slice and minimal `multi-agent-ai-mini` scenario bundle

Delivered:

- `adapter.py`, schemas, default policy, and the minimal public scenario bundle now exist on the shared adapter contract
- registry/example/test surfaces recognize the package as an implemented public track

### MA-M2 - Domain tension and policy proof

Status: Completed (2026-03-23)

Objective:

- prove delegated coordination alternatives, branch-review pressure, and approval-required multi-agent plans

Delivered:

- `branch_options.json` now carries reviewed coordination alternatives beside the shared bundle baseline
- `tests/test_multi_agent_ai_domain.py` validates deny/allow/require-approval behavior for the package-local proof path

### MA-M3 - Replay, simulation, playbook, and docs completion

Status: Completed (2026-03-23)

Objective:

- complete replay/simulation/package-doc parity and contributor/operator guidance

Delivered:

- replay/simulation artifacts, playbook guidance, and package docs are now aligned around the implemented public multi-agent AI slice
- kickoff/history docs now advance cleanly to the next package milestone without implying promotion hardening is already done

### MA-M4 - Promotion hardening

Status: Completed (2026-03-23)

Objective:

- harden the package for downstream public promotion readiness

Delivered:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package-local current-state docs now record the completed `MA-M4` hardening pass without widening stable App Server, HTTP API, or SDK surfaces

# Open Agent World Public Adapter Changelog

## Unreleased

### OAW-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `OAW-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### OAW-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `OAW-M2`, `OAW-M3`, and `OAW-M4`
- `playbooks/adapter-open-agent-world.md`

Changed:

- package docs and kickoff state now describe the implemented public open-agent-world slice through local `OAW-M3`

### OAW-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/open-agent-world-mini/intervention_options.json`
- `tests/test_open_agent_world_domain.py`

Changed:

- package-local milestone history now treats bounded intervention alternatives as the explicit proof path beside the shared bundle baseline

### OAW-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Added:

- `adapter.py`, schemas, default policy, and the `open-agent-world-mini` public scenario bundle

Changed:

- the package is now registered as an implemented public adapter track

### OAW-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public open-agent-world track
- milestone scaffolding for `OAW-M0` and `OAW-M1`

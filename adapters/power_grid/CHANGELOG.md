# Power Grid Public Adapter Changelog

## Unreleased

### PG-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `PG-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### PG-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `PG-M2`, `PG-M3`, and `PG-M4`
- `playbooks/adapter-power-grid.md`

Changed:

- package docs and kickoff state now describe the implemented public power-grid slice through local `PG-M3`

### PG-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/power-grid-mini/contingency_options.json`
- `tests/test_power_grid_domain.py`

Changed:

- package-local milestone history now treats contingency-response alternatives as the explicit proof path beside the shared bundle baseline

### PG-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Added:

- `adapter.py`, schemas, default policy, and the `power-grid-mini` public scenario bundle

Changed:

- the package is now registered as an implemented public adapter track

### PG-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public power-grid track
- milestone scaffolding for `PG-M0` and `PG-M1`

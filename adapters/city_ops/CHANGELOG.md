# City Ops Public Adapter Changelog

## Unreleased

### CO-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `CO-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### CO-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `CO-M2`, `CO-M3`, and `CO-M4`
- `playbooks/adapter-city-ops.md`

Changed:

- package docs and kickoff state now describe the implemented public city-ops slice through local `CO-M3`

### CO-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/city-ops-mini/coordination_options.json`
- `tests/test_city_ops_domain.py`

Changed:

- package-local milestone history now treats civic coordination alternatives as the explicit proof path beside the shared bundle baseline

### CO-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Added:

- `adapter.py`, schemas, default policy, and the `city-ops-mini` public scenario bundle

Changed:

- the package is now registered as an implemented public adapter track

### CO-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public city-ops track
- milestone scaffolding for `CO-M0` and `CO-M1`

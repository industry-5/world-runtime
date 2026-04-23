# Supply Network Public Adapter Changelog

## Unreleased

### SN-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `SN-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### SN-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `SN-M2`, `SN-M3`, and `SN-M4`

Changed:

- package docs and kickoff state now describe the implemented public supply-network slice through local `SN-M3`
- contributor/operator guidance is now aligned around the replay/simulation artifacts already on disk

### SN-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/supply-network-mini/reroute_options.json`
- `tests/test_supply_network_domain.py`

Changed:

- decision/simulation artifacts now preserve alternate reroute tradeoffs beside the shared public bundle baseline
- package status/roadmap no longer leave the supply-network track framed as only a legacy `SN-M1` carryover

### SN-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Changed:

- package-local docs now record the existing adapter contract, schemas, default policy, and minimal scenario as the completed `SN-M1` slice

### SN-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public supply-network adapter track
- milestone scaffolding for `SN-M0` and `SN-M1`

Changed:

- package-local docs now capture the existing supply-network adapter assets as the starting point for future public-track milestone work

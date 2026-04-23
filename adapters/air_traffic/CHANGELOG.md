# Air Traffic Public Adapter Changelog

## Unreleased

### AT-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `AT-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### AT-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `AT-M2`, `AT-M3`, and `AT-M4`

Changed:

- package docs and kickoff state now describe the implemented public air-traffic slice through local `AT-M3`
- contributor/operator guidance is now aligned around the replay/simulation artifacts already on disk

### AT-M2 - Domain tension and policy proof

Changed:

- package-local milestone history now treats `conflicting_proposals.json` and `tests/test_air_traffic_domain.py` as the explicit air-traffic policy proof surface
- package status/roadmap no longer leave the air-traffic track framed as only a legacy `AT-M1` carryover

### AT-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Changed:

- package-local docs now record the existing adapter contract, schemas, default policy, and minimal scenario as the completed `AT-M1` slice

### AT-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public air-traffic adapter track
- milestone scaffolding for `AT-M0` and `AT-M1`

Changed:

- package-local docs now capture the existing air-traffic adapter assets as the starting point for future public-track milestone work

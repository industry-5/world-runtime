# Autonomous Vehicle Public Adapter Changelog

## Unreleased

### AV-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `AV-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### AV-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `AV-M2`, `AV-M3`, and `AV-M4`
- `playbooks/adapter-autonomous-vehicle.md`

Changed:

- package docs and kickoff state now describe the implemented public autonomous-vehicle slice through local `AV-M3`

### AV-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/autonomous-vehicle-mini/maneuver_options.json`
- `tests/test_autonomous_vehicle_domain.py`

Changed:

- package-local milestone history now treats motion-safety alternatives as the explicit proof path beside the shared bundle baseline

### AV-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Added:

- `adapter.py`, schemas, default policy, and the `autonomous-vehicle-mini` public scenario bundle

Changed:

- the package is now registered as an implemented public adapter track

### AV-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public autonomous-vehicle track
- milestone scaffolding for `AV-M0` and `AV-M1`

# Digital Twin Public Adapter Changelog

## Unreleased

### DT-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `DT-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### DT-M3 - City-ops overlay expansion and docs completion

Added:

- `playbooks/adapter-digital-twin.md`
- package-local milestone briefs for `DT-M2`, `DT-M3`, and `DT-M4`

Changed:

- package docs and kickoff state now describe the implemented public digital-twin overlay slice through local `DT-M3`

### DT-M2 - Power-grid overlay proof

Added:

- `examples/scenarios/digital-twin-mini/host_bindings.json`
- `examples/scenarios/digital-twin-mini/overlay_options.json`
- `tests/test_digital_twin_domain.py`

Changed:

- package-local milestone history now treats the power-grid-first host proof as explicit overlay evidence beside the shared runtime artifact set

### DT-M1 - Overlay positioning, host-bound contract, and minimal metadata wiring

Added:

- `adapter.py`, schemas, default policy, and the `digital-twin-mini` public overlay bundle

Changed:

- the package is now registered as an implemented public adapter track

### DT-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public digital-twin overlay track
- milestone scaffolding for `DT-M0` and `DT-M1`

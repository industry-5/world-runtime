# Lab Science Public Adapter Changelog

## Unreleased

### LS-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `LS-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### LS-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `LS-M2`, `LS-M3`, and `LS-M4`
- `playbooks/adapter-lab-science.md`

Changed:

- package docs and kickoff state now describe the implemented public lab-science slice through local `LS-M3`

### LS-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/lab-science-mini/release_options.json`
- `tests/test_lab_science_domain.py`

Changed:

- package-local milestone history now treats regulated release alternatives as the explicit proof path beside the shared bundle baseline

### LS-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Added:

- `adapter.py`, schemas, default policy, and the `lab-science-mini` public scenario bundle

Changed:

- the package is now registered as an implemented public adapter track

### LS-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public lab-science track
- milestone scaffolding for `LS-M0` and `LS-M1`

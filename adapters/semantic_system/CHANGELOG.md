# Semantic System Public Adapter Changelog

## Unreleased

### SS-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `SS-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### SS-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `SS-M2`, `SS-M3`, and `SS-M4`
- `playbooks/adapter-semantic-system.md`

Changed:

- package docs and kickoff state now describe the implemented public semantic-system slice through local `SS-M3`

### SS-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/semantic-system-mini/conflicting_proposals.json`
- `tests/test_semantic_system_domain.py`

Changed:

- package-local milestone history now treats governed semantic alternatives as the explicit proof path beside the shared bundle baseline

### SS-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Added:

- `adapter.py`, schemas, default policy, and the `semantic-system-mini` public scenario bundle

Changed:

- the package is now registered as an implemented public adapter track

### SS-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public semantic-system track
- milestone scaffolding for `SS-M0` and `SS-M1`

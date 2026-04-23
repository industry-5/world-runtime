# Market Micro Public Adapter Changelog

## Unreleased

### MM-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `MM-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### MM-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `MM-M2`, `MM-M3`, and `MM-M4`
- `playbooks/adapter-market-micro.md`

Changed:

- package docs and kickoff state now describe the implemented public market-micro slice through local `MM-M3`

### MM-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/market-micro-mini/risk_options.json`
- `tests/test_market_micro_domain.py`

Changed:

- package-local milestone history now treats market-risk alternatives as the explicit proof path beside the shared bundle baseline

### MM-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Added:

- `adapter.py`, schemas, default policy, and the `market-micro-mini` public scenario bundle

Changed:

- the package is now registered as an implemented public adapter track

### MM-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public market-micro track
- milestone scaffolding for `MM-M0` and `MM-M1`

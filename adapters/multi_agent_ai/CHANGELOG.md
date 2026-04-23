# Multi-Agent AI Public Adapter Changelog

## Unreleased

### MA-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `MA-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### MA-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `MA-M2`, `MA-M3`, and `MA-M4`
- `playbooks/adapter-multi-agent-ai.md`

Changed:

- package docs and kickoff state now describe the implemented public multi-agent AI slice through local `MA-M3`

### MA-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/multi-agent-ai-mini/branch_options.json`
- `tests/test_multi_agent_ai_domain.py`

Changed:

- package-local milestone history now treats reviewed coordination alternatives as the explicit proof path beside the shared bundle baseline

### MA-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Added:

- `adapter.py`, schemas, default policy, and the `multi-agent-ai-mini` public scenario bundle

Changed:

- the package is now registered as an implemented public adapter track

### MA-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public multi-agent AI track
- milestone scaffolding for `MA-M0` and `MA-M1`

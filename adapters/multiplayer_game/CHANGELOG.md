# Multiplayer Game Public Adapter Changelog

## Unreleased

### MPG-M4 - Promotion hardening

Changed:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package status, roadmap, README, and kickoff state now describe the completed public `MPG-M4` slice without widening stable App Server, HTTP API, or SDK surfaces

### MPG-M3 - Replay, simulation, playbook, and docs completion

Added:

- package-local milestone briefs for `MPG-M2`, `MPG-M3`, and `MPG-M4`
- `playbooks/adapter-multiplayer-game.md`

Changed:

- package docs and kickoff state now describe the implemented public multiplayer-game slice through local `MPG-M3`

### MPG-M2 - Domain tension and policy proof

Added:

- `examples/scenarios/multiplayer-game-mini/resolution_options.json`
- `tests/test_multiplayer_game_domain.py`

Changed:

- package-local milestone history now treats concurrency-resolution alternatives as the explicit proof path beside the shared bundle baseline

### MPG-M1 - Adapter contract, schemas, minimal scenario, registry wiring

Added:

- `adapter.py`, schemas, default policy, and the `multiplayer-game-mini` public scenario bundle

Changed:

- the package is now registered as an implemented public adapter track

### MPG-M0 - Bootstrap and hygiene

Added:

- package-local governance docs for the public multiplayer-game track
- milestone scaffolding for `MPG-M0` and `MPG-M1`

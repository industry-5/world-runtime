# Multiplayer Game Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-multiplayer-game`
- Milestone status: **MPG-M0 through MPG-M4 complete**
- Current milestone: **No active package milestone (MPG-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_MPG_M4.md` retained for history

## Current Snapshot

- `MPG-M1` established the first runtime-authoritative multiplayer-game adapter slice, schemas, policy, and minimal public scenario bundle
- `MPG-M2` now treats concurrency-resolution alternatives, rollback pressure, and approval-required reconciliation as explicit package-local proof through `resolution_options.json` and `tests/test_multiplayer_game_domain.py`
- `MPG-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public multiplayer-game slice
- `MPG-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_multiplayer_game_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `MPG-M4` validation baseline:

1. Package bootstrap:
- `find adapters/multiplayer_game -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "MPG-M[0-4]" adapters/multiplayer_game/ROADMAP.md adapters/multiplayer_game/STATUS.md adapters/multiplayer_game/README.md adapters/multiplayer_game/NEW_THREAD_KICKOFF_PROMPT.md adapters/multiplayer_game/NEW_THREAD_MPG_M0.md adapters/multiplayer_game/NEW_THREAD_MPG_M1.md adapters/multiplayer_game/NEW_THREAD_MPG_M2.md adapters/multiplayer_game/NEW_THREAD_MPG_M3.md adapters/multiplayer_game/NEW_THREAD_MPG_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_multiplayer_game_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-multiplayer-game.md` and `examples/scenarios/multiplayer-game-mini/README.md` still describe the same synchronization path

## Completed MPG-M4 Outcome

- the completed `MPG-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `MPG-M4` slice instead of reopening foundational implementation work
- the multiplayer-game track should stay focused on authoritative reconciliation, simultaneous intent handling, and shared-state fairness rather than broad consumer game features

## Handoff Checklist For New Thread

1. Re-read `adapters/multiplayer_game/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/multiplayer_game/NEW_THREAD_MPG_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `MPG-M0` through `MPG-M4` scope unless a correctness fix requires it.

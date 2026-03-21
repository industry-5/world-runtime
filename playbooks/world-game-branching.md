# Playbook: World Game Branching and Replay

## Branch model

- Baseline branch is loaded from `world_game.scenario.load`.
- New branches are created with `world_game.branch.create`.
- In collaboration-enabled sessions, `world_game.proposal.adopt` is the preferred path before mutating branches.
- Turn execution is branch-local via `world_game.turn.run`.
- Branch comparison is deterministic via `world_game.branch.compare`.

## Replay model

- Branches record ordered `wg_turn_executed` events.
- `world_game.replay.run` rebuilds state from baseline plus ordered events.
- Replay parity is expected when inputs and ordering are unchanged.

## Determinism rules

- Stable ordering of interventions/shocks and effects.
- No random shock triggering in runtime turn execution.
- Policy evaluation before canonical commit.
- Collaboration stage gating is additive and only applies when World Game collaboration mode is enabled.

## Collaboration note

Direct branch creation remains supported for single-user or low-ceremony analysis. When you want facilitated workshop flow, use:

1. `world_game.session.create`
2. `world_game.proposal.create`
3. `world_game.proposal.submit`
4. `world_game.proposal.adopt`

This keeps branch creation attributable to actors and connected to proposal/provenance records.

## Validation

- `python3 -m pytest -q tests/test_world_game_branches.py tests/test_world_game_replay.py tests/test_world_game_compare.py`
- `python3 -m pytest -q tests/test_world_game_smoke.py`

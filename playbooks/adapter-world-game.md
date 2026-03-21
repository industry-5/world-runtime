# Playbook: World Game Adapter

## Goal

Run `adapter-world-game` as a collaborative planning domain with deterministic branching, replay, policy-aware turns, annotations, and provenance inspection.

This playbook covers the domain/runtime layer behind the showcase app. For the primary showcase UI walkthrough, use [playbooks/world-game-studio-next-demo.md](world-game-studio-next-demo.md).

## Steps

1. Validate adapter and scenario assets.
2. Create a World Game collaboration session.
3. Load a world-game scenario through runtime methods.
4. Create and submit a proposal.
5. Adopt the proposal into a branch.
6. Execute one or more turns with interventions/shocks.
7. Compare outcomes and replay branch events.
8. Add annotations and inspect provenance.

## Commands

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_world_game_domain.py tests/test_world_game_smoke.py`
- `python3 -m pytest -q tests/test_world_game_policies.py tests/test_world_game_replay.py`
- `python3 -m pytest -q tests/test_world_game_collaboration.py tests/labs/test_world_game_studio_next.py`

## Notes

- Direct branch creation with `world_game.branch.create` still works.
- Collaboration mode adds actor roles, stage gating, proposals, annotations, and provenance on top of the existing single-user workflow.
- Collaboration durability is currently limited to the active runtime session.
- `labs/world_game_studio` has been retired; use `labs/world_game_studio_next` for the active UI path.

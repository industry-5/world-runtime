# Playbook: Multiplayer Game Adapter

## Goal

Run a public multiplayer-game synchronization workflow without changing kernel internals.

## Steps

1. Load multiplayer-game fixtures from `examples/scenarios/multiplayer-game-mini`.
2. Validate domain types with `adapters/multiplayer_game/schemas` and adapter checks (`make adapters`).
3. Evaluate `proposal.json` and `resolution_options.json` against `adapters/multiplayer_game/policies/default_policy.json`.
4. Confirm explicit concurrency-control outcomes:
   - plans without an authoritative lock or above the tick-drift ceiling are `deny`
   - large contested-player windows emit `warn`
   - wider rollback plans become `require_approval`
5. Run the multiplayer-game quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-multiplayer-game`
6. Validate package coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_multiplayer_game_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

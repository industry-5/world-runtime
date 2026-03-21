# Playbook: World Game Scenarios

## Scenario locations

- `examples/scenarios/world-game-mini/`
- `examples/scenarios/world-game-multi-region/`
- `examples/world-game-authoring/template_bundle.multi-region.v1.json` (WG-M8 authoring template bundle)

## Required files per scenario

- `scenario.json`
- `entities.json`
- `events.json`
- `interventions.json`
- `shocks.json`
- `README.md`

## Authoring conventions

- Keep indicator ids stable and lowercase snake_case.
- Define baseline values for every region and every indicator.
- Ensure every intervention/shock references valid regions and indicators.
- Include at least one tradeoff intervention and at least one approval-sensitive intervention.
- Keep policy pack reference explicit via `policy_pack_ref`.

## Validation

- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_world_game_examples.py tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/adapters/world_game/test_authoring.py`

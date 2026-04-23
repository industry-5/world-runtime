# DA-M7 - Agent coordination and governance

## Objective

Implement `adapter-multi-agent-ai` and `adapter-open-agent-world` through local `M1` to `M3` on top of the completed nine implemented public tracks and the shared standards established in `DA-M2`.

## In Scope

- the first runtime-authoritative `multi_agent_ai` and `open_agent_world` adapter slices, schemas, policies, scenario bundles, and package-local milestone progression
- validation and docs updates required to keep the public portfolio coherent under the shared discovery and bundle contract
- narrowly-scoped supporting fixes needed to preserve the completed `DA-M6` implemented tracks while adding the next pair

## Out Of Scope

- new stable App Server, HTTP API, or SDK surfaces
- widening `supply_ops` or `world_game` into this public series
- new public domains outside `multi_agent_ai` and `open_agent_world`

## Acceptance Highlights

- `adapter-multi-agent-ai` lands a real public slice and advances through local `MA-M1` to `MA-M3`
- `adapter-open-agent-world` lands a real public slice and advances through local `OAW-M1` to `OAW-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline remain green as the public portfolio grows
- touched series/package/root docs remain aligned

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_multiplayer_game_domain.py tests/test_autonomous_vehicle_domain.py`
- package-local and milestone-specific validation added in-thread

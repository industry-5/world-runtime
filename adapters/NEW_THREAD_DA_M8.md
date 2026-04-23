# DA-M8 - Digital twin overlay

## Objective

Implement `adapter-digital-twin` as a host-bound overlay track through local `DT-M1` to `DT-M3`, first against `power_grid`, then `city_ops`, on top of the completed eleven implemented public tracks and the shared standards established in `DA-M2`.

## In Scope

- the first overlay-first `digital_twin` adapter slice, host-binding metadata, and package-local milestone progression
- validation and docs updates required to keep the public portfolio coherent while introducing the overlay exception
- narrowly-scoped supporting fixes needed to preserve the completed `DA-M7` implemented tracks while adding the overlay path

## Out Of Scope

- new stable App Server, HTTP API, or SDK surfaces
- treating `digital_twin` as a standalone public world showcase
- widening `supply_ops` or `world_game` into this public series
- new public domains outside the existing `digital_twin` overlay plan

## Acceptance Highlights

- `adapter-digital-twin` lands a real host-bound overlay slice and advances through local `DT-M1` to `DT-M3`
- the overlay proof is first established against `power_grid` and then extended to `city_ops`
- shared public adapter discovery, the generic non-overlay scenario-bundle baseline, and the explicit overlay boundary remain green as the public portfolio grows
- touched series/package/root docs remain aligned

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_power_grid_domain.py tests/test_city_ops_domain.py tests/test_multi_agent_ai_domain.py tests/test_open_agent_world_domain.py tests/test_operator_workflows.py`
- package-local and milestone-specific validation added in-thread

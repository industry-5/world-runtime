# DA-M4 - Infrastructure and civic coordination

## Objective

Implement `adapter-power-grid` and `adapter-city-ops` through local `M1` to `M3` on top of the completed foundation trio and the shared standards established in `DA-M2`.

## In Scope

- the first runtime-authoritative `power_grid` and `city_ops` adapter slices, schemas, policies, scenario bundles, and package-local milestone progression
- validation and docs updates required to keep the public portfolio coherent under the shared discovery and bundle contract
- narrowly-scoped supporting fixes needed to preserve the completed `DA-M3` foundation trio while adding the next pair

## Out Of Scope

- new stable App Server, HTTP API, or SDK surfaces
- widening `supply_ops` or `world_game` into this public series
- new public domains outside `power_grid` and `city_ops`

## Acceptance Highlights

- `adapter-power-grid` lands a real public slice and advances through local `PG-M1` to `PG-M3`
- `adapter-city-ops` lands a real public slice and advances through local `CO-M1` to `CO-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline remain green as the public portfolio grows
- touched series/package/root docs remain aligned

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py`
- package-local and milestone-specific validation added in-thread

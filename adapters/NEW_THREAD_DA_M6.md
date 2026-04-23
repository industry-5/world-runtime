# DA-M6 - Concurrency and motion safety

## Objective

Implement `adapter-multiplayer-game` and `adapter-autonomous-vehicle` through local `M1` to `M3` on top of the completed seven implemented public tracks and the shared standards established in `DA-M2`.

## In Scope

- the first runtime-authoritative `multiplayer_game` and `autonomous_vehicle` adapter slices, schemas, policies, scenario bundles, and package-local milestone progression
- validation and docs updates required to keep the public portfolio coherent under the shared discovery and bundle contract
- narrowly-scoped supporting fixes needed to preserve the completed `DA-M5` implemented tracks while adding the next pair

## Out Of Scope

- new stable App Server, HTTP API, or SDK surfaces
- widening `supply_ops` or `world_game` into this public series
- new public domains outside `multiplayer_game` and `autonomous_vehicle`

## Acceptance Highlights

- `adapter-multiplayer-game` lands a real public slice and advances through local `MPG-M1` to `MPG-M3`
- `adapter-autonomous-vehicle` lands a real public slice and advances through local `AV-M1` to `AV-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline remain green as the public portfolio grows
- touched series/package/root docs remain aligned

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py`
- package-local and milestone-specific validation added in-thread

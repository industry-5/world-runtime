# DA-M3 - Foundation and legacy parity

## Objective

Bring `adapter-supply-network` and `adapter-air-traffic` to fuller package parity while implementing `adapter-semantic-system` through local `SS-M1` to `SS-M3`, all on top of the shared standards established in `DA-M2`.

## In Scope

- package-local parity work for the existing public proof paths in `adapters/supply_network/` and `adapters/air_traffic/`
- the first runtime-authoritative `semantic_system` adapter, schemas, policy, scenario bundle, and package-local milestone progression
- validation and docs updates required to keep the foundation trio coherent under the `DA-M2` shared discovery and bundle contract

## Out Of Scope

- new stable App Server, HTTP API, or SDK surfaces
- widening `supply_ops` or `world_game` into this public series
- new public domains outside `supply_network`, `air_traffic`, and `semantic_system`

## Acceptance Highlights

- `adapter-supply-network` and `adapter-air-traffic` reach fuller package-local parity rather than staying as legacy carryovers
- `adapter-semantic-system` lands a real public slice and advances through local `SS-M1` to `SS-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline remain green as the foundation trio grows
- touched series/package/root docs remain aligned

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py`
- package-local and milestone-specific validation added in-thread

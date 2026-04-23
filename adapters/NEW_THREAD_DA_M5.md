# DA-M5 - Regulated and market pressure

## Objective

Implement `adapter-lab-science` and `adapter-market-micro` through local `M1` to `M3` on top of the completed foundation/infrastructure quintet and the shared standards established in `DA-M2`.

## In Scope

- the first runtime-authoritative `lab_science` and `market_micro` adapter slices, schemas, policies, scenario bundles, and package-local milestone progression
- validation and docs updates required to keep the public portfolio coherent under the shared discovery and bundle contract
- narrowly-scoped supporting fixes needed to preserve the completed `DA-M4` implemented tracks while adding the next pair

## Out Of Scope

- new stable App Server, HTTP API, or SDK surfaces
- widening `supply_ops` or `world_game` into this public series
- new public domains outside `lab_science` and `market_micro`

## Acceptance Highlights

- `adapter-lab-science` lands a real public slice and advances through local `LS-M1` to `LS-M3`
- `adapter-market-micro` lands a real public slice and advances through local `MM-M1` to `MM-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline remain green as the public portfolio grows
- touched series/package/root docs remain aligned

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py`
- package-local and milestone-specific validation added in-thread

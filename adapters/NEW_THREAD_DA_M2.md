# DA-M2 - Shared Adapter Standards and Generic Validation

## Objective

Generalize public adapter discovery and scenario-bundle validation so the public adapter portfolio can grow without hard-coded legacy assumptions while preserving richer adapter-local proofs.

## In Scope

- shared registry/discovery expectations for public adapter tracks
- generic scenario-bundle contract and validation checklist
- baseline test/script updates needed for scalable public adapter growth
- series/package doc updates needed to keep the new standards explicit

## Out Of Scope

- implementation of new adapter domain code beyond narrow support for shared discovery
- new stable App Server, HTTP API, or SDK surfaces
- widening `supply_ops` or `world_game` into this public series

## Acceptance Highlights

- shared validation is not hard-coded to only the current legacy public adapters
- the generic public scenario-bundle shape is documented and testable
- richer adapters can still keep adapter-specific proofs on top of the generic baseline
- touched series/package/root docs remain aligned

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py`
- any new DA-M2-specific checks added in-thread

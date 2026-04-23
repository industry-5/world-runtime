# CO-M4 - Promotion Hardening

## Objective

Harden `adapter-city-ops` for downstream public promotion readiness while preserving the completed civic-coordination proof slice and avoiding stable-surface widening.

## In Scope

- package-local audit of docs, scenario artifacts, playbook guidance, and validation coverage
- narrow hardening fixes that improve promotion readiness without changing package identity
- package/current-state doc updates needed to capture the actual `CO-M4` outcome

## Out Of Scope

- new stable App Server, HTTP API, or SDK surface work
- reopening completed `CO-M1` through `CO-M3` scope unless a correctness fix requires it
- broadening the package into a general municipal platform surface

## Definition Of Done

- the city-ops package is harder to promote downstream without changing its core proof story
- package docs and changelog reflect the actual `CO-M4` outcome
- root docs remain rollup-only unless top-level public posture changes

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_city_ops_domain.py tests/test_operator_workflows.py`

# PG-M4 - Promotion Hardening

## Objective

Harden `adapter-power-grid` for downstream public promotion readiness while preserving the completed contingency/replay proof slice and avoiding stable-surface widening.

## In Scope

- package-local audit of docs, scenario artifacts, playbook guidance, and validation coverage
- narrow hardening fixes that improve promotion readiness without changing package identity
- package/current-state doc updates needed to capture the actual `PG-M4` outcome

## Out Of Scope

- new stable App Server, HTTP API, or SDK surface work
- reopening completed `PG-M1` through `PG-M3` scope unless a correctness fix requires it
- broadening the package into a market-design or wholesale-trading track

## Definition Of Done

- the power-grid package is harder to promote downstream without changing its core proof story
- package docs and changelog reflect the actual `PG-M4` outcome
- root docs remain rollup-only unless top-level public posture changes

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_power_grid_domain.py tests/test_operator_workflows.py`

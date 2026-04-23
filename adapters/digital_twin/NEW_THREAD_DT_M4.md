# DT-M4 - Promotion Hardening

## Objective

Harden `adapter-digital-twin` for downstream public promotion readiness while preserving the completed host-bound overlay proof slice and avoiding stable-surface widening.

## In Scope

- package-local audit of docs, scenario artifacts, playbook guidance, and validation coverage
- narrow hardening fixes that improve promotion readiness without changing package identity
- package/current-state doc updates needed to capture the actual `DT-M4` outcome

## Out Of Scope

- new stable App Server, HTTP API, or SDK surface work
- reopening completed `DT-M1` through `DT-M3` scope unless a correctness fix requires it
- turning the digital twin package into a standalone showcase world

## Definition Of Done

- the digital-twin package is harder to promote downstream without changing its host-bound overlay proof story
- package docs and changelog reflect the actual `DT-M4` outcome
- root docs remain rollup-only unless top-level public posture changes

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_digital_twin_domain.py tests/test_operator_workflows.py`

# Power Grid Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-power-grid` is the public power-grid package in the World Runtime public domain adapter scenario program.

## Purpose

- prove balancing, contingency response, and cascading infrastructure simulation
- exercise least-bad-choice decision making under critical-infrastructure constraints

## Current State

- current state: promotion-hardened public `PG-M4` slice with adapter contract, schemas, default/scenario policy, contingency-response alternatives, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/power-grid-mini/`
  - `playbooks/adapter-power-grid.md`
- `contingency_options.json` preserves least-bad-response alternatives on top of the shared bundle baseline
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`
- the package now serves as the first host proof surface for `adapter-digital-twin` through host-bound overlay bindings rather than new stable package surfaces

## Working Defaults

- adapter id: `adapter-power-grid`
- package path: `adapters/power_grid`
- scenario path: `examples/scenarios/power-grid-mini`
- milestone code: `PG`

## Contributor Validation Path

Use this package-local bundle when touching the power-grid path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_power_grid_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-power-grid.md`

## Boundaries

- internal milestone ledgers and handoff prompts are intentionally not included in this public export
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the power-grid track should stay focused on balancing, contingencies, and least-bad critical-infrastructure response rather than wholesale market modeling

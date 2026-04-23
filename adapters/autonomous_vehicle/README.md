# Autonomous Vehicle Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-autonomous-vehicle` is the public autonomous-vehicle package in the World Runtime public domain adapter scenario program.

## Purpose

- prove dynamic planning under hard safety constraints in physical-space reasoning
- exercise intervention logic, least-bad choices, and explicit safety boundaries
- keep package-local roadmap, status, and change history inside this package.

## Current State

- current state: released public adapter slice with adapter contract, schemas, default/scenario policy, maneuver alternatives, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/autonomous-vehicle-mini/`
  - `playbooks/adapter-autonomous-vehicle.md`
- `maneuver_options.json` preserves motion-safety alternatives on top of the shared bundle baseline
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`

## Package Docs

- `README.md` - package overview and boundaries
- `ROADMAP.md` - package direction and scope
- `STATUS.md` - current execution ledger
- `CHANGELOG.md` - package release and change history


## Working Defaults

- adapter id: `adapter-autonomous-vehicle`
- package path: `adapters/autonomous_vehicle`
- scenario path: `examples/scenarios/autonomous-vehicle-mini`
- track code: `AV`

## Contributor Validation Path

Use this package-local bundle when touching the autonomous-vehicle path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_autonomous_vehicle_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-autonomous-vehicle.md`

## Boundaries

- package-local roadmap and status live here
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the autonomous-vehicle track should stay focused on motion planning, teleassist intervention, and safety-limited fallback choices rather than broad autonomy platform coverage

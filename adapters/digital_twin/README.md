# Digital Twin Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-digital-twin` is the public digital-twin overlay package in the World Runtime public domain adapter scenario program.

## Purpose

- provide a host-bound overlay track rather than a standalone showcase world
- prove twin-layer simulation and host binding first on `power_grid`, then on `city_ops`
- keep package-local roadmap, status, and change history inside this package.

## Current State

- current state: released public adapter slice with adapter contract, schemas, default/scenario policy, host-binding metadata, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/digital-twin-mini/`
  - `playbooks/adapter-digital-twin.md`
- `host_bindings.json` keeps the overlay boundary explicit across the `power_grid` and `city_ops` host proofs
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`

## Package Docs

- `README.md` - package overview and boundaries
- `ROADMAP.md` - package direction and scope
- `STATUS.md` - current execution ledger
- `CHANGELOG.md` - package release and change history


## Working Defaults

- adapter id: `adapter-digital-twin`
- package path: `adapters/digital_twin`
- scenario path: `examples/scenarios/digital-twin-mini`
- first host targets: `power_grid`, then `city_ops`
- track code: `DT`

## Contributor Validation Path

Use this package-local bundle when touching the digital-twin path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_digital_twin_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-digital-twin.md`

## Boundaries

- package-local roadmap and status live here
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- the overlay must stay host-bound to public host tracks rather than becoming a standalone showcase world
- no stable App Server, HTTP API, or SDK surface is widened by this package

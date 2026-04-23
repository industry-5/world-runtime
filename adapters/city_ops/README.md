# City Ops Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-city-ops` is the public city-operations package in the World Runtime public domain adapter scenario program.

## Purpose

- prove cross-agency incident coordination across transport, utilities, and public response
- exercise one shared operating model spanning multiple civic subdomains
- keep package-local roadmap, status, and change history inside this package.

## Current State

- current state: released public adapter slice with adapter contract, schemas, default/scenario policy, coordination alternatives, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/city-ops-mini/`
  - `playbooks/adapter-city-ops.md`
- `coordination_options.json` preserves civic coordination alternatives on top of the shared bundle baseline
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`
- the package now serves as the second host proof surface for `adapter-digital-twin` through host-bound overlay bindings rather than new stable package surfaces

## Package Docs

- `README.md` - package overview and boundaries
- `ROADMAP.md` - package direction and scope
- `STATUS.md` - current execution ledger
- `CHANGELOG.md` - package release and change history


## Working Defaults

- adapter id: `adapter-city-ops`
- package path: `adapters/city_ops`
- scenario path: `examples/scenarios/city-ops-mini`
- track code: `CO`

## Contributor Validation Path

Use this package-local bundle when touching the city-ops path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_city_ops_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-city-ops.md`

## Boundaries

- package-local roadmap and status live here
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the city-ops track should remain focused on cross-agency civic coordination rather than becoming a general municipal product surface

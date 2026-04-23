# Supply Network Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-supply-network` is the public supply-network package in the World Runtime public domain adapter scenario program.

## Purpose

- prove disruption handling, replay, projection, and simulation under operational pressure
- keep package-local roadmap, status, and change history inside this package.
- serve as one of the implemented public proof paths in the foundation trio

## Current State

- current state: released public adapter slice with adapter contract, schemas, default/scenario policy, replay/simulation bundle artifacts, alternate reroute proofs, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/supply-network-mini/`
  - `playbooks/adapter-supply-network.md`
- `reroute_options.json` now carries package-local alternate tradeoffs on top of the shared bundle baseline

## Package Docs

- `README.md` - package overview and boundaries
- `ROADMAP.md` - package direction and scope
- `STATUS.md` - current execution ledger
- `CHANGELOG.md` - package release and change history


## Working Defaults

- adapter id: `adapter-supply-network`
- package path: `adapters/supply_network`
- scenario path: `examples/scenarios/supply-network-mini`
- track code: `SN`

## Contributor Validation Path

Use this package-local bundle when touching the supply-network path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_supply_network_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-supply-network.md`

## Boundaries

- package-local roadmap and status live here
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the supply-network track should remain distinct from `adapter-supply-ops`

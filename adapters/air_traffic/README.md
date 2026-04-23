# Air Traffic Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-air-traffic` is the safety-constrained public air-traffic package in the World Runtime public domain adapter scenario program.

## Purpose

- prove hard safety constraints, urgency, approvals, and simulation-before-action under operational pressure
- keep package-local roadmap, status, and change history inside this package.
- serve as one of the implemented public proof paths in the foundation trio

## Current State

- current state: released public adapter slice with adapter contract, schemas, default/scenario policy, constrained-alternative review, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/air-traffic-mini/`
  - `playbooks/adapter-air-traffic.md`
- `conflicting_proposals.json` remains the package-local supplemental proof file on top of the shared bundle baseline

## Package Docs

- `README.md` - package overview and boundaries
- `ROADMAP.md` - package direction and scope
- `STATUS.md` - current execution ledger
- `CHANGELOG.md` - package release and change history


## Working Defaults

- adapter id: `adapter-air-traffic`
- package path: `adapters/air_traffic`
- scenario path: `examples/scenarios/air-traffic-mini`
- track code: `AT`

## Contributor Validation Path

Use this package-local bundle when touching the air-traffic path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_air_traffic_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-air-traffic.md`

## Boundaries

- package-local roadmap and status live here
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the air-traffic track remains the high-constraint proof path; it should not be diluted into a generic logistics demo

# Lab Science Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-lab-science` is the public lab-science package in the World Runtime public domain adapter scenario program.

## Purpose

- prove regulated experiment workflows, evidence chains, and policy depth
- exercise provenance-heavy decisions where process integrity is part of the runtime proof

## Current State

- current state: promotion-hardened public `LS-M4` slice with adapter contract, schemas, default/scenario policy, regulated-release alternatives, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/lab-science-mini/`
  - `playbooks/adapter-lab-science.md`
- `release_options.json` preserves regulated release alternatives on top of the shared bundle baseline
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`

## Working Defaults

- adapter id: `adapter-lab-science`
- package path: `adapters/lab_science`
- scenario path: `examples/scenarios/lab-science-mini`
- milestone code: `LS`

## Contributor Validation Path

Use this package-local bundle when touching the lab-science path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_lab_science_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-lab-science.md`

## Boundaries

- internal milestone ledgers and handoff prompts are intentionally not included in this public export
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the lab-science track should remain focused on regulated release, evidence integrity, and deviation governance rather than broad LIMS or clinical operations scope

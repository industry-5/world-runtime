# Semantic System Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-semantic-system` is the public semantic-coherence package in the World Runtime public domain adapter scenario program.

## Purpose

- prove semantic coherence, governed meaning changes, and policy-visible relationship consistency
- exercise provenance and approval boundaries where correctness of meaning matters as much as operational correctness

## Current State

- current state: promotion-hardened public `SS-M4` slice with adapter contract, schemas, default/scenario policy, semantic-conflict alternatives, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/semantic-system-mini/`
  - `playbooks/adapter-semantic-system.md`
- `conflicting_proposals.json` preserves semantic-governance alternatives on top of the shared bundle baseline
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`

## Working Defaults

- adapter id: `adapter-semantic-system`
- package path: `adapters/semantic_system`
- scenario path: `examples/scenarios/semantic-system-mini`
- milestone code: `SS`

## Contributor Validation Path

Use this package-local bundle when touching the semantic-system path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_semantic_system_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-semantic-system.md`

## Boundaries

- internal milestone ledgers and handoff prompts are intentionally not included in this public export
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the semantic-system track should remain focused on governed meaning change and coherence pressure rather than general knowledge-management breadth

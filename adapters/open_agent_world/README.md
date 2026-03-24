# Open Agent World Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-open-agent-world` is the public open-agent-world package in the World Runtime public domain adapter scenario program.

## Purpose

- prove emergent multi-agent governance, intervention, and conflict-management behavior
- exercise open coordination where many agents act on the same projected state under explicit oversight

## Current State

- current state: promotion-hardened public `OAW-M4` slice with adapter contract, schemas, default/scenario policy, intervention alternatives, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/open-agent-world-mini/`
  - `playbooks/adapter-open-agent-world.md`
- `intervention_options.json` preserves bounded governance alternatives on top of the shared bundle baseline
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`

## Working Defaults

- adapter id: `adapter-open-agent-world`
- package path: `adapters/open_agent_world`
- scenario path: `examples/scenarios/open-agent-world-mini`
- milestone code: `OAW`

## Contributor Validation Path

Use this package-local bundle when touching the open-agent-world path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_open_agent_world_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-open-agent-world.md`

## Boundaries

- internal milestone ledgers and handoff prompts are intentionally not included in this public export
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the open-agent-world track should stay focused on shared-world governance, intervention, and conflict management rather than broad sandbox-platform scope

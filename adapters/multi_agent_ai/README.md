# Multi-Agent AI Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-multi-agent-ai` is the public multi-agent AI package in the World Runtime public domain adapter scenario program.

## Purpose

- prove agent proposal, conflict, branching, and review flows inside a governed runtime
- exercise multi-actor coordination where agents can suggest but policy still governs action
- keep package-local roadmap, status, and change history inside this package.

## Current State

- current state: released public adapter slice with adapter contract, schemas, default/scenario policy, coordination-branch alternatives, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/multi-agent-ai-mini/`
  - `playbooks/adapter-multi-agent-ai.md`
- `branch_options.json` preserves reviewed coordination alternatives on top of the shared bundle baseline
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`

## Package Docs

- `README.md` - package overview and boundaries
- `ROADMAP.md` - package direction and scope
- `STATUS.md` - current execution ledger
- `CHANGELOG.md` - package release and change history


## Working Defaults

- adapter id: `adapter-multi-agent-ai`
- package path: `adapters/multi_agent_ai`
- scenario path: `examples/scenarios/multi-agent-ai-mini`
- track code: `MA`

## Contributor Validation Path

Use this package-local bundle when touching the multi-agent AI path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_multi_agent_ai_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-multi-agent-ai.md`

## Boundaries

- package-local roadmap and status live here
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the multi-agent AI track should stay focused on delegated coordination, branching, and review governance rather than broad agent-platform scope

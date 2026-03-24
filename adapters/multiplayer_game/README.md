# Multiplayer Game Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-multiplayer-game` is the public multiplayer-game package in the World Runtime public domain adapter scenario program.

## Purpose

- prove shared-state concurrency, simultaneous intent handling, and synchronization under load
- stress the runtime with live multi-actor updates without turning the package into a proxy for any internal game project

## Current State

- current state: promotion-hardened public `MPG-M4` slice with adapter contract, schemas, default/scenario policy, concurrency-resolution alternatives, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/multiplayer-game-mini/`
  - `playbooks/adapter-multiplayer-game.md`
- `resolution_options.json` preserves concurrency-resolution alternatives on top of the shared bundle baseline
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`

## Working Defaults

- adapter id: `adapter-multiplayer-game`
- package path: `adapters/multiplayer_game`
- scenario path: `examples/scenarios/multiplayer-game-mini`
- milestone code: `MPG`

## Contributor Validation Path

Use this package-local bundle when touching the multiplayer-game path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_multiplayer_game_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-multiplayer-game.md`

## Boundaries

- internal milestone ledgers and handoff prompts are intentionally not included in this public export
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the multiplayer-game track should stay focused on authoritative reconciliation, simultaneous intent handling, and shared-state fairness rather than broad consumer game features

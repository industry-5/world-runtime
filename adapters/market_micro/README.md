# Market Micro Public Adapter Package

_Last updated: 2026-03-23 (America/Chicago)_

`adapter-market-micro` is the public market-micro package in the World Runtime public domain adapter scenario program.

## Purpose

- prove high event intensity, exposure limits, and multi-actor conflict behavior
- exercise risk controls and policy-visible interventions in market-like conditions

## Current State

- current state: promotion-hardened public `MM-M4` slice with adapter contract, schemas, default/scenario policy, market-risk alternatives, replay/simulation artifacts, package-local docs, and playbook guidance
- package assets on disk include:
  - `adapter.py`
  - `schemas/`
  - `policies/default_policy.json`
  - `examples/scenarios/market-micro-mini/`
  - `playbooks/adapter-market-micro.md`
- `risk_options.json` preserves market-risk alternatives on top of the shared bundle baseline
- the package is now registered in `adapters/public_program.py` and available through `AdapterRegistry.with_defaults()`

## Working Defaults

- adapter id: `adapter-market-micro`
- package path: `adapters/market_micro`
- scenario path: `examples/scenarios/market-micro-mini`
- milestone code: `MM`

## Contributor Validation Path

Use this package-local bundle when touching the market-micro path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_market_micro_domain.py tests/test_operator_workflows.py`
- contributor/operator guidance lives in `playbooks/adapter-market-micro.md`

## Boundaries

- internal milestone ledgers and handoff prompts are intentionally not included in this public export
- root docs should keep only rollup pointers for this track
- adapter implementation stays inside the stable `adapters.base.DomainAdapter` contract
- no stable App Server, HTTP API, or SDK surface is widened by this package
- the market-micro track should remain focused on exposure limits, inventory pressure, and desk-risk controls rather than full exchange or brokerage breadth

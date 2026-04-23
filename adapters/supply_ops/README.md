# Supply Ops Domain Package

`adapter-supply-ops` is the fixture-first supply-operations domain package for the orchestration-native path described in the Supply Ops build blueprint.

## Purpose

- provide a fixture-first ERP/WMS-style domain path for commitments, inventory, capacity, and fulfillment orchestration
- prove the runtime can ingest business signals, translate them into proposals, evaluate tradeoffs explicitly, and simulate before action
- keep package-local rollups, execution status, and the rolling kickoff entrypoint inside `adapters/supply_ops/`
- pair with `labs/supply_ops_lab` as the thin operator-facing demo surface once the lab track begins implementation

## Current State

- current state: released fixture-first adapter slice with deterministic translation, policy-covered proposal flow, shared replay/simulation validation, connector-shaped ingress envelope fixtures, and approved-recovery execution evidence framing
- the package is registered in `adapters/registry.py` as `adapter-supply-ops`
- the package now contributes adapter-local schemas, a default policy with all four outcome classes, `translator.py`, `replay.py`, `ingress.py`, `evidence.py`, inbound ERP/WMS fixture packs under `adapters/supply_ops/fixtures/`, and the `examples/scenarios/supply-ops-mini` fixture bundle
- `labs/supply_ops_lab` now provides a thin runnable `SO-P2` preset/result/timeline surface hardened through `SO-P3`, and live connector-backed transport execution is still not implemented

This directory remains the local source of truth for package rollups, implementation status, and public-facing guidance.

## Implemented Path

The current Supply Ops path is intentionally fixture-first and runtime-authoritative:

1. connector-shaped inbound envelopes under `fixtures/ingress/` are validated by `ingress.py` so connector metadata stays explicit while authority still stops at translation-only signal unpacking
2. canonical ERP/WMS-shaped signal bundles under `fixtures/inbound/` are translated into proposal-shaped payloads by `translator.py`
3. translated proposals are checked against `policies/default_policy.json` and still expose the explicit `allow`, `warn`, `require_approval`, and `deny` outcomes
4. the reviewed example scenario in `examples/scenarios/supply-ops-mini/` rebuilds through the shared `ReplayEngine` and `SimpleProjector`
5. `replay.py` derives a risk-only baseline event plus hypothetical recovery events from translated proposals so the shared `SimulationEngine` can validate the recovery path without mutating live runtime state directly
6. `evidence.py` turns the approved recovery path into replay-safe execution evidence that references the existing stable connector surface expectation without claiming transport execution already exists
7. future thin clients or labs should call existing stable runtime/public HTTP surfaces and display results; they should not reimplement translation, policy, replay, simulation, or execution-evidence packaging logic in client code

## Contributor Validation Path

Use this package-local bundle when touching the Supply Ops path:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`
- `python3 -m pytest -q tests/test_supply_ops_ingress.py`
- `python3 -m pytest -q tests/test_supply_ops_translator.py`
- `python3 -m pytest -q tests/test_supply_ops_replay.py`
- `python3 -m pytest -q tests/test_supply_ops_execution_evidence.py`
- contributor/operator guidance lives in `playbooks/adapter-supply-ops.md`

## Boundaries

- package-local roadmap and status live here
- root docs should keep only rollup pointers for this track
- adapter implementation should stay inside the stable `adapters.base.DomainAdapter` contract
- connector-shaped ingress expectations remain fixture-first and should not add live transport execution or new public/runtime API methods
- `labs/supply_ops_lab` should remain thin relative to runtime logic and should use existing stable HTTP surfaces only

## Planned Package Map

- `README.md` - package overview and boundaries
- `ROADMAP.md` - package direction and scope
- `STATUS.md` - current execution ledger and next-thread entrypoint
- `CHANGELOG.md` - package release and change history
- root rollup pointers live in repo-level `README.md`, `STATUS.md`, `ROADMAP.md`, `docs/README.md`, and `adapters/README.md`
- implementation assets now include:
  - `ingress.py`
  - `evidence.py`
  - `translator.py`
  - `replay.py`
  - `fixtures/`


## Working Defaults

- domain identity: `adapter-supply-ops`
- package path: `adapters/supply_ops`
- example scenario path: `examples/scenarios/supply-ops-mini`
- first lab dependency: `labs/supply_ops_lab`
- first implementation pass stays distinct from `adapter-supply-network`

# Playbook: Supply Ops Adapter

## Goal

Run the implemented fixture-first Supply Ops path from translated signal to policy review, replay rebuild, and simulation evidence without changing kernel internals.

## Current State

- current state: implemented fixture-first `SO-M4` adapter slice; the lab now exposes a thin runnable `SO-P2` surface hardened through `SO-P3`
- the adapter now ships connector-shaped ingress envelope fixtures, deterministic ERP/WMS fixture translation, policy-covered proposal flow, replay/simulation validation helpers, approved-recovery execution-evidence packaging, and the `supply-ops-mini` example bundle
- use the package-local and lab-local docs as the source of truth for milestone detail:
  - `adapters/supply_ops/README.md`
  - `adapters/supply_ops/ROADMAP.md`
  - `adapters/supply_ops/STATUS.md`
  - `labs/supply_ops_lab/README.md`
  - `labs/supply_ops_lab/ROADMAP.md`
  - `labs/supply_ops_lab/STATUS.md`

## Steps

1. Start from connector-shaped ingress fixture packs under `adapters/supply_ops/fixtures/ingress/` or canonical signal bundles under `adapters/supply_ops/fixtures/inbound/`.
2. Validate the envelope with `adapters/supply_ops/ingress.py`, then translate the unpacked signal bundle with `adapters/supply_ops/translator.py` and compare the result to `adapters/supply_ops/fixtures/translated/` or `examples/scenarios/supply-ops-mini/proposal.json` for the reviewed recovery path.
3. Evaluate the translated proposal against `adapters/supply_ops/policies/default_policy.json` and confirm the explicit policy outcome (`allow`, `warn`, `require_approval`, or `deny`).
4. Rebuild the example scenario in `examples/scenarios/supply-ops-mini/` through the shared `ReplayEngine` and `SimpleProjector`, then confirm the rebuilt offset matches `projection.json`.
5. Use `adapters/supply_ops/replay.py` to derive a risk-only baseline event plus hypothetical recovery events from a translated proposal, then run the shared `SimulationEngine` to inspect the recovery diff before action.
6. Package the approved recovery path with `adapters/supply_ops/evidence.py` and compare the result to `examples/scenarios/supply-ops-mini/execution_evidence.json` so the execution handoff stays replay-safe and policy-visible before any future transport work.
7. Keep any future lab or client implementation thin and runtime-authoritative; it should call existing stable HTTP/runtime surfaces and render results, not duplicate translation, policy, replay, simulation, or execution-evidence logic in frontend code.

## Validation

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`
- `python3 -m pytest -q tests/test_supply_ops_ingress.py`
- `python3 -m pytest -q tests/test_supply_ops_translator.py`
- `python3 -m pytest -q tests/test_supply_ops_replay.py`
- `python3 -m pytest -q tests/test_supply_ops_execution_evidence.py`

## Boundaries

- connector-shaped ingress expectations only; live transport execution remains future work
- keep the package distinct from `adapter-supply-network`
- no new runtime kernel or public API methods are required for the current slice
- `labs/supply_ops_lab` remains thin and runtime-authoritative in posture; it should not widen beyond its documented `SO-P3` surface without a new lab-local milestone

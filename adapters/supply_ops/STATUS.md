# Supply Ops Domain Status

_Last updated: 2026-03-22 (America/Chicago)_

## Current Phase

- Domain package: `adapter-supply-ops`
- Milestone status: **SO-M4 complete; SO-M5 ready to start**
- Current milestone: **SO-M5 - first stable-surface connector handoff**
- Next recommended milestone: **SO-M5 - first stable-surface connector handoff**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: `docs/milestones/SO-M/SO-M5/PROMPT.md`
- Canonical archived milestone history: `docs/milestones/SO-M/README.md`

## Planned Milestones

- `SO-M0` - package bootstrap and hygiene
- `SO-M1` - adapter contract, schemas, minimal scenario, default policy, registry wiring
- `SO-M2` - fixture-backed ERP/WMS translator and policy-covered proposal flow
- `SO-M3` - replay/simulation hardening, docs, and playbook completion
- `SO-M4` - governed live-ingress preparation and execution evidence
- `SO-M5` - first stable-surface connector handoff

## Current Snapshot

- `SO-M0` governance/bootstrap closeout is complete
- `SO-M1` fixture-first adapter slice is implemented and registered in the default adapter registry
- `SO-M2` adds `translator.py`, inbound ERP/WMS fixture packs, golden translated proposal fixtures, and policy-covered proposal-flow tests for `allow`, `warn`, `require_approval`, and `deny`
- `SO-M3` now adds `replay.py`, shared-kernel projector coverage for Supply Ops events, replay/simulation tests grounded in translated fixtures plus the `supply-ops-mini` scenario, and refreshed package README/playbook guidance for contributors and operators
- `SO-M4` now adds `ingress.py`, connector-shaped inbound envelope fixtures under `fixtures/ingress/`, `evidence.py`, and the reviewed `examples/scenarios/supply-ops-mini/execution_evidence.json` artifact while preserving the completed translator/replay path and stable runtime/public API surfaces
- baseline validation passed on 2026-03-22 for adapter checks, example checks, and targeted pytest coverage including `tests/test_supply_ops_ingress.py`, `tests/test_supply_ops_translator.py`, `tests/test_supply_ops_replay.py`, and `tests/test_supply_ops_execution_evidence.py`
- root repository docs now describe the adapter as an implemented fixture-first `SO-M4` slice while describing the lab as a thin runnable `SO-P2` surface with local `SO-P3` hardening/docs landed
- future stable-surface connector submission and runtime handoff remain unstarted and are the next recommended package milestone
- the domain remains distinct from `adapter-supply-network` and stays on existing stable runtime/public API surfaces

## Validation Baseline

Current `SO-M5` baseline:

1. Package bootstrap:
- `find adapters/supply_ops -maxdepth 1 -type f | sort`

2. Baseline adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`

3. Current package tests:
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`
- `python3 -m pytest -q tests/test_supply_ops_ingress.py`
- `python3 -m pytest -q tests/test_supply_ops_translator.py`
- `python3 -m pytest -q tests/test_supply_ops_replay.py`
- `python3 -m pytest -q tests/test_supply_ops_execution_evidence.py`

4. Milestone consistency:
- `rg -n "SO-M[0-5]" adapters/supply_ops/ROADMAP.md adapters/supply_ops/STATUS.md adapters/supply_ops/NEW_THREAD_KICKOFF_PROMPT.md docs/milestones/SO-M/README.md docs/milestones/SO-M/SO-M5/PROMPT.md`

5. Broader documentation consistency:
- verify root-doc references describe the adapter as an implemented fixture-first package slice and the lab as a thin runnable `SO-P2` surface with local `SO-P3` hardening/docs

## Current SO-M5 Objective

- route the completed `SO-M4` ingress/evidence preparation slice into a first governed connector handoff on existing stable runtime/public surfaces without collapsing into `adapter-supply-network`, widening the public/runtime API surface, or implying lab implementation has started

## Milestone Advancement Discipline

- preserve the completed `SO-M4` translator/fixture/policy/scenario/replay/ingress/evidence/doc boundaries while scoping future work carefully inside `SO-M5`
- keep local rollups inside `adapters/supply_ops/` and canonical milestone history inside `docs/milestones/SO-M/README.md`
- when a milestone closes, update `STATUS.md`, `CHANGELOG.md`, `ROADMAP.md`, `NEW_THREAD_KICKOFF_PROMPT.md`, and the next `NEW_THREAD_SO_Mx.md` together

## Immediate Next Opportunities

- map the approved `SO-M4` execution-evidence package into the first stable-surface connector submission flow without widening shared transport work
- keep execution evidence and outbound handoff replay-safe, policy-visible, and adapter-local in meaning
- keep future lab/client responsibilities thin and runtime-authoritative while the package remains distinct from `adapter-supply-network`

## Known Constraints

- the domain must remain distinct from `adapter-supply-network`
- `labs/supply_ops_lab` now has a thin runnable hardened surface and should not be widened in the next package thread
- the package should stay on existing stable runtime/public API surfaces during `SO-M5` unless a narrower repo-wide change is explicitly planned
- live connector-backed transport execution is not implemented yet and should not bypass the explicit translation and evidence boundaries

## Handoff Checklist For New Thread

1. Re-read `adapters/supply_ops/STATUS.md` and `adapters/supply_ops/ROADMAP.md` from disk.
2. Re-read root `README.md`, `STATUS.md`, `ROADMAP.md`, `docs/README.md`, and `adapters/README.md` before assuming repo-wide posture.
3. Confirm `git status` and avoid reverting unrelated changes.
4. Re-read `docs/milestones/SO-M/README.md`, `docs/milestones/SO-M/SO-M5/PROMPT.md`, and any supplemental package-local detail docs created for the active milestone before implementing.
5. Keep the thread inside the `SO-M5` scope defined in `ROADMAP.md` unless a narrow supporting fix is required for correctness.

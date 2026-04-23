# Supply Ops Domain Roadmap

## Goal

Build `adapter-supply-ops` into a fixture-first supply-operations domain package that can model commitments, inventory, capacity, explicit tradeoff review, and simulation-before-action without changing the stable runtime kernel or public API surfaces.

## Principles

- keep world state and state transitions explicit
- treat inbound business signals as translation inputs, not direct state mutations
- keep policy outcomes visible: `allow`, `warn`, `require_approval`, `deny`
- keep implementation scoped to the adapter contract and existing stable runtime/public API surfaces in v1
- keep detailed milestone history local to this package and use root docs for rollup pointers only

## Milestone Format

Each milestone should capture:

- objective
- scope
- deliverables
- acceptance criteria
- validation commands
- completion evidence

## Milestones

### SO-M0 - Package bootstrap and hygiene

Status: Completed (2026-03-22)

Objective:

- lock package-local roadmap, status, changelog, kickoff prompt, and first milestone brief so they agree on current truth
- make the package discoverable from root rollup docs without implying implementation already exists

Deliverables:

- `adapters/supply_ops/README.md`
- `adapters/supply_ops/ROADMAP.md`
- `adapters/supply_ops/STATUS.md`
- `adapters/supply_ops/CHANGELOG.md`
- `adapters/supply_ops/NEW_THREAD_KICKOFF_PROMPT.md`
- `adapters/supply_ops/NEW_THREAD_SO_M0.md`
- root rollup pointers in repo docs

Acceptance criteria:

- local governance docs exist and agree on milestone names and current state
- the package is explicitly marked planning/bootstrap only
- the kickoff prompt and `NEW_THREAD_SO_M0.md` are decision-complete enough to finish `SO-M0` in a fresh thread
- root docs point to the package without overstating implementation status

Completion evidence:

- package-local docs describe the same active milestone state and handoff model
- root rollup docs point to the package as planning/bootstrap only
- `STATUS.md` names `SO-M1` as the next recommended milestone without implying it has started
- `NEW_THREAD_SO_M1.md` exists and `NEW_THREAD_KICKOFF_PROMPT.md` now points to `SO-M1`

Validation commands:

- `find adapters/supply_ops -maxdepth 1 -type f | sort`
- `rg -n "SO-M[0-3]" adapters/supply_ops/ROADMAP.md adapters/supply_ops/STATUS.md adapters/supply_ops/NEW_THREAD_KICKOFF_PROMPT.md adapters/supply_ops/NEW_THREAD_SO_M0.md`

### SO-M1 - Adapter contract, schemas, minimal scenario, default policy, registry wiring

Status: Completed (2026-03-22)

Objective:

- introduce the actual adapter package under the existing `DomainAdapter` contract with minimal but coherent fixtures and policy assets

Deliverables:

- `adapters/supply_ops/adapter.py`
- `adapters/supply_ops/schemas/entity_types.schema.json`
- `adapters/supply_ops/schemas/event_types.schema.json`
- `adapters/supply_ops/policies/default_policy.json`
- `examples/scenarios/supply-ops-mini/`
- registry wiring and adapter validation coverage

Acceptance criteria:

- `adapter-supply-ops` appears in the default adapter registry
- adapter assets exist and pass adapter checks
- minimal scenario fixtures validate against the adapter taxonomy
- root docs remain rollup-only
- no new runtime kernel or public API surface is added for the first slice

Validation commands:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`
- `make adapters`
- `make examples`

Completion evidence:

- the registry exposes `adapter-supply-ops`
- the package contains the minimal adapter, schemas, policy, and scenario assets described above
- validation covers both adapter discovery and scenario-level coherence
- root docs now describe the adapter as a minimal implemented slice while keeping `labs/supply_ops_lab` planning/bootstrap only
- `STATUS.md` now advances the package to `SO-M2`, `NEW_THREAD_SO_M2.md` exists, and `NEW_THREAD_KICKOFF_PROMPT.md` points to `SO-M2`

### SO-M2 - Fixture-backed ERP/WMS translator and policy-covered proposal flow

Status: Completed (2026-03-22)

Objective:

- add a deterministic translator that maps inbound ERP/WMS-shaped fixtures into proposal-ready runtime payloads while keeping the adapter boundary translation-only

Deliverables:

- `adapters/supply_ops/translator.py`
- inbound fixture samples under `adapters/supply_ops/fixtures/`
- targeted translator and policy coverage
- allow/warn/require-approval/deny examples grounded in supply-ops tradeoffs

Acceptance highlights:

- order/inventory/capacity signals translate deterministically
- no translator path mutates runtime state directly
- policy tests exercise all four outcome classes
- the package remains on existing runtime/public API surfaces only

Validation commands:

- `find adapters/supply_ops -maxdepth 1 -type f | sort`
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`
- `python3 -m pytest -q tests/test_supply_ops_translator.py`

Completion evidence:

- `translator.py` now translates inbound ERP/WMS fixture bundles under `adapters/supply_ops/fixtures/inbound/` into proposal-ready payloads verified against golden outputs under `adapters/supply_ops/fixtures/translated/`
- Supply Ops policy coverage now exercises `allow`, `warn`, `require_approval`, and `deny` without widening the stable runtime kernel or public API surfaces
- the `SO-M1` example proposal remains valid and now matches the translated `require_approval` fixture path
- root rollup docs describe `adapter-supply-ops` as an implemented fixture-first `SO-M2` slice while `labs/supply_ops_lab` remains planning/bootstrap only
- `STATUS.md` now advances the package to `SO-M3`, `NEW_THREAD_SO_M3.md` exists, and `NEW_THREAD_KICKOFF_PROMPT.md` points to `SO-M3`

### SO-M3 - Replay/simulation hardening, docs, and playbook completion

Status: Completed (2026-03-22)

Objective:

- harden the domain path with replay/simulation checks, operator-facing docs, and a credible contributor/onboarding path

Deliverables:

- replay and shared-kernel validation for supply-ops fixtures
- package-local replay helpers for risk-baseline and hypothetical recovery events
- package README/playbook updates aligned to actual implementation
- package-local lab integration notes that preserve the thin-client/runtime-authoritative split while the lab remains bootstrap-only
- milestone closeout evidence in package-local docs

Acceptance highlights:

- supply-ops example fixtures rebuild correctly through the shared replay/projector path
- translated proposals can seed replay/simulation validation without mutating runtime state directly
- docs explain the thin-client/runtime-authoritative split clearly
- playbook and package docs are sufficient for a new contributor to run the path end to end

Validation commands:

- `find adapters/supply_ops -maxdepth 1 -type f | sort`
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`
- `python3 -m pytest -q tests/test_supply_ops_translator.py`
- `python3 -m pytest -q tests/test_supply_ops_replay.py`

Completion evidence:

- `examples/scenarios/supply-ops-mini/events.json` now rebuilds coherently through the shared `ReplayEngine` and `SimpleProjector`, with Supply Ops-specific state captured for commitments, inventory positions, and capacity buckets
- `adapters/supply_ops/replay.py` now derives a risk-only baseline event and hypothetical recovery events from the translated fixture-first path so Supply Ops simulations stay grounded in the existing stable runtime/public surfaces
- package docs and `playbooks/adapter-supply-ops.md` now explain the translator, policy, replay, simulation, and thin-client/runtime-authoritative boundaries without implying lab readiness or live connector-backed ingress
- root rollup docs describe `adapter-supply-ops` as an implemented fixture-first `SO-M3` slice while `labs/supply_ops_lab` remains planning/bootstrap only
- `STATUS.md` now advances the package to `SO-M4`, `NEW_THREAD_SO_M4.md` exists, and `NEW_THREAD_KICKOFF_PROMPT.md` points to `SO-M4`

### SO-M4 - Governed live-ingress preparation and execution evidence

Status: Completed (2026-03-22)

Objective:

- prepare the first connector-shaped ingress and execution-evidence package slice without collapsing into `adapter-supply-network`, bypassing translation, or widening stable runtime/public API surfaces accidentally

Deliverables:

- `ingress.py` plus connector-shaped inbound signal envelope expectations and fixture packs for the next Supply Ops slice
- `evidence.py` plus decision-to-execution evidence framing for approved recovery flows on the existing stable runtime/public surfaces
- reviewed example execution-evidence artifact under `examples/scenarios/supply-ops-mini/`
- package-local docs that keep adapter responsibilities distinct from future lab/client responsibilities

Acceptance highlights:

- inbound signals remain translation inputs rather than direct state mutations
- execution evidence stays replay-safe, policy-visible, and adapter-local in meaning
- package docs keep the lab/client surface thin and runtime-authoritative
- root docs remain rollup-only

Validation commands:

- `find adapters/supply_ops -maxdepth 1 -type f | sort`
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`
- `python3 -m pytest -q tests/test_supply_ops_ingress.py`
- `python3 -m pytest -q tests/test_supply_ops_translator.py`
- `python3 -m pytest -q tests/test_supply_ops_replay.py`
- `python3 -m pytest -q tests/test_supply_ops_execution_evidence.py`

Completion evidence:

- `ingress.py` now validates connector-shaped inbound envelopes under `adapters/supply_ops/fixtures/ingress/` and preserves the translation-only boundary by rejecting direct runtime-state mutation flags or non-inbound misuse
- `translator.py` now accepts the connector-shaped envelope fixtures without changing the existing proposal-only translator output or widening stable runtime/public surfaces
- `evidence.py` now packages approved recovery flows into replay-safe execution evidence grounded in policy results, approval state, and hypothetical recovery events while referencing only existing stable connector surface expectations
- `examples/scenarios/supply-ops-mini/execution_evidence.json` now captures the reviewed approved recovery path end to end and matches the package-local evidence builder output
- root rollup docs describe `adapter-supply-ops` as an implemented fixture-first `SO-M4` slice while `labs/supply_ops_lab` remains planning/bootstrap only
- `STATUS.md` now advances the package to `SO-M5`, `NEW_THREAD_SO_M5.md` exists, and `NEW_THREAD_KICKOFF_PROMPT.md` points to `SO-M5`

### SO-M5 - First stable-surface connector handoff

Status: Ready to start

Objective:

- route the prepared `SO-M4` ingress/evidence package slice into a first governed connector handoff on existing stable runtime/public surfaces without generalizing shared transport work or widening lab/client scope

Deliverables:

- package-local execution-handoff framing that maps approved recovery evidence into the first stable connector submission flow
- targeted fixtures/tests/docs for the first handoff path on existing stable connector/public surfaces
- package-local docs that keep adapter responsibilities distinct from `adapter-supply-network` and future lab/client work

Acceptance highlights:

- existing stable runtime/public surfaces are reused rather than widened
- the package remains distinct from `adapter-supply-network`
- execution handoff remains policy-visible, replay-safe, and adapter-local in meaning
- lab/client posture stays thin and runtime-authoritative

## Notes

- This roadmap is package-local and should carry the detailed milestone history for the Supply Ops track.
- Root repository docs should point here but should not duplicate the detailed milestone sequence.

# Supply Ops Domain Changelog

## 2026-03-22

### SO-M4 - Governed Live-Ingress Preparation And Execution Evidence

Completed:

- added the first governed ingress/evidence preparation slice on top of the completed `SO-M3` translator and replay path:
  - `ingress.py`
  - connector-shaped inbound fixture packs under `fixtures/ingress/`
  - `evidence.py`
  - `examples/scenarios/supply-ops-mini/execution_evidence.json`
- kept the ingress boundary translation-only by validating connector-shaped metadata, preserving the canonical signal-bundle translator path, and rejecting direct runtime-state mutation flags in the new tests
- added approved-recovery execution evidence framing that stays policy-visible, replay-safe, and adapter-local in meaning while pointing only at existing stable connector surface expectations
- refreshed package-local and operator-facing guidance so contributors can trace the path from connector-shaped ingress envelope through translation, policy review, replay/simulation, and execution-evidence packaging without implying live transport execution or lab readiness
- updated package-local and root rollup docs so `adapter-supply-ops` is described as an implemented fixture-first `SO-M4` slice while `labs/supply_ops_lab` remains planning/bootstrap only
- milestone handoff materials advanced to `SO-M5`:
  - `NEW_THREAD_KICKOFF_PROMPT.md` now points to `SO-M5`
  - `NEW_THREAD_SO_M5.md` defines the next implementation thread boundary

Validation:

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

Notes:

- this milestone intentionally stops at connector-shaped ingress expectations, replay-safe execution-evidence packaging, and doc/playbook alignment on existing stable runtime/public surfaces
- live connector transport execution, shared transport generalization, and lab implementation remain deferred to later work

### SO-M3 - Replay/Simulation Hardening, Docs, And Playbook Completion

Completed:

- added Supply Ops replay/simulation hardening on top of the completed `SO-M2` translator slice:
  - `replay.py`
  - shared-kernel projector support for Supply Ops commitment, inventory, and capacity events
  - `tests/test_supply_ops_replay.py`
- refreshed package-local and operator-facing guidance so a new contributor can trace the implemented path from inbound fixture translation through policy review, replay rebuild, and simulation evidence without repo archaeology
- updated package-local and root rollup docs so `adapter-supply-ops` is described as an implemented fixture-first `SO-M3` slice while `labs/supply_ops_lab` remains planning/bootstrap only
- milestone handoff materials advanced to `SO-M4`:
  - `NEW_THREAD_KICKOFF_PROMPT.md` now points to `SO-M4`
  - `NEW_THREAD_SO_M4.md` defines the next implementation thread boundary

Validation:

- `find adapters/supply_ops -maxdepth 1 -type f | sort`
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`
- `python3 -m pytest -q tests/test_supply_ops_translator.py`
- `python3 -m pytest -q tests/test_supply_ops_replay.py`

Notes:

- this milestone intentionally stops at fixture-first replay/simulation validation, package docs/playbook completion, and thin-client/runtime-authoritative guidance
- live connector-backed ingress, runtime execution evidence beyond the current package slice, and lab implementation remain deferred to later work

### SO-M2 - Fixture-Backed ERP/WMS Translator And Policy-Covered Proposal Flow

Completed:

- added the first package-local translator path on top of the existing `SO-M1` adapter slice:
  - `translator.py`
  - deterministic inbound ERP/WMS fixture bundles under `fixtures/inbound/`
  - golden translated proposals under `fixtures/translated/`
- expanded Supply Ops policy coverage so the package now exercises `allow`, `warn`, `require_approval`, and `deny` tradeoff paths on existing stable runtime/public API surfaces only
- preserved the `SO-M1` reviewed recovery example by matching the translated high-expedite fixture path to `examples/scenarios/supply-ops-mini/proposal.json`
- updated package-local and root rollup docs so `adapter-supply-ops` is described as an implemented fixture-first `SO-M2` slice while `labs/supply_ops_lab` remains planning/bootstrap only
- milestone handoff materials advanced to `SO-M3`:
  - `NEW_THREAD_KICKOFF_PROMPT.md` now points to `SO-M3`
  - `NEW_THREAD_SO_M3.md` defines the next implementation thread boundary

Validation:

- `find adapters/supply_ops -maxdepth 1 -type f | sort`
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`
- `python3 -m pytest -q tests/test_supply_ops_translator.py`

Notes:

- this milestone intentionally stops at translation-only fixture ingestion and policy-covered proposal generation
- replay/projector hardening, operator docs/playbook completion, and lab integration notes remain deferred to `SO-M3`

### SO-M1 - Adapter Contract, Schemas, Minimal Scenario, Default Policy, Registry Wiring

Completed:

- added the first functional `adapter-supply-ops` slice on the existing `DomainAdapter` contract:
  - `adapter.py`
  - `schemas/entity_types.schema.json`
  - `schemas/event_types.schema.json`
  - `policies/default_policy.json`
  - `examples/scenarios/supply-ops-mini/`
- registered `adapter-supply-ops` in the default adapter registry and extended baseline validation to cover adapter discovery, scenario coherence, and Supply Ops-specific checks
- updated root-doc rollup wording so the adapter is described as a minimal implemented slice while `labs/supply_ops_lab` remains planning/bootstrap only
- milestone handoff materials advanced to `SO-M2`:
  - `NEW_THREAD_KICKOFF_PROMPT.md` now points to `SO-M2`
  - `NEW_THREAD_SO_M2.md` defines the next implementation thread boundary

Validation:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py`
- `python3 -m pytest -q tests/test_scenario_bundles.py`
- `python3 -m pytest -q tests/test_supply_ops_adapter.py`

Notes:

- this milestone intentionally stops at the fixture-first adapter slice
- translator work, inbound ERP/WMS fixtures, and lab implementation remain deferred to later milestones

### SO-M0 - Package Bootstrap and Hygiene

Completed:

- package-local planning and handoff docs for the new Supply Ops track so the bootstrap set stays internally consistent:
  - `README.md`
  - `ROADMAP.md`
  - `STATUS.md`
  - `CHANGELOG.md`
  - `NEW_THREAD_KICKOFF_PROMPT.md`
  - `NEW_THREAD_SO_M0.md`
- root-doc rollup pointers so the track is discoverable without claiming implementation is already complete
- milestone handoff materials advanced to `SO-M1`:
  - `NEW_THREAD_KICKOFF_PROMPT.md` now points to `SO-M1`
  - `NEW_THREAD_SO_M1.md` defines the first implementation thread boundary

Notes:

- this completed milestone remains documentation/bootstrap only
- no adapter code, schemas, policies, fixtures, or registry wiring were added in this pass

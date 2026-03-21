# World Game Domain Status

_Last updated: 2026-03-14 (America/Chicago)_

## Current Phase

- Domain package: `adapter-world-game`
- Milestone status: **WG-M0-WG-M15 complete**
- Current milestone: **WG-M15 complete (Phase 5 provenance/evidence lineage)**

## Completed Milestones

- WG-M0: Package governance and hygiene bootstrap
- WG-M1: Adapter + schemas + minimal fixture surface
- WG-M2: Domain engine + deterministic replay/branching
- WG-M3: Policy packs + rich scenario content
- WG-M4: Thin studio + docs + smoke path
- WG-M5: Phase 2 contracts + normalization + networked scenario asset
- WG-M6: Deterministic network propagation engine + diagnostics + replay payload parity
- WG-M7: Regional equity analysis + reporting surfaces (`turn`, `compare`, `equity.report`)
- WG-M8: Authoring contracts + deterministic template bundle model (schema validation + template instantiation)
- WG-M9: Authoring workflows (`draft -> validate -> publish -> instantiate`) via runtime methods and CLI entrypoint
- WG-M10: Reusable template packs, docs, and studio authoring UX
- WG-M11: Multi-actor session state, actor roster management, and timeline-safe collaboration context
- WG-M12: Proposal-first planning workflow with adopt/reject lifecycle and branch linkage
- WG-M13: Facilitation stage machine with role-gated advancement and stage-aware validation
- WG-M14: Structured annotations for branches/proposals plus optional comparison summaries
- WG-M15: Provenance inspection for scenarios, proposals, annotations, and branches

## Validation Evidence

- `python3 scripts/check_adapters.py` -> includes `adapter-world-game`
- `python3 scripts/check_examples.py` -> includes world-game scenario checks
- `python3 -m pytest -q tests/test_world_game_authoring.py tests/test_world_game_authoring_workflow.py` -> passed (WG-M9 runtime/CLI authoring workflows, deterministic publish IDs, instantiate path)
- `python3 -m pytest -q tests/test_world_game_authoring.py tests/test_world_game_authoring_workflow.py tests/labs/test_world_game_studio.py` -> passed (WG-M10 template packs + studio authoring UX runtime wiring)
- `python3 -m pytest -q tests/test_world_game_authoring.py tests/test_world_game_examples.py tests/test_world_game_domain.py` -> passed (WG-M8+WG-M9 authoring contracts + deterministic instantiation + runtime compatibility)
- `python3 -m pytest -q tests/test_world_game_network_phase2.py` -> passed (Phase 2 deterministic network/equity validations)
- `python3 -m pytest -q tests/test_world_game_smoke.py tests/test_world_game_examples.py` -> passed
- `python3 -m pytest -q tests/test_world_game_domain.py tests/test_world_game_branches.py tests/test_world_game_replay.py tests/test_world_game_compare.py tests/test_world_game_policies.py` -> passed
- `python3 -m pytest -q tests/test_world_game_collaboration.py` -> passed (WG-M11 through WG-M15 collaboration workflow, stage gating, annotation lifecycle, provenance inspection)
- `make protocol-compat` -> passed
- `make public-api-compat` -> passed

## Next Milestone Candidate

- Deferred follow-up: automatic persisted collaboration storage/indexing beyond manual session bundle export/import

## Notes

- `adapter-world-game` is the World Game domain/runtime authority behind the Studio Next showcase surface.
- Root repository `ROADMAP.md` and `STATUS.md` contain rollup pointers only; detailed WG tracking remains domain-local.
- For new implementation threads, use `adapters/world_game/NEW_THREAD_KICKOFF_PROMPT.md`.
- WG-M9 landed additive runtime methods in `core/app_server.py` (`world_game.authoring.*`) plus deterministic workflow helpers in `core/domains/world_game.py`.
- WG-M9 added authoring CLI workflow entrypoint `scripts/world_game_authoring.py` with `template-list`, `scaffold`, `validate`, `publish`, and `instantiate`.
- Protocol/public API runtime-call docs now include `world_game.authoring.*` methods.
- WG-M10 added reusable template packs:
  - `examples/world-game-authoring/template_bundle.multi-region-stress.v1.json`
  - `examples/world-game-authoring/template_bundle.resilience-first-regional-planning.v1.json`
- WG-M10 added in-domain authoring playbooks:
  - `adapters/world_game/playbooks/template-authoring-rules.md`
  - `adapters/world_game/playbooks/library-authoring-rules.md`
  - `adapters/world_game/playbooks/publish-instantiate-workflow.md`
- WG-M10 extended `labs/world_game_studio` with authoring UX:
  - template pack browsing (`world_game.authoring.template.list`)
  - draft create/edit/validate/publish (`world_game.authoring.draft.*`, `world_game.authoring.bundle.publish`)
  - instantiate + load generated scenarios (`world_game.authoring.bundle.instantiate` -> `world_game.scenario.load`)
- WG-M10 added a supporting correctness fix: bundle instantiation now returns `scenario_payload` and file outputs write raw scenario payloads (runtime-load compatible) instead of normalized internal state.
- WG-M11 through WG-M15 added additive collaboration modules under `adapters/world_game/collaboration/` for:
  - session state / actor roles
  - proposals
  - facilitation stage gating
  - annotations
  - provenance
- WG-M11 through WG-M15 added runtime methods in `core/app_server.py` and `adapters/world_game/service.py` for:
  - `world_game.session.*`
  - `world_game.proposal.*`
  - `world_game.annotation.*`
  - `world_game.provenance.inspect`
- Additive WG-P5 follow-on added collaboration durability runtime methods:
  - `world_game.session.export` (bundle export + optional file write)
  - `world_game.session.import` (bundle import/rehydration for a target runtime session)
- WG-M11 through WG-M15 extended `labs/world_game_studio` with thin collaboration UX:
  - session bootstrap
  - actor roster management
  - stage controls
  - proposal create/submit/adopt
  - branch-targeted annotations
  - provenance inspection

## Risks / Deferred Follow-Ups

- Risk: flow/stock dynamics are intentionally deterministic and linear (no optimizer/stochastic calibration); scenarios with nonlinear resource coupling still require manual coefficient tuning.
- Risk: Phase 2 enforces DAG-only dependency graphs; real-world cyclic networks are currently blocked by contract and need explicit milestone design.
- Risk: WG-M8 authoring schema validation currently relies on `jsonschema.RefResolver`, which is deprecated upstream and should migrate to `referencing` APIs before a future dependency major upgrade.
- Deferred: add dedicated schema validation tests for `adapters/world_game/schemas/scenario.schema.json` against Phase 2 fixtures.
- Deferred: extend studio UI from JSON-first rendering to comparative charts for regional tradeoff and disparity trends across 3+ branches.
- Deferred: evaluate whether `world_game.network.inspect` should expose historical turn snapshots (currently latest-turn diagnostics only).
- Deferred: add a studio-side persisted draft history/version timeline (current draft editor is session-local JSON state).
- Deferred: add automatic persisted storage/indexing for World Game collaboration bundles; current durability path is manual `world_game.session.export` / `world_game.session.import`.

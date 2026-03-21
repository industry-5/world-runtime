# World Game Domain Roadmap

## Goal

Evolve `adapter-world-game` into the runtime-native, policy-governed, branch-first public showcase planning domain for `world-runtime`.

## Milestone Format

Each milestone includes:

- objective
- scope
- deliverables
- acceptance criteria
- validation commands
- completion evidence

## Milestones

### WG-M0 - Package governance and hygiene bootstrap

Status: Completed (2026-03-11)

Objective:

- establish domain-local roadmap/status hygiene and root-level rollup pointers.

Deliverables:

- `adapters/world_game/ROADMAP.md`
- `adapters/world_game/STATUS.md`
- root rollup references in repository `ROADMAP.md` and `STATUS.md`

### WG-M1 - Adapter + schemas + minimal fixture surface

Status: Completed (2026-03-11)

Objective:

- introduce the new adapter contract surface and schema bundle without breaking existing adapters.

Deliverables:

- `adapters/world_game/adapter.py`
- adapter-level schemas and default policy
- minimal scenario seed in `examples/scenarios/world-game-mini/`
- adapter registry/check integration

### WG-M2 - Domain engine + deterministic replay/branching

Status: Completed (2026-03-11)

Objective:

- implement canonical world-game domain logic with deterministic turn, branch, replay, and comparison flows.

Deliverables:

- `core/domains/world_game.py`
- `world_game.*` runtime methods in `core/app_server.py`
- deterministic replay/branching/comparison tests
- policy-gated turn execution before canonical commit

Acceptance highlights:

- branch isolation for sibling branches
- replay parity for ordered turn events
- structured comparison report output for 2+ branches

### WG-M3 - Policy packs + rich scenario content

Status: Completed (2026-03-11)

Objective:

- add meaningful policy packs and scenario packs (`world-game-mini`, `world-game-multi-region`) with explicit tradeoffs.

Deliverables:

- policy packs under `adapters/world_game/policies/`
- scenario packs under `examples/scenarios/world-game-mini/` and `examples/scenarios/world-game-multi-region/`
- fixture catalogs under `adapters/world_game/fixtures/`
- policy and example integrity tests/checks

Acceptance highlights:

- deterministic `warn`, `require_approval`, and `deny` paths reachable
- multi-region scenario includes cross-region spillover tradeoffs
- scenario assets validate in script and tests

### WG-M4 - Thin studio + docs + smoke path

Status: Completed (2026-03-11)

Objective:

- ship a thin studio client, world-game playbooks, and smoke coverage over runtime APIs.

Deliverables:

- `labs/world_game_studio/` thin client and proxy server
- playbooks: adapter usage, scenario authoring, branching/replay
- smoke test covering load -> turn -> branch -> compare -> replay

Acceptance highlights:

- frontend contains no scoring/branch business logic
- studio uses runtime methods only (`world_game.*`)
- legacy FEW lab surface removed so the thin studio remains the only public world-game lab

### WG-M5 - Phase 2 contracts + normalization + scenario assets

Status: Completed (2026-03-11)

Objective:

- add additive Phase 2 scenario contract fields and deterministic normalization/validation for networked modeling.

Deliverables:

- optional scenario fields: `dependency_graph`, `resource_stocks`, `resource_flows`, `spillover_rules`, `equity_dimensions`
- DAG-only graph validation and reference/bounds hardening in `core/domains/world_game.py`
- upgraded canonical networked fixture: `examples/scenarios/world-game-multi-region/scenario.json`

Acceptance highlights:

- unknown node/region/indicator references in Phase 2 fields fail normalization
- invalid capacities/bounds fail normalization
- dependency graph cycles fail normalization (DAG-only v1 rule)

### WG-M6 - Deterministic network propagation engine

Status: Completed (2026-03-11)

Objective:

- execute deterministic propagation over direct effects, stocks, flows, and spillovers with replay-safe diagnostics.

Deliverables:

- deterministic turn pipeline (direct effects -> stock update -> constrained flows -> spillovers -> scoring/policy)
- branch diagnostics payload for stock deltas, saturated edges, unmet demand, conservation, spillover contributions
- replay event payload includes propagation artifacts for parity checks

Acceptance highlights:

- same scenario/actions produce identical propagation outputs
- constrained flow clipping and conservation checks surface in diagnostics
- replay parity covers network diagnostics and equity payloads

### WG-M7 - Regional equity analysis + reporting surfaces

Status: Completed (2026-03-11)

Objective:

- add branch-level regional equity analysis and expose it through runtime/reporting surfaces.

Deliverables:

- equity metrics: per-region normalized outcomes, disparity spread/variance, baseline trend, winners/losers
- integrated outputs in `world_game.turn.run` and `world_game.branch.compare`
- new runtime methods: `world_game.network.inspect`, `world_game.equity.report`
- studio readability update for regional tradeoff emphasis

Acceptance highlights:

- branch comparison summary includes explicit regional tradeoff tables
- equity report is stable/deterministic across repeated runs
- legacy scenarios remain valid in direct-effects-only mode

### WG-M8 - Authoring contracts and template model

Status: Completed (2026-03-11)

Objective:

- establish explicit contracts for scenario/indicator/intervention/shock authoring and reusable template composition.

Scope:

- Phase 3 authoring foundation only (no facilitation/multiplayer ingestion work).

Deliverables:

- authoring schemas for:
  - scenario templates
  - indicator registries
  - intervention libraries
  - shock libraries
  - template instantiation bundles
- placeholder/parameter model for reusable templates (for region count, indicator sets, policy pack refs)
- draft/published bundle metadata with deterministic versioning fields

Acceptance highlights:

- a template bundle validates without requiring immediate runtime execution
- a template bundle can be deterministically instantiated into a concrete scenario payload
- schema validation errors are author-facing and path-specific (no generic failure blobs)

Validation commands:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_world_game_examples.py tests/test_world_game_domain.py`

Completion evidence:

- Added authoring schemas: `scenario_template`, `indicator_registry`, `intervention_library`, `shock_library`, `template_bundle`
- Added deterministic authoring helpers in `core/domains/world_game.py`:
  - `validate_world_game_template_bundle`
  - `load_world_game_template_bundle`
  - `instantiate_world_game_template_bundle`
- Added authoring template bundle example:
  - `examples/world-game-authoring/template_bundle.multi-region.v1.json`
- Added WG-M8 validation coverage:
  - `tests/test_world_game_authoring.py`

### WG-M9 - Authoring workflows (draft -> validate -> publish -> instantiate)

Status: Completed (2026-03-11)

Objective:

- provide executable authoring workflows so scenario packs can be created/iterated without manual JSON surgery.

Scope:

- runtime/CLI workflows for authoring lifecycle, preserving backward compatibility with current scenario assets.

Deliverables:

- runtime authoring methods:
  - `world_game.authoring.template.list`
  - `world_game.authoring.draft.create`
  - `world_game.authoring.draft.validate`
  - `world_game.authoring.bundle.publish`
  - `world_game.authoring.bundle.instantiate`
- deterministic validation pipeline for authoring bundles (schema + semantic checks)
- authoring CLI entrypoint for scaffold/validate/publish/instantiate operations
- compatibility guardrails so existing scenarios continue to run unchanged

Acceptance highlights:

- authoring workflow can generate a valid new scenario from a template in one deterministic path
- published bundle IDs/versioning are stable and reproducible for identical inputs
- invalid drafts fail before publish with explicit remediation messages

Validation commands:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_world_game_authoring.py tests/test_world_game_authoring_workflow.py`
- `python3 -m pytest -q tests/test_world_game_smoke.py tests/test_world_game_examples.py`
- `make protocol-compat`
- `make public-api-compat`

Completion evidence:

- Added runtime authoring methods in `core/app_server.py`:
  - `world_game.authoring.template.list`
  - `world_game.authoring.draft.create`
  - `world_game.authoring.draft.validate`
  - `world_game.authoring.bundle.publish`
  - `world_game.authoring.bundle.instantiate`
- Added workflow helpers in `core/domains/world_game.py`:
  - `list_world_game_template_bundles`
  - `create_world_game_template_bundle_draft`
  - `validate_world_game_template_bundle_workflow`
  - `publish_world_game_template_bundle`
- Added authoring CLI workflow entrypoint:
  - `scripts/world_game_authoring.py` (`template-list`, `scaffold`, `validate`, `publish`, `instantiate`)
- Added WG-M9 runtime/CLI coverage:
  - `tests/test_world_game_authoring_workflow.py`
- Updated protocol and public API runtime-call docs to include `world_game.authoring.*`.

### WG-M10 - Reusable template packs, docs, and studio authoring UX

Status: Completed (2026-03-11)

Objective:

- ship reusable scenario templates and first-class authoring ergonomics for operators/researchers.

Scope:

- template content library + docs + thin studio authoring UX wiring.

Deliverables:

- reusable template packs for at least:
  - FEW advanced baseline
  - multi-region dependency stress test
  - resilience-first regional planning
- authoring docs/playbooks:
  - template authoring rules
  - indicator/intervention/shock library authoring rules
  - publish/instantiate workflow
- studio updates to:
  - browse template packs
  - create/edit draft authoring bundles
  - validate and instantiate scenario outputs
- smoke path from template selection to instantiated scenario execution

Acceptance highlights:

- new scenario creation path does not require hand-editing multiple raw files
- instantiated scenarios remain replay-safe and branch-comparison compatible
- template packs are reusable across multiple region/indicator configurations

Validation commands:

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_world_game_smoke.py tests/test_world_game_examples.py tests/labs/test_world_game_studio.py`

Completion evidence:

- Added reusable template packs:
  - `examples/world-game-authoring/template_bundle.multi-region-stress.v1.json`
  - `examples/world-game-authoring/template_bundle.resilience-first-regional-planning.v1.json`
- Added WG-M10 authoring playbooks:
  - `adapters/world_game/playbooks/template-authoring-rules.md`
  - `adapters/world_game/playbooks/library-authoring-rules.md`
  - `adapters/world_game/playbooks/publish-instantiate-workflow.md`
- Extended studio authoring UX in `labs/world_game_studio/`:
  - template pack browsing
  - draft create/edit/validate/publish
  - instantiate-and-load scenario flow
- Added/updated WG-M10 validation coverage:
  - `tests/test_world_game_authoring.py`
  - `tests/test_world_game_authoring_workflow.py`
  - `tests/test_world_game_smoke.py`
  - `tests/labs/test_world_game_studio.py`

### WG-M11 - Multi-actor session model

Status: Completed (2026-03-13)

Objective:

- introduce actor-aware World Game sessions, explicit collaboration state, and timeline-safe event attribution without breaking single-user scenario flows.

Deliverables:

- additive collaboration state in World Game session context:
  - `session_meta`
  - `actors`
  - `timeline`
  - `proposals`
  - `annotations`
  - `facilitation_state`
  - `provenance`
- runtime methods:
  - `world_game.session.create`
  - `world_game.session.get`
  - `world_game.session.actor.add`
  - `world_game.session.actor.remove`
  - `world_game.session.actor.list`
- role/capability model for `facilitator`, `analyst`, `observer`, `approver`

Acceptance highlights:

- collaboration sessions are durable in World Game service state
- actor-aware actions can attribute `actor_id`
- single-user scenario load and simulation remain valid without collaboration setup
- every state-changing collaboration action appends a timeline-safe event

### WG-M12 - Proposal and deliberation workflow

Status: Completed (2026-03-13)

Objective:

- make proposals the primary collaborative planning object before branch mutation.

Deliverables:

- runtime methods:
  - `world_game.proposal.create`
  - `world_game.proposal.update`
  - `world_game.proposal.get`
  - `world_game.proposal.list`
  - `world_game.proposal.submit`
  - `world_game.proposal.adopt`
  - `world_game.proposal.reject`
- proposal lifecycle support for `draft`, `submitted`, `adopted`, `rejected`, `archived`
- proposal-to-branch linkage with additive provenance references

Acceptance highlights:

- proposals can exist before branch mutation
- proposal adoption creates or links a branch without mutating the baseline directly
- rejected proposals preserve history and actor attribution
- proposal lineage is inspectable through provenance records

### WG-M13 - Facilitation mechanics

Status: Completed (2026-03-13)

Objective:

- represent workshop progression as a deterministic session stage machine.

Deliverables:

- runtime methods:
  - `world_game.session.stage.get`
  - `world_game.session.stage.set`
  - `world_game.session.stage.advance`
- explicit stages:
  - `setup`
  - `proposal_intake`
  - `deliberation`
  - `selection`
  - `simulation`
  - `review`
  - `closed`
- stage-gated validation for proposal adoption and simulation actions when collaboration mode is enabled

Acceptance highlights:

- invalid transitions fail predictably
- facilitator/approver capabilities govern stage advancement
- backward-compatible flows remain open when collaboration is not enabled

### WG-M14 - Annotations and structured commentary

Status: Completed (2026-03-13)

Objective:

- preserve structured human interpretation around branches, proposals, and related artifacts.

Deliverables:

- runtime methods:
  - `world_game.annotation.create`
  - `world_game.annotation.list`
  - `world_game.annotation.update`
  - `world_game.annotation.archive`
- annotation target contract:
  - `target_type`
  - `target_id`
- annotation types for risk/opportunity/assumption/disagreement/evidence-gap/facilitator-note

Acceptance highlights:

- annotations are actor-attributed
- annotations can target branch/proposal/session-level artifacts
- branch comparisons can optionally include branch annotation summaries

### WG-M15 - Provenance and evidence lineage

Status: Completed (2026-03-13)

Objective:

- add traceable provenance from authored scenario inputs through proposals, annotations, and branch outcomes.

Deliverables:

- runtime method:
  - `world_game.provenance.inspect`
- provenance records for scenarios, proposals, annotations, and branches
- authored template lineage capture from scenario metadata into runtime provenance

Acceptance highlights:

- branch outcomes can trace back to scenario and proposal lineage
- evidence references on proposals and annotations remain inspectable
- provenance records remain additive metadata blocks rather than a separate graph engine

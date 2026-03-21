# World Game Studio Next Roadmap

## Goal

Build `world_game_studio_next` into the modern Dymaxion-first, branch-first, policy-aware planning studio for `adapter-world-game`.

This studio program should:

- keep `adapters/world_game` as the domain and runtime source of truth
- treat `labs/world_game_studio` as retired historical context rather than an active migration dependency
- deliver a map-centered planning experience for evidence, branching, replay, comparison, and facilitation

## Boundaries

The studio owns:

- shell layout and navigation
- user interaction design and workflows
- Dymaxion visualization and layer rendering
- client-side adapters for runtime payloads
- design system implementation
- UX for compare, replay, provenance, and facilitation

The studio does not own:

- simulation rules
- policy logic
- canonical scoring behavior
- branch or replay semantics
- authoring schema or scenario truth unless a milestone explicitly defines additive support work

Additive runtime or domain work is in scope only when required to support the studio cleanly.

## Principles

- Keep the client thin relative to runtime logic.
- Put the Dymaxion canvas at the center of gravity early.
- Prefer contract-first seams over ad hoc payload shaping.
- Do not reintroduce dependencies on the retired `labs/world_game_studio` surface.
- Treat compare, replay, evidence, and facilitation as first-class product pillars.
- Keep the product tone aligned with planetary stewardship rather than battle-management metaphors.

## Milestone Format

Each milestone includes:

- objective
- scope
- intended user-visible outcome
- deliverables
- client architecture work
- runtime methods expected to be consumed
- likely touched areas
- data/topology/layer dependencies
- out of scope
- acceptance criteria
- validation commands
- completion evidence
- suggested next milestone

## Milestones

### WG-P0 - Program bootstrap and hygiene

Status: Completed (2026-03-13)

Objective:

- establish the new `world_game_studio_next` program surface, migration stance, and thread-ready planning hygiene.

Scope:

- create studio-local roadmap, status, changelog, and kickoff prompt
- establish the relationship between `world_game_studio_next`, legacy `world_game_studio`, and `adapters/world_game`
- mirror the external design docs into `scratch/world-game-design-docs`

Intended user-visible outcome:

- contributors can open a new thread for `WG-P0` or `WG-P1` and immediately understand where the new studio work lives, which docs govern it, and which implementation surface is active.

Deliverables:

- `labs/world_game_studio_next/ROADMAP.md`
- `labs/world_game_studio_next/STATUS.md`
- `labs/world_game_studio_next/CHANGELOG.md`
- `labs/world_game_studio_next/NEW_THREAD_KICKOFF_PROMPT.md`
- `scratch/world-game-design-docs/` mirror with index file

Client architecture work:

- no production client code yet
- define the architectural envelope and milestone breakdown for later execution threads

Runtime methods expected to be consumed:

- none required for implementation
- document future dependency on `world_game.*` runtime methods only

Likely touched areas:

- `labs/world_game_studio_next/`
- `scratch/world-game-design-docs/`

Data/topology/layer dependencies:

- reference only; no contracts implemented yet
- milestones must point to the mirrored design docs as local planning inputs

Out of scope:

- scaffolding the new studio application
- changing `labs/world_game_studio`
- changing runtime/domain behavior
- updating root rollup docs unless a later consistency pass requires it

Acceptance criteria:

- the new studio-local docs exist and follow the repo's roadmap/status/changelog hygiene pattern
- the migration stance between old and new studio surfaces is explicit
- the kickoff prompt is decision-complete enough to drive one milestone per thread
- the mirrored design docs exist under `scratch/world-game-design-docs`
- there is no ambiguity about `adapters/world_game` remaining the domain source of truth

Validation commands:

- `find labs/world_game_studio_next -maxdepth 1 -type f | sort`
- `find scratch/world-game-design-docs -maxdepth 1 -type f | sort`
- `rg -n "WG-P[0-6]" labs/world_game_studio_next/ROADMAP.md labs/world_game_studio_next/STATUS.md labs/world_game_studio_next/NEW_THREAD_KICKOFF_PROMPT.md`
- `rg -n "legacy|thin-client|source of truth|world_game_studio_next" labs/world_game_studio_next/*.md`

Completion evidence:

- studio-local planning docs and kickoff prompt created
- mirrored design-doc reference path created under `scratch/`
- milestone IDs and migration language aligned across all new docs

Suggested next milestone:

- `WG-P1 - Topology, geometry, and layer contracts`

### WG-P1 - Topology, geometry, and layer contracts

Status: Completed (2026-03-13)

Objective:

- lock the semantic and rendering contracts required for the studio so later frontend milestones can execute without reopening topology, Dymaxion-asset, or layer-model decisions.

Scope:

- define the canonical gameplay region and adjacency strategy
- define the Dymaxion asset package shape and versioning stance
- define layer registries, render contracts, scenario layer manifests, and map adapter boundaries
- identify any additive runtime/domain contract work required for the studio

Intended user-visible outcome:

- the future studio can rely on stable region IDs, map assets, and layer semantics, making the Dymaxion canvas and inspector behavior predictable across scenarios and branches.

Deliverables:

- studio-side contract docs or types for map render state, layer registry, and adapter boundaries
- domain-side contract plan for semantic region registry, adjacency registry, and geometry package location
- explicit mapping between scenario/runtime payloads and studio layer data objects
- milestone-local validation checklist for topology and layer invariants

Client architecture work:

- define `CanvasRenderState`
- define layer definition, layer data source, render spec, and provenance shapes
- define adapter seams such as `mapGeometryAdapter`, `mapScenarioAdapter`, `mapBranchAdapter`, `mapCompareAdapter`, `mapReplayAdapter`, and `mapAnnotationAdapter`

Runtime methods expected to be consumed:

- `world_game.scenario.list`
- `world_game.scenario.load`
- `world_game.turn.run`
- `world_game.branch.compare`
- `world_game.replay.run`
- `world_game.network.inspect`
- `world_game.equity.report`
- `world_game.annotation.create`
- `world_game.provenance.inspect`
- additive methods only if needed for topology manifests or layer metadata

Likely touched areas:

- `labs/world_game_studio_next/` contract docs or type definitions
- `adapters/world_game/topology/` for semantic registries if created in this milestone
- `adapters/world_game/README.md` or package-local docs only if interface truth must be documented there

Data/topology/layer dependencies:

- `scratch/world-game-design-docs/05 CANVAS_INTERACTION_SPEC.md`
- `scratch/world-game-design-docs/06 DYMAXION_MAP_TECH_SPEC.md`
- `scratch/world-game-design-docs/07 REGION_TOPOLOGY_SPEC.md`
- `scratch/world-game-design-docs/08 DATA_LAYER_SPEC.md`
- `scratch/world-game-design-docs/09 FRONTEND_IMPLEMENTATION_PLAN.md`

Out of scope:

- bootable application scaffold
- actual Dymaxion rendering implementation
- compare/replay UI implementation
- collaboration persistence implementation

Acceptance criteria:

- canonical region, adjacency, and geometry-package placement are explicitly chosen
- the split between semantic topology assets and render geometry is explicit
- layer contracts are typed and stable enough for implementation without reopening product semantics
- the mapping from runtime outputs to layer objects is defined for scenario, branch, compare, replay, annotation, and provenance views
- any required additive runtime/domain follow-ons are listed explicitly rather than implied

Validation commands:

- `rg -n "CanvasRenderState|LayerDefinition|layer manifest|mapGeometryAdapter|mapScenarioAdapter" labs/world_game_studio_next`
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- milestone-specific topology contract review checklist captured in docs

Completion evidence:

- contract files/docs created:
  - `labs/world_game_studio_next/contracts/map_contracts.ts`
  - `labs/world_game_studio_next/contracts/WG-P1_TOPOLOGY_GEOMETRY_DECISIONS.md`
  - `labs/world_game_studio_next/contracts/WG-P1_RUNTIME_LAYER_MAPPING.md`
  - `labs/world_game_studio_next/contracts/WG-P1_VALIDATION_CHECKLIST.md`
  - `labs/world_game_studio_next/assets/world_game_map/v1/README.md`
  - `adapters/world_game/topology/README.md`
  - `adapters/world_game/topology/topology.contract.v1.json`
  - `adapters/world_game/topology/scenario_bindings/world-game-multi-region.binding.v1.json`
- unresolved runtime/domain contract gaps listed explicitly in WG-P1 decision and mapping docs
- later canvas and layer milestones no longer depend on open topology placement or adapter-boundary decisions

Suggested next milestone:

- `WG-P2 - Studio platform foundation`

### WG-P2 - Studio platform foundation

Status: Completed (2026-03-13)

Objective:

- create the permanent application skeleton for `world_game_studio_next` with a stable shell, state model, runtime service layer, and design-token baseline.

Scope:

- scaffold the new app, build/test harness, route shell, state providers, and runtime service modules
- define canonical studio state domains for scenario, session, branch, selection, layers, compare, replay, and notifications
- establish the shell regions without attempting full feature parity

Intended user-visible outcome:

- the new studio boots, renders the permanent shell, and can host future map and workflow features without replacing its architectural foundation.

Deliverables:

- modern app scaffold under `labs/world_game_studio_next`
- build and test commands
- shell layout: top bar, left rail, center workspace, right inspector, bottom dock
- initial design tokens and UI primitives
- runtime service layer with normalized call helpers
- canonical client state model and provider wiring

Client architecture work:

- app entrypoint and routing
- service modules for scenario, session, proposal, branch, replay, annotation, provenance, and authoring
- store/state slices for selection, layers, compare, replay, and async request lifecycle
- shared error/loading/notification UX

Runtime methods expected to be consumed:

- `world_game.scenario.list`
- `world_game.scenario.load`
- `world_game.session.create`
- `world_game.session.get`
- `world_game.branch.create`
- `world_game.branch.compare`
- `world_game.replay.run`
- `world_game.proposal.create`
- `world_game.proposal.submit`
- `world_game.proposal.adopt`
- `world_game.annotation.create`
- `world_game.provenance.inspect`
- `world_game.authoring.template.list`

Likely touched areas:

- `labs/world_game_studio_next/package.json` or equivalent app manifest
- `labs/world_game_studio_next/src/`
- studio-local tests
- studio-local README if needed for run instructions

Data/topology/layer dependencies:

- `WG-P1` contracts must be accepted or explicitly stubbed
- no final map asset implementation required yet, but the shell must reserve the canvas center and inspector/dock semantics

Out of scope:

- final Dymaxion interaction model
- map-driven proposal authoring
- replay timeline behavior
- collaboration durability/export
- cutover from legacy studio

Acceptance criteria:

- the new studio boots locally with deterministic install/run steps
- the permanent shell renders and remains stable across route/state changes
- the client state model is centralized rather than fragmented across panels
- runtime service boundaries are explicit and thin relative to runtime logic
- basic shell-level tests and build commands pass

Validation commands:

- studio build command chosen in this milestone
- studio test command chosen in this milestone
- `python3 -m pytest -q tests/labs/test_world_game_studio.py` only if legacy references are intentionally preserved during migration checks
- milestone-specific smoke tests for shell render and service-layer basics

Completion evidence:

- app scaffold and shell committed:
  - `labs/world_game_studio_next/index.html`
  - `labs/world_game_studio_next/server.py`
  - `labs/world_game_studio_next/src/app/`
  - `labs/world_game_studio_next/src/styles/`
- canonical state and runtime service seams landed:
  - `labs/world_game_studio_next/src/state/store.js`
  - `labs/world_game_studio_next/src/services/`
- deterministic studio-local build/test harness landed:
  - `labs/world_game_studio_next/scripts/build_static.py`
  - `tests/labs/test_world_game_studio_next.py`
- studio run/build/test instructions documented:
  - `labs/world_game_studio_next/README.md`

Suggested next milestone:

- `WG-P3 - Dymaxion canvas and core planning loop`

### WG-P3 - Dymaxion canvas and core planning loop

Status: Completed (2026-03-14)

Objective:

- establish the Dymaxion canvas as a real interaction surface and make the scenario/session/branch/proposal/turn loop playable through the new shell.

Scope:

- implement base Dymaxion rendering, hit testing, selection, focus, labels, and viewport controls
- connect the canvas to the inspector and branch/session state
- deliver the first operational layer bundle and map-driven proposal/turn flow

Intended user-visible outcome:

- a user can load a scenario, select regions on the Dymaxion map, draft/adopt a proposal, run a turn, and inspect resulting changes from the same map-centered workspace.

Deliverables:

- `DymaxionCanvas` and initial layer stack
- region polygons, labels, seam-aware interaction semantics, fit/reset controls
- inspector bridge for region and branch context
- initial layer bundle: boundaries, labels, selection overlays, one dominant state layer, one flow layer, proposal preview, annotation badges
- proposal targeting path driven from region selection
- turn-result updates reflected in map and inspector surfaces

Client architecture work:

- viewport and selection hooks
- map render-model adapters
- proposal-target selection state and preview rendering
- shell-to-canvas synchronization for scenario, branch, and active layer context

Runtime methods expected to be consumed:

- `world_game.scenario.load`
- `world_game.session.create`
- `world_game.session.get`
- `world_game.proposal.create`
- `world_game.proposal.submit`
- `world_game.proposal.adopt`
- `world_game.turn.run`
- `world_game.network.inspect`
- `world_game.annotation.create`

Likely touched areas:

- `labs/world_game_studio_next/src/world_canvas/`
- `labs/world_game_studio_next/src/proposal/`
- `labs/world_game_studio_next/src/simulation/`
- `labs/world_game_studio_next/src/state/`
- layer/type modules created in `WG-P1`

Data/topology/layer dependencies:

- accepted topology IDs and geometry assets from `WG-P1`
- scenario layer manifest and initial layer registry
- explicit seam and anchor behavior for labels and adjacency

Out of scope:

- sophisticated compare workbench
- replay timeline and scrubbing
- facilitation/presence polish
- final cutover from legacy studio

Acceptance criteria:

- region hit testing is reliable and stable across redraw/resize
- inspector selection remains synchronized with map state
- a user can complete the core planning loop: load scenario -> focus branch -> target region -> create/adopt proposal -> run turn -> inspect results
- initial layer bundle is legible and conflict-controlled
- the UI still depends on runtime results rather than client-side simulation logic

Validation commands:

- studio unit/component tests for region selection, inspector sync, and proposal preview
- studio integration test for scenario -> proposal -> adopt -> turn flow
- `python3 -m pytest -q tests/test_world_game_smoke.py tests/test_world_game_examples.py`
- `python3 -m pytest -q tests/test_world_game_collaboration.py` if collaboration session methods are touched materially

Completion evidence:

- end-to-end playable core loop in the new studio
- map-centered interaction replaces form-only workflow for the primary planning path
- initial layer bundle and inspector synchronization proven by tests

Suggested next milestone:

- `WG-P4 - Compare, replay, and evidence surfaces`

### WG-P4 - Compare, replay, and evidence surfaces

Status: Completed (2026-03-14)

Objective:

- make branch comparison, replay, and evidence/provenance inspection legible enough that the studio can explain outcomes rather than merely display raw state.

Scope:

- implement compare workspace and branch set selection
- add replay timeline, stepping, scrubbing, and replay-linked canvas state
- add provenance and evidence drawers linked from visible objects and deltas

Intended user-visible outcome:

- a user can compare alternate futures, replay how a branch evolved, and inspect why a visible change happened without dropping into raw JSON or backend internals.

Deliverables:

- compare room with delta, split, and ghost modes
- branch identity system and compare legend
- replay dock or timeline controls with deterministic turn cursor
- provenance drawer and evidence/assumption surfaces linked from compare and replay
- replay-linked inspector and map overlays

Client architecture work:

- compare-selection state
- replay cursor state
- map compare and replay adapter modules
- evidence/provenance presentation components

Runtime methods expected to be consumed:

- `world_game.branch.compare`
- `world_game.replay.run`
- `world_game.provenance.inspect`
- `world_game.equity.report`
- `world_game.network.inspect`
- `world_game.annotation.create` and list/refresh support if added

Likely touched areas:

- `labs/world_game_studio_next/src/compare/`
- `labs/world_game_studio_next/src/replay/`
- `labs/world_game_studio_next/src/provenance/`
- map adapter/state modules
- bottom dock / timeline shell areas

Data/topology/layer dependencies:

- compare-ready delta layers and legends from `WG-P1`
- replay-capable layer bindings keyed by branch and turn index
- provenance metadata shapes for visible state, annotations, proposals, and branch outcomes

Out of scope:

- real-time multi-user presence polish
- collaboration persistence/export mechanics
- final accessibility/performance hardening pass

Acceptance criteria:

- compare mode supports at least baseline vs branch and branch vs branch reasoning
- replay scrub and step behavior keeps canvas, inspector, and summary surfaces synchronized
- provenance is reachable from compare and replay views and explains visible outcomes meaningfully
- branch differences are legible without reading raw runtime payloads

Validation commands:

- studio tests for compare state transitions, replay cursor behavior, and provenance drawer rendering
- studio integration test for branch compare plus replay-linked inspector flow
- `python3 -m pytest -q tests/test_world_game_compare.py tests/test_world_game_replay.py`
- `python3 -m pytest -q tests/test_world_game_collaboration.py` if annotation/provenance linkages require runtime-facing adjustments

Completion evidence:

- compare and replay are first-class studio workflows rather than deferred panels
- provenance/evidence access is integrated into visible decision surfaces
- branch reasoning quality improves measurably over the legacy studio

Suggested next milestone:

- `WG-P5 - Collaboration, facilitation, and persistence`

### WG-P5 - Collaboration, facilitation, and persistence

Status: Completed (2026-03-14)

Objective:

- make the new studio multiplayer-ready for live workshops and close the known durability gap for collaboration state beyond the active runtime process.

Scope:

- expose stage banner, participant presence, proposal queue, moderation/facilitation controls, and shared-attention presentation cues
- add persistence/export support for collaboration state if runtime work is required
- keep collaboration subordinate to the map/simulation experience rather than splitting it into a separate admin tool

Intended user-visible outcome:

- facilitators and participants can run a live session with visible stage gating, shared awareness, moderated proposal flow, and durable session artifacts that survive beyond one in-memory process.

Deliverables:

- facilitation banner and stage-aware action gating
- participant roster/presence surfaces
- proposal queue and moderation affordances
- shared-attention or spotlight mode for presentations/workshops
- collaboration persistence/export mechanism and matching UI affordances
- updated playbook coverage for facilitation workflows

Client architecture work:

- session/presence state expansion
- stage-aware action guards in the shell
- queue and moderation UI
- collaboration export/import or persisted-session retrieval UX

Runtime methods expected to be consumed:

- `world_game.session.create`
- `world_game.session.get`
- `world_game.session.actor.add`
- `world_game.session.stage.set`
- `world_game.session.stage.advance`
- `world_game.proposal.create`
- `world_game.proposal.submit`
- `world_game.proposal.adopt`
- `world_game.annotation.create`
- `world_game.provenance.inspect`
- additive persistence/export methods if needed to close the current in-memory-only gap

Likely touched areas:

- `labs/world_game_studio_next/src/session/`
- `labs/world_game_studio_next/src/proposal/`
- `labs/world_game_studio_next/src/provenance/`
- `adapters/world_game/` and runtime surfaces only if persistence/export support is needed
- playbooks and package docs for collaboration changes

Data/topology/layer dependencies:

- stable branch/proposal/session identity handling from prior milestones
- annotation/evidence overlays should remain compatible with facilitation flows
- no new topology decisions should be reopened here

Out of scope:

- legacy studio cutover
- final release packaging/promotion decision
- major redesign of the already accepted map contracts

Acceptance criteria:

- facilitators can see and control stage state from the new studio
- proposal intake/review/selection behavior is visible and actionable for multi-user sessions
- collaboration state is durable beyond a single active process if the runtime milestone lands here
- the collaboration experience still keeps the map and branch reasoning at the center of the app

Validation commands:

- studio tests for stage gating, proposal queue transitions, and facilitation controls
- studio integration test for workshop flow: session -> actor roster -> proposal intake -> selection -> simulation -> review
- `python3 -m pytest -q tests/test_world_game_collaboration.py`
- `python3 -m pytest -q tests/labs/test_world_game_studio.py` as a regression guard if shared collaboration surfaces are still referenced during migration
- protocol/public API compatibility checks if runtime methods are added or changed

Completion evidence:

- multiplayer-ready facilitation flow demonstrated in the new studio
- collaboration durability/export gap either closed or explicitly deferred with implementation evidence and constraints
- playbooks/status docs updated with the new collaboration posture

Suggested next milestone:

- `WG-P6 - Hardening, cutover, and legacy containment`

### WG-P6 - Hardening, cutover, and legacy containment

Status: Completed (2026-03-14)

Objective:

- harden the new studio for sustained use, decide the long-term relationship with the legacy studio, and package the new surface as the primary World Game experience or an explicitly parallel track.

Scope:

- accessibility, performance, reduced-motion, and keyboard-traversal hardening
- onboarding/demo flow and scenario polish
- public-facing docs and release hygiene
- explicit cutover decision for `labs/world_game_studio`

Intended user-visible outcome:

- the new studio feels production-capable for demos, workshops, and contributor iteration, with clear documentation and no ambiguity about whether the legacy studio is still primary.

Deliverables:

- accessibility and performance pass
- scenario/demo onboarding flow
- updated README/playbooks/status/changelog surfaces
- cutover or containment decision document for legacy `world_game_studio`
- if promoted, clear migration notes and compatibility expectations

Client architecture work:

- performance profiling and targeted optimization
- keyboard and reduced-motion refinements
- empty/error/loading polish
- onboarding route or guided entry flow

Runtime methods expected to be consumed:

- all methods used by prior milestones
- no new runtime methods expected unless hardening uncovers a missing support seam

Likely touched areas:

- broad `labs/world_game_studio_next/src/` polish areas
- studio-local docs and playbooks
- root or package rollup docs only if the promotion decision requires new pointers
- legacy studio docs if the containment or deprecation stance must be made explicit

Data/topology/layer dependencies:

- stable layer presets and scenario manifests
- finalized map asset package and performance constraints
- no major contract redesign should remain open at this point

Out of scope:

- new major product pillars beyond the already planned program
- speculative GIS/general cartography expansion
- replacing `adapters/world_game` as the domain truth source

Acceptance criteria:

- accessibility and interaction hardening are validated on the new shell
- the studio meets agreed performance budgets for ordinary planning workflows
- onboarding/demo flow can walk a new user through the core loop
- the project has a documented, explicit stance on whether legacy `world_game_studio` is retained, contained, or replaced

Validation commands:

- studio build/test/lint bundle
- milestone-specific accessibility and performance checks chosen by implementation
- end-to-end flow covering scenario -> proposal -> simulate -> compare -> replay -> provenance -> facilitation
- domain/runtime regression checks for any shared surfaces touched by cutover work

Completion evidence:

- new studio is hardened and documented
- legacy studio posture is explicit and discoverable
- future contributors no longer need to infer which studio surface is active

Suggested next milestone:

- post-program stabilization or promotion work, depending on cutover outcome

## Post-WG-P6 Extension Guidance

These milestones extend the roadmap beyond `WG-P6` without reopening the completed core-program work.

Guidance for all post-`WG-P6` milestones:

- `adapters/world_game` remains the domain and runtime source of truth
- no breaking changes to existing `world_game.*` methods should be assumed
- any additive runtime work must be justified by a specific studio clarity, facilitation, or durability gap
- client code must continue to avoid local simulation, scoring, or policy logic
- the current vanilla JS `world_game_studio_next` surface remains implementation truth; React/Vite direction in mirrored design docs is aspirational reference only

Candidate additive seams that may be mentioned when justified, but should not be assumed up front:

- `world_game.topology.*` delivery or scenario-linked topology references
- richer compare delta payloads
- replay checkpoint/event marker payloads
- session listing or resume support
- synchronized spotlight or presence metadata

Post-`WG-P6` test-plan expectations:

- each milestone should define milestone-specific studio tests
- runtime-facing work should cross-check existing domain/runtime pytest suites
- each milestone should include at least one user-journey validation centered on the most-changed route
- `WG-P10` should treat browser E2E coverage as required completion evidence rather than a deferred follow-up

### WG-P7 - Experience realization and shell redesign

Status: Completed (2026-03-14)

Objective:

- rebalance the studio shell so the Dymaxion canvas becomes the dominant visual and cognitive surface while preserving the thin-client runtime posture.

Scope:

- redistribute dense controls out of the single long right-rail workflow into map HUD, route-specific workspace panels, inspector cards, and bottom-tray surfaces
- mature the design-system implementation with stronger hierarchy, calmer grouping, presentation mode, and explicit density modes
- add role-aware workspace presets for facilitator, analyst, delegate, and observer without forking runtime behavior
- preserve branch, stage, scenario, and selection continuity across route changes while improving legibility

Intended user-visible outcome:

- the studio feels intentionally designed for workshops, analysis, and screen-shared facilitation rather than like a successful prototype harness.

Deliverables:

- redesigned shell composition with larger canvas footprint in major routes
- route-specific control grouping that reduces inspector overload
- density and presentation-mode controls with accessible defaults
- role-aware workspace presets and clearer stage/branch/status framing
- refreshed design-token and panel treatment aligned with the design-doc posture

Client architecture work:

- shell-layout state for density, presentation, and role-emphasis modes
- route-aware workspace composition and inspector-card grouping
- persistent selection/branch/stage handoff across route transitions
- screenshot-friendly shell-state fixtures if lightweight to support regression coverage

Runtime methods expected to be consumed:

- all methods already used by `WG-P3` through `WG-P6`
- no new runtime methods expected by default

Likely touched areas:

- `labs/world_game_studio_next/src/app/`
- `labs/world_game_studio_next/src/world_canvas/`
- `labs/world_game_studio_next/src/styles/`
- studio-local tests and playbooks if route composition changes materially

Data/topology/layer dependencies:

- existing Dymaxion assets and layer manifests remain authoritative
- no topology-contract reopening should be required
- layer visibility and route composition should remain compatible with compare, replay, and facilitation surfaces

Out of scope:

- additive runtime/domain method design unless a specific UI blocker is confirmed
- major compare or replay semantic redesign
- browser E2E rollout as a program requirement

Acceptance criteria:

- the canvas occupies more of the primary workspace in all major routes
- compare, replay, and facilitation controls remain reachable without dominating core inspection tasks
- presentation mode meaningfully improves projection and screen-share readability
- route transitions preserve selection, branch, stage, and scenario context

Validation commands:

- `python3 labs/world_game_studio_next/scripts/build_static.py`
- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`
- milestone-specific studio tests for route composition and density or presentation toggles
- manual demo pass across onboarding, plan, compare, replay, and facilitate routes

Completion evidence:

- shell redesign shifts the product closer to the intended planetary-operations-room posture
- map-first shell composition now uses larger center-workspace ratios, route-aware control density, and map HUD framing
- role-aware workspace presets (`facilitator`, `analyst`, `delegate`, `observer`) are available without runtime behavior forks
- density controls (`default`, `analysis`, `presentation`) are implemented with presentation/screen-share readability treatment
- route transitions continue to preserve selection, branch, stage, and scenario continuity
- studio docs and milestone-local tests cover WG-P7 behavior changes

Suggested next milestone:

- `WG-P8 - Analytical overlays, compare depth, and narrative explanation`

### WG-P8 - Analytical overlays, compare depth, and narrative explanation

Status: Completed (2026-03-14)

Objective:

- deepen the map and inspector into a true analysis surface so branch outcomes can be explained spatially and temporally without falling back to raw payload reading.

Scope:

- expand analysis-ready layer families and improve compare hotspot surfacing
- add replay markers, branch points, and explanation checkpoints tied to visible map and inspector state
- strengthen provenance storytelling around what changed, where, when, and because of what
- improve compare summaries for threshold, uncertainty, and multi-indicator reasoning under presentation conditions

Intended user-visible outcome:

- analysts and facilitators can explain branch outcomes clearly from inside the studio, especially during compare and replay workflows.

Deliverables:

- richer compare overlays and linked hotspot summaries
- replay markers, checkpoint summaries, and branch-point cues
- explanation-first provenance entry points from region, proposal, compare, and replay context
- stronger legends and narrative summary surfaces for multi-indicator change

Client architecture work:

- compare hotspot state and linked inspector-summary components
- replay marker/checkpoint state and map synchronization hooks
- provenance-entry routing from more visible artifact types
- multi-layer rendering discipline for threshold, uncertainty, and summary overlays

Runtime methods expected to be consumed:

- `world_game.branch.compare`
- `world_game.replay.run`
- `world_game.provenance.inspect`
- `world_game.equity.report`
- existing branch, proposal, and network methods as needed for visible context
- additive runtime follow-ons only if needed for topology delivery, richer compare deltas, replay markers, or provenance summaries

Likely touched areas:

- `labs/world_game_studio_next/src/compare/`
- `labs/world_game_studio_next/src/replay/`
- `labs/world_game_studio_next/src/provenance/`
- `labs/world_game_studio_next/src/world_canvas/`
- runtime/domain surfaces only if additive explanation payloads are justified

Data/topology/layer dependencies:

- stable region IDs and Dymaxion geometry from earlier milestones
- compare/replay layer bindings must remain deterministic by branch and turn context
- explanation layers must remain compatible with presentation mode and reduced-motion behavior

Out of scope:

- replacing file-driven topology transport unless a justified additive runtime seam lands
- generalized GIS tooling beyond studio analysis needs
- full facilitation-role redesign, which belongs to `WG-P9`

Acceptance criteria:

- compare mode highlights top divergence regions and key indicator deltas directly on the map and in linked summaries
- replay mode exposes branch points, turn markers, and explanation checkpoints
- provenance can be opened from selected region, proposal, compare hotspot, or replay checkpoint
- dominant layer and compare legend remain understandable under presentation conditions

Validation commands:

- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`
- milestone-specific studio tests for compare hotspot selection, replay marker sync, and provenance-entry routing
- targeted map-rendering regression tests around multi-layer overlay interactions
- existing domain/runtime compare and replay pytest coverage when runtime-facing changes are made

Completion evidence:

- compare and replay become explanation-forward rather than payload-forward workflows
- analysts can narrate branch tradeoffs from the map and inspector alone in ordinary cases
- any additive runtime seams are documented as additive support work, not silent contract drift

Suggested next milestone:

- `WG-P9 - Facilitation, shared-attention, and session-role maturity`

### WG-P9 - Facilitation, shared-attention, and session-role maturity

Status: Completed (2026-03-14)

Objective:

- turn the current facilitation feature set into a workshop-ready shared session surface with clearer role emphasis, shared attention, and discoverable session continuity.

Scope:

- add role-sensitive presets and clearer room-state awareness for facilitator, analyst, delegate, and observer workflows
- improve shared spotlight, presenter cues, queue triage, and unresolved-evidence visibility
- make session continuity beyond bundle import or export more discoverable if runtime support is available
- preserve the map as the coordination surface rather than splitting facilitation into a detached admin tool

Intended user-visible outcome:

- a facilitator can run a live multi-actor session with clear attention management, role clarity, and durable continuation paths.

Deliverables:

- role-sensitive workspace emphasis and facilitator-oriented room controls
- stronger shared-attention or spotlight workflow
- clearer proposal-queue triage for approval-required or unresolved items
- improved session-continuity affordances beyond manual bundle mechanics when supported
- updated facilitation playbook coverage for workshop operation and debrief

Client architecture work:

- role-preset and room-state summary state
- spotlight and presenter-visibility UX refinements
- queue triage and unresolved-evidence summaries
- session continuity or resume affordances if additive runtime support lands

Runtime methods expected to be consumed:

- `world_game.session.create`
- `world_game.session.get`
- `world_game.session.actor.add`
- `world_game.session.stage.set`
- `world_game.session.stage.advance`
- `world_game.proposal.create`
- `world_game.proposal.submit`
- `world_game.proposal.adopt`
- existing annotation, provenance, and session export/import methods
- additive runtime work only if synchronized spotlight, presence metadata, session listing/resume, or facilitation checkpoints are required

Likely touched areas:

- `labs/world_game_studio_next/src/session/`
- `labs/world_game_studio_next/src/provenance/`
- `labs/world_game_studio_next/src/world_canvas/`
- `labs/world_game_studio_next/src/app/`
- collaboration runtime surfaces only if additive session maturity seams are justified

Data/topology/layer dependencies:

- prior compare/replay/provenance surfaces must remain compatible with shared-attention workflows
- no topology or layer-contract redesign should be reopened
- role-aware emphasis should be purely presentational unless runtime semantics explicitly require additive support

Out of scope:

- release-packaging and browser E2E graduation work, which belongs to `WG-P10`
- replacing the session model with a new collaboration architecture
- reintroducing legacy studio as the primary facilitation surface

Acceptance criteria:

- facilitator, analyst, delegate, and observer views expose different default emphasis without forking the app
- spotlight and presentation state can be shared across participants when runtime support exists, or remains explicitly local if not
- proposal queue review and unresolved evidence become easier to triage during live facilitation
- durable session continuation is discoverable rather than hidden behind import-only mechanics

Validation commands:

- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`
- `python3 -m pytest -q tests/test_world_game_collaboration.py`
- milestone-specific studio tests for role presets, queue triage behavior, and facilitator state transitions
- end-to-end workshop flow pass from setup through debrief

Completion evidence:

- facilitation surfaces support live room operation with less operator friction
- role-aware emphasis improves usability without changing runtime authority boundaries
- session durability posture is clearer to both facilitators and contributors
- shared-attention presenter and spotlight cues are explicit and intentionally marked local-only under current runtime support

Suggested next milestone:

- `WG-P10 - Release-grade stabilization, browser E2E, and promotion follow-through`

### WG-P10 - Release-grade stabilization, browser E2E, and promotion follow-through

Status: Completed (2026-03-14)

Objective:

- finish the path from primary demo/workshop surface to trusted primary product surface through browser-grade validation, profiling discipline, and final promotion hygiene.

Scope:

- add browser interaction coverage for onboarding, keyboard flow, map interactions, compare, replay, and facilitation
- define responsiveness expectations for redraw, scrub, and overlay toggles and replace fragile hotspots when profiling justifies it
- finalize docs, playbooks, and contributor guidance around `world_game_studio_next` as the canonical studio surface
- close remaining release-hygiene gaps without inventing new product pillars

Intended user-visible outcome:

- the studio feels dependable in front of real users, not just implementers.

Deliverables:

- browser E2E harness and core user-journey coverage
- profiling evidence and targeted rendering or interaction optimizations
- final consistency pass across roadmap, status, README, playbooks, and manifest surfaces
- explicit promotion follow-through guidance for contributors and demo operators

Client architecture work:

- test harness integration for browser workflows
- profiling hooks or diagnostics needed to validate redraw and replay responsiveness
- targeted performance fixes replacing proven hotspots
- final accessibility and reduced-motion regression pass under the redesigned shell

Runtime methods expected to be consumed:

- all methods used by `WG-P7` through `WG-P9`
- no new runtime methods expected unless stabilization exposes a concrete missing seam

Likely touched areas:

- `labs/world_game_studio_next/`
- studio-local test harness and fixtures
- playbooks and docs describing canonical usage
- runtime/domain regression coverage only if stabilization touches shared seams

Data/topology/layer dependencies:

- shell and overlay model should be stable enough that browser tests are not immediately invalidated by known redesign work
- no contract-level topology changes should remain open at this point
- performance work should preserve deterministic visual output for the same state inputs

Out of scope:

- speculative new product pillars after post-`WG-P6` stabilization
- replacing `adapters/world_game` as source of truth
- widening scope into unrelated runtime modernization

Acceptance criteria:

- browser E2E coverage exists for the primary user journeys
- ordinary map workflows meet explicit responsiveness expectations
- accessibility and reduced-motion behavior remain intact under the redesigned shell
- docs and playbooks point contributors unambiguously to studio-next for current work

Validation commands:

- `python3 labs/world_game_studio_next/scripts/build_static.py`
- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`
- new browser E2E suite for onboarding, plan, compare, replay, and facilitate flows
- profiling evidence for map redraw and replay scrub responsiveness
- final consistency pass across studio-local docs and playbooks

Completion evidence:

- studio-next is validated as the trusted primary product surface
- browser-grade workflow coverage replaces the last major testing blind spot
- contributor-facing guidance no longer leaves ambiguity about what surface to extend
- browser E2E harness landed in `tests/labs/test_world_game_studio_next_browser_e2e.py` with onboarding, keyboard shortcuts, map interaction, and compare/replay/facilitate route coverage
- planning workspace exposes responsiveness diagnostics (`window.__WG_STUDIO_NEXT_DIAGNOSTICS`) and visible summary output (`planning-performance-summary`)
- explicit responsiveness budgets are documented and emitted for p95 checks:
  - map redraw (`120ms`)
  - replay scrub (`180ms`)
  - overlay toggle (`150ms`)
- README, playbook, status, changelog, and studio manifest now align on studio-next as canonical active surface

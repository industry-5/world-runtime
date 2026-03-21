# World Game Studio Next Changelog

This file is the release and build narrative for `world_game_studio_next`. For the current operational snapshot, use [STATUS.md](STATUS.md). For milestone strategy and implementation sequencing, use [ROADMAP.md](ROADMAP.md).

## Unreleased

### Program bootstrap

- Established `labs/world_game_studio_next` as the dedicated build track for the modern World Game studio.
- Added studio-local roadmap, status, changelog, and milestone kickoff materials so future work can proceed one milestone per thread.
- Preserved `labs/world_game_studio` as the legacy thin-client baseline during migration rather than overwriting it in place.
- Mirrored the external World Game design specs into `scratch/world-game-design-docs/` to provide a stable local reference path for future implementation threads.

### WG-P1 topology, geometry, and layer contracts

- Added typed studio contract surface at `labs/world_game_studio_next/contracts/map_contracts.ts`, including `CanvasRenderState`, `LayerDefinition`, `ScenarioLayerManifest`, and explicit map adapter boundaries.
- Locked topology/geometry split and package placement in `labs/world_game_studio_next/contracts/WG-P1_TOPOLOGY_GEOMETRY_DECISIONS.md`.
- Added runtime-to-layer mapping contract coverage in `labs/world_game_studio_next/contracts/WG-P1_RUNTIME_LAYER_MAPPING.md`.
- Added milestone-local checklist for topology and layer invariants in `labs/world_game_studio_next/contracts/WG-P1_VALIDATION_CHECKLIST.md`.
- Reserved Dymaxion geometry package location and file shape under `labs/world_game_studio_next/assets/world_game_map/v1/README.md`.
- Added additive semantic-topology contract seed under `adapters/world_game/topology/` including:
  - `topology.contract.v1.json`
  - `scenario_bindings/world-game-multi-region.binding.v1.json`
- Kept `labs/world_game_studio` unchanged; no legacy studio migration/cutover changes in WG-P1.

### WG-P2 studio platform foundation

- Added a bootable studio-next application scaffold:
  - `labs/world_game_studio_next/index.html`
  - `labs/world_game_studio_next/server.py`
  - `labs/world_game_studio_next/src/main.js`
- Added centralized studio state domains and request lifecycle store:
  - `labs/world_game_studio_next/src/state/store.js`
- Added explicit, thin runtime service boundaries:
  - `labs/world_game_studio_next/src/services/runtimeClient.js`
  - `labs/world_game_studio_next/src/services/scenarioService.js`
  - `labs/world_game_studio_next/src/services/sessionService.js`
  - `labs/world_game_studio_next/src/services/proposalService.js`
  - `labs/world_game_studio_next/src/services/branchService.js`
  - `labs/world_game_studio_next/src/services/replayService.js`
  - `labs/world_game_studio_next/src/services/annotationService.js`
  - `labs/world_game_studio_next/src/services/provenanceService.js`
  - `labs/world_game_studio_next/src/services/authoringService.js`
- Added permanent shell layout and route scaffolding:
  - `labs/world_game_studio_next/src/app/shell.js`
  - `labs/world_game_studio_next/src/app/router.js`
  - `labs/world_game_studio_next/src/app/render.js`
  - `labs/world_game_studio_next/src/app/bootstrap.js`
- Added initial design-token baseline and shell styling:
  - `labs/world_game_studio_next/src/styles/tokens.css`
  - `labs/world_game_studio_next/src/styles/shell.css`
- Added studio-local build/test harness and manifest:
  - `labs/world_game_studio_next/scripts/build_static.py`
  - `labs/world_game_studio_next/studio_manifest.json`
  - `labs/world_game_studio_next/.gitignore`
- Added WG-P2 milestone tests:
  - `tests/labs/test_world_game_studio_next.py`
- Added studio-next run/build/test instructions:
  - `labs/world_game_studio_next/README.md`
- Kept `labs/world_game_studio` unchanged; legacy studio remains reference baseline only.

### WG-P3 Dymaxion canvas and core planning loop

- Added WG-P3 Dymaxion geometry package payloads under:
  - `labs/world_game_studio_next/assets/world_game_map/v1/dymaxion_faces.json`
  - `labs/world_game_studio_next/assets/world_game_map/v1/dymaxion_land.json`
  - `labs/world_game_studio_next/assets/world_game_map/v1/dymaxion_regions.json`
  - `labs/world_game_studio_next/assets/world_game_map/v1/dymaxion_region_labels.json`
  - `labs/world_game_studio_next/assets/world_game_map/v1/dymaxion_flow_anchors.json`
  - `labs/world_game_studio_next/assets/world_game_map/v1/dymaxion_projection_meta.json`
- Added world-canvas modules for package loading, render-model derivation, and SVG interaction:
  - `labs/world_game_studio_next/src/world_canvas/geometryLoader.js`
  - `labs/world_game_studio_next/src/world_canvas/mapAdapters.js`
  - `labs/world_game_studio_next/src/world_canvas/dymaxionCanvas.js`
  - `labs/world_game_studio_next/src/world_canvas/planningWorkspace.js`
- Wired canvas + planning workspace into the shell and bootstrap flow:
  - `labs/world_game_studio_next/src/app/bootstrap.js`
  - `labs/world_game_studio_next/src/app/render.js`
  - `labs/world_game_studio_next/src/app/shell.js`
- Extended studio state and service boundaries for WG-P3 runtime flow:
  - added `canvas` and `planning` state domains in `src/state/store.js`
  - added `simulationService` (`world_game.turn.run`, `world_game.network.inspect`)
  - extended `sessionService` with stage advancement methods
  - extended proposal and annotation services for list/adopt/list-target workflows
- Added WG-P3 styling for map-first layout and layer/viewport/overlay visuals in:
  - `labs/world_game_studio_next/src/styles/shell.css`
- Updated studio-next tests and docs for WG-P3 workflow and geometry-package assertions:
  - `tests/labs/test_world_game_studio_next.py`
  - `labs/world_game_studio_next/README.md`
  - `labs/world_game_studio_next/studio_manifest.json`
- Kept `labs/world_game_studio` unchanged; no migration/cutover changes in WG-P3.

### WG-P4 compare, replay, and evidence surfaces

- Added dedicated WG-P4 studio modules:
  - `labs/world_game_studio_next/src/compare/compareWorkspace.js`
  - `labs/world_game_studio_next/src/compare/mapCompareAdapter.js`
  - `labs/world_game_studio_next/src/replay/replayWorkspace.js`
  - `labs/world_game_studio_next/src/replay/mapReplayAdapter.js`
  - `labs/world_game_studio_next/src/provenance/provenanceDrawer.js`
- Extended the WG-P3 planning workspace with route-aware compare/replay/provenance panels and controls:
  - compare pair selection, delta/split/ghost mode switch, compare run action
  - replay branch load, timeline cursor scrub, step controls
  - provenance drawer reachable from compare/replay contexts plus manual artifact lookup
- Integrated compare/replay/provenance flows into app orchestration and state:
  - `labs/world_game_studio_next/src/app/bootstrap.js`
  - `labs/world_game_studio_next/src/state/store.js`
  - `labs/world_game_studio_next/src/app/render.js`
  - `labs/world_game_studio_next/src/app/shell.js`
- Updated map adapters/canvas rendering for WG-P4:
  - compare and replay context-aware dominant layer derivation
  - compare overlay rendering (delta focus, ghost highlights, split guide)
  - replay frame-linked map and inspector synchronization
  - supporting styles in `labs/world_game_studio_next/src/styles/shell.css`
- Added a narrow additive runtime follow-on in domain service support for replay scrubbing:
  - `world_game.replay.run` now includes `replay_frames` and `replay_frame_count` in `adapters/world_game/service.py`
  - this preserves existing replay summary fields while exposing per-turn frame payloads for studio WG-P4 timeline behavior
- Fixed provenance service parameter naming to match runtime contract (`artifact_type`/`artifact_id`):
  - `labs/world_game_studio_next/src/services/provenanceService.js`
- Extended simulation service thin boundary with equity reporting:
  - `labs/world_game_studio_next/src/services/simulationService.js`
- Updated milestone tests/docs/manifest for WG-P4:
  - `tests/labs/test_world_game_studio_next.py`
  - `tests/test_world_game_smoke.py`
  - `labs/world_game_studio_next/README.md`
  - `labs/world_game_studio_next/studio_manifest.json`
- Kept `labs/world_game_studio` unchanged; no migration/cutover edits in WG-P4.

### WG-P5 collaboration, facilitation, and persistence

- Added explicit WG-P5 facilitation and collaboration controls to the map-first workspace:
  - stage set/advance controls with visible stage-aware action gating
  - participant roster/presence controls (`actor id` + role add)
  - proposal moderation queue with submit/adopt/reject affordances
  - spotlight and presentation mode facilitation cues
  - collaboration session export/import controls
- Extended shell and rendering for WG-P5 collaboration awareness:
  - top-bar facilitation banner with stage, allowed actions, and spotlight status
  - left-rail participant and proposal queue summaries
  - presentation-mode class toggles for workshop-focused display posture
- Added map-level spotlight overlays and presentation-mode visual adjustments in:
  - `labs/world_game_studio_next/src/world_canvas/mapAdapters.js`
  - `labs/world_game_studio_next/src/world_canvas/dymaxionCanvas.js`
  - `labs/world_game_studio_next/src/styles/shell.css`
- Reworked WG-P5 action orchestration in bootstrap/state:
  - replaced implicit stage auto-advance with explicit stage-aware action guards
  - added actor add, stage set/advance, proposal reject, queue filtering, spotlight controls
  - added collaboration export/import flow with bundle download + import rehydration
  - persisted facilitation UI state domain (`queueFilter`, `spotlightRegionId`, `presentationMode`, persistence summary)
- Added additive runtime/domain follow-on methods to close collaboration durability gap:
  - `world_game.session.export`
  - `world_game.session.import`
  - app-server wiring in `core/app_server.py`
  - service implementation in `adapters/world_game/service.py`
- Updated protocol/public API/domain docs for new runtime methods:
  - `APP_SERVER_PROTOCOL.md`
  - `api/PUBLIC_API_V1.md`
  - `adapters/world_game/README.md`
  - `adapters/world_game/STATUS.md`
- Updated WG-P5 studio and runtime validation coverage:
  - `tests/labs/test_world_game_studio_next.py`
  - `tests/test_world_game_collaboration.py`
- Kept `labs/world_game_studio` unchanged; no migration/cutover edits in WG-P5.

### WG-P6 hardening, cutover, and legacy containment

- Added onboarding-first route posture and guided quickstart flow in studio-next:
  - new `onboard` route in `src/state/store.js` and `src/app/router.js`
  - onboarding checklist/status panel and quickstart controls in `src/world_canvas/planningWorkspace.js`
  - route jump shortcuts for core flow transitions from onboarding
- Added accessibility hardening for keyboard and assistive workflows:
  - skip-link and live status region in `src/app/shell.js`
  - screen-reader route/stage/selection summaries in `src/app/render.js`
  - reduced-motion state and toggle wiring in `src/app/bootstrap.js`
  - visible focus styles and reduced-motion CSS in `src/styles/shell.css`
  - keyboard-accessible region navigator in planning workspace
  - keyboard viewport shortcuts on Dymaxion canvas (`+`, `-`, `0`, `f`)
- Added targeted performance hardening:
  - reduced render churn by committing viewport updates after drag completion in `src/world_canvas/dymaxionCanvas.js`
  - memoized canvas render fingerprint in `src/world_canvas/planningWorkspace.js` to skip unchanged redraws
- Added explicit legacy containment/cutover documentation:
  - `labs/world_game_studio_next/WG-P6_CUTOVER_CONTAINMENT_DECISION.md`
  - `labs/world_game_studio/README.md` updated with containment notice pointing to studio-next as primary
- Updated studio-next docs/manifest/tests for WG-P6:
  - `labs/world_game_studio_next/README.md`
  - `labs/world_game_studio_next/studio_manifest.json`
  - `tests/labs/test_world_game_studio_next.py`

### WG-P7 experience realization and shell redesign

- Rebalanced shell composition so Dymaxion map workspace dominates across major routes:
  - expanded center-column footprint
  - route-aware planning-workspace composition for compare/replay map-first flows
- Added explicit experience controls for role-aware presets and density modes:
  - top-bar workspace role selector (`facilitator`, `analyst`, `delegate`, `observer`)
  - top-bar density selector (`default`, `analysis`, `presentation`)
  - stage banner now includes active role and density context
- Added route-context map HUD to keep branch, selection, and experience framing visible near the canvas.
- Refined inspector into grouped cards:
  - core mode/stage/branch/selection status
  - region metrics card
  - compare/provenance card
  - service boundaries card (deemphasized in presentation mode)
- Added role-aware UI gating in planning workspace controls while preserving runtime authority:
  - facilitator has full control surfaces
  - analyst/delegate/observer reduce facilitation and mutation affordances in the studio shell only
- Added density-mode shell behavior:
  - `analysis` prioritizes inspector detail posture
  - `presentation` increases map legibility and suppresses low-value chrome for projection/screen-share
- Updated orchestration/state/docs/tests for WG-P7:
  - `labs/world_game_studio_next/src/state/store.js`
  - `labs/world_game_studio_next/src/app/shell.js`
  - `labs/world_game_studio_next/src/app/render.js`
  - `labs/world_game_studio_next/src/app/bootstrap.js`
  - `labs/world_game_studio_next/src/world_canvas/planningWorkspace.js`
  - `labs/world_game_studio_next/src/styles/shell.css`
  - `tests/labs/test_world_game_studio_next.py`
  - `labs/world_game_studio_next/README.md`
  - `playbooks/world-game-studio-next-demo.md`
  - `labs/world_game_studio_next/studio_manifest.json`
  - `labs/world_game_studio_next/ROADMAP.md`
  - `labs/world_game_studio_next/STATUS.md`
- Kept `labs/world_game_studio` unchanged; no legacy migration/cutover edits in WG-P7.

### WG-P8 analytical overlays, compare depth, and narrative explanation

- Added compare hotspot modeling and narrative payload derivation in:
  - `labs/world_game_studio_next/src/compare/mapCompareAdapter.js`
  - thresholded hotspot selection, severity/confidence classification, and indicator-delta summary
- Extended compare workspace controls and routing:
  - hotspot threshold control
  - hotspot focus/provenance actions linked to map and inspector context
  - compare summary payload now includes hotspot and indicator delta context
- Added replay marker/checkpoint modeling in:
  - `labs/world_game_studio_next/src/replay/mapReplayAdapter.js`
  - checkpoint classification from replay frames (policy/shock/delta cues)
  - branch-point cue support from branch lineage
- Extended replay workspace controls and routing:
  - checkpoint list with focus/provenance actions
  - checkpoint context synchronized to replay cursor
- Expanded provenance-entry inference in:
  - `labs/world_game_studio_next/src/world_canvas/planningWorkspace.js`
  - selected region context
  - compare hotspot context
  - replay checkpoint context
- Updated map overlays and presentation readability:
  - compare hotspot and replay checkpoint overlays in `src/world_canvas/dymaxionCanvas.js`
  - replay checkpoint layer registration and inspector metric additions in `src/world_canvas/mapAdapters.js`
  - presentation-readability styling in `src/styles/shell.css`
- Updated orchestration/state shell integration:
  - compare/replay hotspot/checkpoint state fields in `src/state/store.js`
  - new compare/replay action handlers and provenance routing hooks in `src/app/bootstrap.js`
  - inspector/dock context labels in `src/app/render.js`
- Updated WG-P8 tests and docs:
  - `tests/labs/test_world_game_studio_next.py`
  - `labs/world_game_studio_next/README.md`
  - `labs/world_game_studio_next/ROADMAP.md`
  - `labs/world_game_studio_next/STATUS.md`
  - `labs/world_game_studio_next/studio_manifest.json`
  - `playbooks/world-game-studio-next-demo.md`

### WG-P9 facilitation, shared-attention, and session-role maturity

- Added role-sensitive facilitation emphasis in studio-next without changing runtime authority:
  - role preset config in `src/app/bootstrap.js` now applies queue/follow defaults for facilitator/analyst/delegate/observer
  - planning workspace now includes role-emphasis summary copy and role-highlight panel styling hooks
- Expanded shared-attention cues for workshop operation:
  - presenter selector and follow-presenter toggle in `src/world_canvas/planningWorkspace.js`
  - top banner and map HUD now display attention status/presenter context in `src/app/render.js` and `src/app/shell.js`
  - shared-attention sync posture is explicit (`local-only`) with current runtime capabilities
- Added queue triage and unresolved-evidence visibility:
  - queue-level triage summary (`review`, `unresolved evidence`, `ready`)
  - proposal-level evidence readiness chips in queue rows
  - unresolved evidence derived from proposal `evidence_refs` and proposal-targeted `evidence-gap` annotations
- Added session continuity discoverability beyond import/export-only cues:
  - `Refresh room state` action (session + proposals + annotations + network refresh path)
  - continuity timeline list from runtime session timeline events
  - room-state summary in left rail
- Updated WG-P9 studio tests/docs/manifest/status/playbook:
  - `tests/labs/test_world_game_studio_next.py`
  - `labs/world_game_studio_next/README.md`
  - `labs/world_game_studio_next/STATUS.md`
  - `labs/world_game_studio_next/ROADMAP.md`
  - `labs/world_game_studio_next/studio_manifest.json`
  - `playbooks/world-game-studio-next-demo.md`
- Kept `labs/world_game_studio` unchanged; no legacy migration/cutover edits in WG-P9.

### WG-P10 release-grade stabilization, browser E2E, and promotion follow-through

- Added browser E2E harness coverage in:
  - `tests/labs/test_world_game_studio_next_browser_e2e.py`
  - Safari WebDriver-based journey checks for onboarding, keyboard routing, map interaction, and compare/replay/facilitate route workflows
- Added responsiveness diagnostics and profiling summary surfaces in:
  - `labs/world_game_studio_next/src/world_canvas/planningWorkspace.js`
  - explicit p95 budgets for map redraw (`120ms`), replay scrub (`180ms`), and overlay toggles (`150ms`)
  - runtime-visible diagnostics via `window.__WG_STUDIO_NEXT_DIAGNOSTICS`
  - in-studio diagnostics summary panel `planning-performance-summary`
- Added milestone-level contract assertions for stabilization artifacts:
  - `tests/labs/test_world_game_studio_next.py`
- Updated promotion and operator docs:
  - `labs/world_game_studio_next/README.md`
  - `playbooks/world-game-studio-next-demo.md`
  - `labs/world_game_studio_next/studio_manifest.json`
  - `labs/world_game_studio_next/ROADMAP.md`
  - `labs/world_game_studio_next/STATUS.md`
- Kept `labs/world_game_studio` unchanged; no legacy migration/cutover edits in WG-P10.

### Pending implementation milestones

- WG-P0 through WG-P10 are implemented.
- No studio release or version tag has been cut for `world_game_studio_next` yet.
- The migration posture is parallel-track for now: legacy studio remains available while the new studio is built milestone by milestone.

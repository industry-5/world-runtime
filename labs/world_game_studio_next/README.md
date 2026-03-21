# World Game Studio Next

Dymaxion-first planning studio build for the modern World Game experience.

WG-P3 establishes a map-centered core planning loop while keeping domain logic in runtime methods (`world_game.*`).
WG-P4 adds compare room, replay timeline, and provenance/evidence surfaces linked to the map and inspector.
WG-P5 adds facilitation controls, collaboration moderation surfaces, spotlight presentation cues, and collaboration session durability workflows.
WG-P6 hardens accessibility and performance posture, adds onboarding/demo guidance, and documents explicit legacy containment.
WG-P7 realizes the shell redesign with map-dominant layout, role-aware workspace presets, and density modes (default, analysis, presentation).
WG-P8 adds analysis overlays with compare hotspots, replay checkpoints, and context-aware provenance entry paths.
WG-P9 matures facilitation with role-sensitive room emphasis, shared-attention presenter cues, queue triage, and discoverable session continuity.
WG-P10 adds browser E2E coverage, responsiveness diagnostics, and promotion-grade contributor guidance.

## Run

1. Start API server (default `http://127.0.0.1:8080`):

```bash
python3 -m api.http_server --host 127.0.0.1 --port 8080
```

2. (Optional) Build static bundle:

```bash
python3 labs/world_game_studio_next/scripts/build_static.py
```

3. Start studio-next server:

```bash
python3 labs/world_game_studio_next/server.py --host 127.0.0.1 --port 8093 --upstream http://127.0.0.1:8080
```

4. Open `http://127.0.0.1:8093` (default route is onboarding).

## Studio-Local Validation Commands

- Build: `python3 labs/world_game_studio_next/scripts/build_static.py`
- Test: `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`
- Browser E2E: `python3 -m pytest -q tests/labs/test_world_game_studio_next_browser_e2e.py`
- Structure snapshot: `find labs/world_game_studio_next -maxdepth 2 \( -type f -o -type d \) | sort`

## WG-P10 Release Stabilization and Browser E2E Coverage

- browser E2E harness:
  - Safari WebDriver suite in `tests/labs/test_world_game_studio_next_browser_e2e.py`
  - validates onboarding, keyboard route shortcuts, plan map interaction, compare/replay/facilitate route coverage, and reduced-motion toggle behavior
- responsiveness diagnostics exposed from planning workspace:
  - `window.__WG_STUDIO_NEXT_DIAGNOSTICS`
  - map redraw p95 budget: `120ms`
  - replay scrub p95 budget: `180ms`
  - overlay toggle p95 budget: `150ms`
  - diagnostics summary visible in workspace snapshot as `planning-performance-summary`
- promotion follow-through:
  - docs and playbook positioning now point contributors to `labs/world_game_studio_next` as canonical studio surface
  - runtime/domain authority remains in `adapters/world_game` without frontend simulation-policy forks

## WG-P6 Hardening, Onboarding, and Containment Coverage

- onboarding route and quickstart checklist for core demo flow
- keyboard route shortcuts: `Alt+1` through `Alt+6` (`onboard`, `plan`, `simulate`, `compare`, `replay`, `facilitate`)
- accessible skip-link and screen-reader summary status text
- visible focus states for shell controls and map interaction surfaces
- reduced-motion toggle plus `prefers-reduced-motion` handling
- keyboard-accessible region navigator as non-map fallback selection path
- canvas drag performance hardening by committing viewport updates after pan completion
- explicit cutover/containment decision documented in:
  - `labs/world_game_studio_next/WG-P6_CUTOVER_CONTAINMENT_DECISION.md`
- guided operator walkthrough:
  - `playbooks/world-game-studio-next-demo.md`

## WG-P7 Experience Realization and Shell Redesign Coverage

- map-dominant shell ratio and route-aware control composition:
  - larger center workspace footprint across major routes
  - compare/replay routes collapse into map-first composition with route panels below
- role-aware workspace presets (no runtime behavior fork):
  - facilitator, analyst, delegate, observer workspace modes
  - route controls and action affordances adapt by role while runtime remains authoritative
- density modes with accessible defaults:
  - `default`, `analysis`, `presentation`
  - stage banner and map HUD always show active role and density context
  - presentation mode hides low-value chrome and increases map readability for projection/screen-share
- inspector refinement:
  - grouped inspector cards (core context, region metrics, compare/provenance, service boundaries)
  - service boundaries deemphasized in presentation density
- continuity posture preserved:
  - scenario, stage, branch, and selection state continue to survive route transitions

## WG-P8 Analytical Overlays and Narrative Explanation Coverage

- compare hotspot depth:
  - thresholded hotspot filtering for top divergence regions
  - hotspot severity/confidence narrative rows linked to map selection
  - compare summary now includes indicator delta sample for narrative framing
- replay narrative depth:
  - replay marker/checkpoint model derived from turn frames
  - branch-point cue at replay turn 0 when branch lineage exists
  - checkpoint region highlighting synced to replay cursor/selected checkpoint
- provenance entry expansion:
  - provenance routing now supports selected region context
  - compare hotspot provenance entry routes to active compare branch context
  - replay checkpoint provenance entry routes to replay branch + turn context
- overlay readability:
  - explicit map treatments for selected compare hotspot and replay checkpoint regions
  - compare/replay legends and context labels tuned for presentation density readability

## WG-P9 Facilitation, Shared-Attention, and Session-Role Maturity Coverage

- role-sensitive default emphasis:
  - role presets now set queue triage defaults (`facilitator`, `analyst`, `delegate`, `observer`)
  - role-emphasis summary copy appears in the planning workspace
  - role-specific panel emphasis styling improves facilitator/analyst/delegate/observer workflows without changing runtime authority
- shared-attention maturity:
  - presenter selection and follow-presenter toggle in facilitation spotlight controls
  - stage banner and map HUD include presenter and attention status cues
  - shared-attention sync status is explicitly marked `local-only` in the current runtime posture
- queue triage and unresolved evidence:
  - queue-level triage summary (`review`, `unresolved evidence`, `ready`)
  - proposal queue chips classify evidence readiness for each item
  - unresolved evidence derives from proposal evidence refs and proposal-targeted `evidence-gap` annotations
- session continuity discoverability:
  - `Refresh room state` action rehydrates session/proposal/annotation/network context from runtime
  - continuity timeline shows recent session events from runtime session timeline
  - export/import controls remain available and explicitly framed as continuity mechanics

## WG-P5 Collaboration/Facilitation/Persistence Coverage

- permanent shell regions:
  - top bar
  - left rail
  - center Dymaxion workspace
  - right inspector
  - bottom dock
- Dymaxion canvas interactions:
  - region hit testing and selection
  - shift-click proposal scope targeting
  - pan/zoom/fit/reset viewport controls
  - selection/hover/proposal overlays
  - compare highlights (delta/split/ghost driven overlays)
  - replay-linked dominant layer and flow rendering via replay turn frames
- compare workflow:
  - baseline and target branch selection
  - runtime-backed compare execution (`world_game.branch.compare`)
  - compare visualization modes: delta, split, ghost
  - compare legend and tradeoff summaries without raw payload reading
- replay workflow:
  - runtime-backed replay loading (`world_game.replay.run`)
  - replay timeline cursor with scrub and step controls
  - replay-linked map/inspector synchronization by frame
- evidence/provenance workflow:
  - provenance inspection from compare/replay context and manual artifact lookup
  - runtime-backed provenance surface (`world_game.provenance.inspect`)
  - compare annotation summary usage from runtime compare responses
- facilitation and multiplayer readiness workflow:
  - explicit stage controls (`set` and `advance`) with stage-aware action gating cues
  - participant roster/presence management (`world_game.session.actor.add`)
  - proposal queue board with moderation actions (focus, submit, adopt, reject)
  - persistent top-bar stage banner with allowed actions and spotlight status
  - spotlight and presentation mode cues to support workshop facilitation
- collaboration durability workflow:
  - runtime-backed session export/import (`world_game.session.export`, `world_game.session.import`)
  - studio export/download and import-from-bundle controls in Facilitate route
  - imported bundles rehydrate scenario/session/branch/proposal/annotation context for continued facilitation
- retained core planning workflow:
  - scenario load
  - branch focus
  - proposal create/submit/adopt
  - turn run from active branch
  - runtime-backed network snapshot refresh
- centralized state domains:
  - scenario
  - session
  - branch
  - selection
  - layers
  - canvas
  - planning
  - compare
  - replay
  - facilitation
  - notifications
  - request lifecycle
- runtime service modules:
  - scenario
  - session
  - proposal
  - branch
  - replay
  - simulation (`world_game.turn.run`, `world_game.network.inspect`)
  - simulation equity reports (`world_game.equity.report`)
  - annotation
  - provenance
  - authoring
  - collaboration durability (`world_game.session.export`, `world_game.session.import`)

No simulation/policy behavior is implemented in the frontend. Runtime/domain methods remain authoritative.

## WG-P5 Milestone Validation Commands

- `rg -n "onSetSessionStage|onAdvanceSessionStage|onAddActor|onRejectProposal|onSetSpotlightFromSelection|onSetPresentationMode|onExportSession|onImportSession|world_game.session.export|world_game.session.import|world_game.proposal.reject" labs/world_game_studio_next/src adapters/world_game/service.py core/app_server.py`
- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`
- `python3 -m pytest -q tests/test_world_game_collaboration.py`

## WG-P7 Milestone Validation Commands

- `rg -n "workspace-role-select|density-mode-select|stage-banner-experience|planning-map-hud|routeGroupVisibility|roleCapabilitySet|setWorkspaceRole|setDensityMode" labs/world_game_studio_next/src tests/labs/test_world_game_studio_next.py`
- `python3 labs/world_game_studio_next/scripts/build_static.py`
- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`

## WG-P8 Milestone Validation Commands

- `rg -n "hotspotThreshold|selectedHotspotRegionId|compare-hotspot-threshold|onSetCompareHotspot|onInspectProvenanceFromCompareHotspot|selectedCheckpointTurn|replay-checkpoints|onJumpReplayCheckpoint|onInspectProvenanceFromReplayCheckpoint|analysis.replay_checkpoints|dymaxion-compare-hotspot-region|dymaxion-replay-checkpoint-region" labs/world_game_studio_next/src tests/labs/test_world_game_studio_next.py labs/world_game_studio_next/README.md labs/world_game_studio_next/CHANGELOG.md`
- `python3 labs/world_game_studio_next/scripts/build_static.py`
- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`

## WG-P9 Milestone Validation Commands

- `rg -n "ROLE_PRESET_CONFIG|setPresenterActor|setFollowPresenter|refreshContinuity|planning-role-emphasis-summary|planning-queue-triage-summary|planning-presenter-select|planning-follow-presenter|planning-refresh-continuity|planning-continuity-events|stage-banner-attention|room-state-summary|sharedAttentionStatus|queue-triage-chip" labs/world_game_studio_next/src tests/labs/test_world_game_studio_next.py labs/world_game_studio_next/README.md labs/world_game_studio_next/CHANGELOG.md`
- `python3 labs/world_game_studio_next/scripts/build_static.py`
- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`
- `python3 -m pytest -q tests/test_world_game_collaboration.py`

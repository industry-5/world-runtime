from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
STUDIO_NEXT_DIR = REPO_ROOT / "labs" / "world_game_studio_next"
SRC_DIR = STUDIO_NEXT_DIR / "src"


def test_world_game_studio_next_scaffold_exists():
    assert (STUDIO_NEXT_DIR / "README.md").exists()
    assert (STUDIO_NEXT_DIR / "index.html").exists()
    assert (STUDIO_NEXT_DIR / "server.py").exists()
    assert (STUDIO_NEXT_DIR / "studio_manifest.json").exists()
    assert (STUDIO_NEXT_DIR / "scripts" / "build_static.py").exists()


def test_world_game_studio_next_shell_regions_are_declared():
    shell_js = (SRC_DIR / "app" / "shell.js").read_text(encoding="utf-8")

    assert "shell-top-bar" in shell_js
    assert "shell-left-rail" in shell_js
    assert "shell-center-workspace" in shell_js
    assert "shell-right-inspector" in shell_js
    assert "shell-bottom-dock" in shell_js
    assert "workspace-role-select" in shell_js
    assert "density-mode-select" in shell_js
    assert "stage-banner-experience" in shell_js


def test_world_game_studio_next_state_domains_are_canonical():
    state_store = (SRC_DIR / "state" / "store.js").read_text(encoding="utf-8")

    for domain in [
        "scenario",
        "session",
        "branch",
        "selection",
        "layers",
        "canvas",
        "planning",
        "compare",
        "replay",
        "provenance",
        "facilitation",
        "accessibility",
        "notifications",
        "runtime",
    ]:
        assert f'"{domain}"' in state_store
    assert '"onboard"' in state_store
    assert "proposalRegionIds" in state_store
    assert "hoverRegionId" in state_store
    assert '"experience"' in state_store
    assert "densityMode" in state_store
    assert "workspaceRole" in state_store


def test_world_game_studio_next_runtime_services_are_thin_boundaries():
    service_dir = SRC_DIR / "services"
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(service_dir.glob("*Service.js"))
    )

    expected_methods = [
        "world_game.scenario.list",
        "world_game.scenario.load",
        "world_game.session.create",
        "world_game.session.get",
        "world_game.session.actor.add",
        "world_game.session.actor.list",
        "world_game.session.stage.set",
        "world_game.session.stage.advance",
        "world_game.session.export",
        "world_game.session.import",
        "world_game.branch.create",
        "world_game.branch.compare",
        "world_game.turn.run",
        "world_game.network.inspect",
        "world_game.equity.report",
        "world_game.replay.run",
        "world_game.proposal.create",
        "world_game.proposal.list",
        "world_game.proposal.submit",
        "world_game.proposal.adopt",
        "world_game.proposal.reject",
        "world_game.annotation.create",
        "world_game.annotation.list",
        "world_game.provenance.inspect",
        "world_game.authoring.template.list",
    ]

    for method in expected_methods:
        assert method in combined

    # Keep simulation/policy logic in runtime, not frontend services.
    assert "computeScorecard" not in combined
    assert "applyEffects" not in combined


def test_world_game_studio_next_canvas_modules_exist():
    assert (SRC_DIR / "world_canvas" / "geometryLoader.js").exists()
    assert (SRC_DIR / "world_canvas" / "mapAdapters.js").exists()
    assert (SRC_DIR / "world_canvas" / "dymaxionCanvas.js").exists()
    assert (SRC_DIR / "world_canvas" / "planningWorkspace.js").exists()

    canvas_code = (SRC_DIR / "world_canvas" / "dymaxionCanvas.js").read_text(encoding="utf-8")
    assert "createDymaxionCanvas" in canvas_code
    assert "onRegionSelect" in canvas_code
    assert "onViewportChange" in canvas_code

    bootstrap_code = (SRC_DIR / "app" / "bootstrap.js").read_text(encoding="utf-8")
    assert "createPlanningWorkspace" in bootstrap_code
    assert "world_game.proposal.create" in bootstrap_code
    assert "world_game.proposal.adopt" in bootstrap_code
    assert "world_game.turn.run" in bootstrap_code
    assert "world_game.network.inspect" in bootstrap_code


def test_world_game_studio_next_geometry_package_shape_is_present():
    map_dir = STUDIO_NEXT_DIR / "assets" / "world_game_map" / "v1"
    expected = {
        "dymaxion_faces.json",
        "dymaxion_land.json",
        "dymaxion_regions.json",
        "dymaxion_region_labels.json",
        "dymaxion_flow_anchors.json",
        "dymaxion_projection_meta.json",
    }
    assert expected.issubset({path.name for path in map_dir.glob("*.json")})


def test_world_game_studio_next_wg_p4_modules_and_routes_exist():
    compare_workspace = SRC_DIR / "compare" / "compareWorkspace.js"
    compare_adapter = SRC_DIR / "compare" / "mapCompareAdapter.js"
    replay_workspace = SRC_DIR / "replay" / "replayWorkspace.js"
    replay_adapter = SRC_DIR / "replay" / "mapReplayAdapter.js"
    provenance_drawer = SRC_DIR / "provenance" / "provenanceDrawer.js"

    assert compare_workspace.exists()
    assert compare_adapter.exists()
    assert replay_workspace.exists()
    assert replay_adapter.exists()
    assert provenance_drawer.exists()

    planning_workspace = (SRC_DIR / "world_canvas" / "planningWorkspace.js").read_text(encoding="utf-8")
    assert "createCompareWorkspace" in planning_workspace
    assert "createReplayWorkspace" in planning_workspace
    assert "createProvenanceDrawer" in planning_workspace
    assert "onRunCompare" in planning_workspace
    assert "onLoadReplay" in planning_workspace
    assert "onInspectProvenance" in planning_workspace

    bootstrap_code = (SRC_DIR / "app" / "bootstrap.js").read_text(encoding="utf-8")
    assert "runCompare" in bootstrap_code
    assert "loadReplay" in bootstrap_code
    assert "inspectProvenance" in bootstrap_code
    assert "world_game.branch.compare" in bootstrap_code
    assert "world_game.replay.run" in bootstrap_code
    assert "world_game.provenance.inspect" in bootstrap_code
    assert "world_game.equity.report" in bootstrap_code

    render_code = (SRC_DIR / "app" / "render.js").read_text(encoding="utf-8")
    assert "delta, split, and ghost" in render_code
    assert "timeline loading, stepping, scrubbing" in render_code


def test_world_game_studio_next_wg_p5_facilitation_and_persistence_surfaces_exist():
    planning_workspace = (SRC_DIR / "world_canvas" / "planningWorkspace.js").read_text(encoding="utf-8")
    assert "planning-stage-select" in planning_workspace
    assert "planning-add-actor" in planning_workspace
    assert "planning-proposal-queue" in planning_workspace
    assert "planning-set-spotlight" in planning_workspace
    assert "planning-export-session" in planning_workspace
    assert "planning-import-session" in planning_workspace
    assert "onSetSessionStage" in planning_workspace
    assert "onAddActor" in planning_workspace
    assert "onRejectProposal" in planning_workspace
    assert "onExportSession" in planning_workspace
    assert "onImportSession" in planning_workspace

    bootstrap_code = (SRC_DIR / "app" / "bootstrap.js").read_text(encoding="utf-8")
    assert "world_game.session.actor.add" in bootstrap_code
    assert "world_game.session.stage.set" in bootstrap_code
    assert "world_game.proposal.reject" in bootstrap_code
    assert "world_game.session.export" in bootstrap_code
    assert "world_game.session.import" in bootstrap_code
    assert "ensureActionAllowed" in bootstrap_code

    shell_code = (SRC_DIR / "app" / "shell.js").read_text(encoding="utf-8")
    assert "stage-banner" in shell_code
    assert "participant-list" in shell_code
    assert "proposal-queue-summary" in shell_code


def test_world_game_studio_next_wg_p6_onboarding_and_accessibility_surfaces_exist():
    planning_workspace = (SRC_DIR / "world_canvas" / "planningWorkspace.js").read_text(encoding="utf-8")
    assert "onboarding-start" in planning_workspace
    assert "onboarding-step-list" in planning_workspace
    assert "planning-region-select" in planning_workspace
    assert "onNavigateRoute" in planning_workspace
    assert "onStartOnboarding" in planning_workspace
    assert "onFocusRegion" in planning_workspace
    assert "canvasRenderFingerprint" in planning_workspace

    shell_code = (SRC_DIR / "app" / "shell.js").read_text(encoding="utf-8")
    assert "skip-link" in shell_code
    assert "screenreader-status" in shell_code
    assert "reduced-motion-toggle" in shell_code

    render_code = (SRC_DIR / "app" / "render.js").read_text(encoding="utf-8")
    assert "updateScreenReaderStatus" in render_code
    assert "reduced-motion" in render_code

    bootstrap_code = (SRC_DIR / "app" / "bootstrap.js").read_text(encoding="utf-8")
    assert "KEYBOARD_ROUTE_SHORTCUTS" in bootstrap_code
    assert "startOnboardingQuickstart" in bootstrap_code
    assert "setReducedMotion" in bootstrap_code
    assert "onboard" in bootstrap_code

    canvas_code = (SRC_DIR / "world_canvas" / "dymaxionCanvas.js").read_text(encoding="utf-8")
    assert "dragState.moved = true" in canvas_code
    assert "if (dragState.moved)" in canvas_code
    assert "setViewport(" in canvas_code

    styles = (SRC_DIR / "styles" / "shell.css").read_text(encoding="utf-8")
    assert ".skip-link" in styles
    assert ":focus-visible" in styles
    assert "@media (prefers-reduced-motion: reduce)" in styles
    assert ".onboarding-step-item" in styles


def test_world_game_studio_next_wg_p7_experience_shell_controls_exist():
    planning_workspace = (SRC_DIR / "world_canvas" / "planningWorkspace.js").read_text(encoding="utf-8")
    assert "planning-map-hud" in planning_workspace
    assert "planning-workspace-role" in planning_workspace
    assert "planning-density-mode" in planning_workspace
    assert "routeGroupVisibility" in planning_workspace
    assert "roleCapabilitySet" in planning_workspace
    assert "onSetWorkspaceRole" in planning_workspace
    assert "onSetDensityMode" in planning_workspace

    bootstrap_code = (SRC_DIR / "app" / "bootstrap.js").read_text(encoding="utf-8")
    assert "WORKSPACE_ROLE_OPTIONS" in bootstrap_code
    assert "DENSITY_MODE_OPTIONS" in bootstrap_code
    assert "setWorkspaceRole" in bootstrap_code
    assert "setDensityMode" in bootstrap_code

    render_code = (SRC_DIR / "app" / "render.js").read_text(encoding="utf-8")
    assert "data-density-mode" in render_code
    assert "data-workspace-role" in render_code
    assert "stageBannerExperience" in render_code

    styles = (SRC_DIR / "styles" / "shell.css").read_text(encoding="utf-8")
    assert ".density-analysis" in styles
    assert ".density-presentation" in styles
    assert ".planning-map-hud" in styles


def test_world_game_studio_next_wg_p8_analysis_overlay_surfaces_exist():
    state_store = (SRC_DIR / "state" / "store.js").read_text(encoding="utf-8")
    assert "hotspotThreshold" in state_store
    assert "selectedHotspotRegionId" in state_store
    assert "selectedCheckpointTurn" in state_store

    compare_workspace = (SRC_DIR / "compare" / "compareWorkspace.js").read_text(encoding="utf-8")
    assert "compare-hotspot-threshold" in compare_workspace
    assert "onSetCompareHotspot" in compare_workspace
    assert "onInspectProvenanceFromCompareHotspot" in compare_workspace
    assert "compare-hotspots" in compare_workspace

    replay_workspace = (SRC_DIR / "replay" / "replayWorkspace.js").read_text(encoding="utf-8")
    assert "replay-checkpoints" in replay_workspace
    assert "onJumpReplayCheckpoint" in replay_workspace
    assert "onInspectProvenanceFromReplayCheckpoint" in replay_workspace

    planning_workspace = (SRC_DIR / "world_canvas" / "planningWorkspace.js").read_text(encoding="utf-8")
    assert "compare.selectedHotspotRegionId" in planning_workspace
    assert "replay.selectedCheckpointTurn" in planning_workspace
    assert "selected region" in planning_workspace

    map_adapter = (SRC_DIR / "world_canvas" / "mapAdapters.js").read_text(encoding="utf-8")
    assert "analysis.replay_checkpoints" in map_adapter
    assert "Compare Hotspot Gap" in map_adapter

    canvas_code = (SRC_DIR / "world_canvas" / "dymaxionCanvas.js").read_text(encoding="utf-8")
    assert "dymaxion-compare-hotspot-region" in canvas_code
    assert "dymaxion-replay-checkpoint-region" in canvas_code

    bootstrap_code = (SRC_DIR / "app" / "bootstrap.js").read_text(encoding="utf-8")
    assert "setCompareThreshold" in bootstrap_code
    assert "setCompareHotspot" in bootstrap_code
    assert "jumpReplayCheckpoint" in bootstrap_code
    assert "compare hotspot" in bootstrap_code
    assert "replay checkpoint turn" in bootstrap_code


def test_world_game_studio_next_wg_p9_facilitation_shared_attention_and_role_maturity_surfaces_exist():
    state_store = (SRC_DIR / "state" / "store.js").read_text(encoding="utf-8")
    assert "presenterActorId" in state_store
    assert "followPresenter" in state_store
    assert "sharedAttentionStatus" in state_store

    shell_code = (SRC_DIR / "app" / "shell.js").read_text(encoding="utf-8")
    assert "stage-banner-attention" in shell_code
    assert "room-state-summary" in shell_code

    render_code = (SRC_DIR / "app" / "render.js").read_text(encoding="utf-8")
    assert "stageBannerAttention" in render_code
    assert "Presenter" in render_code
    assert "roomStateSummary" in render_code

    planning_workspace = (SRC_DIR / "world_canvas" / "planningWorkspace.js").read_text(encoding="utf-8")
    assert "ROLE_EMPHASIS" in planning_workspace
    assert "planning-role-emphasis-summary" in planning_workspace
    assert "planning-queue-triage-summary" in planning_workspace
    assert "planning-presenter-select" in planning_workspace
    assert "planning-follow-presenter" in planning_workspace
    assert "planning-attention-sync-summary" in planning_workspace
    assert "planning-refresh-continuity" in planning_workspace
    assert "planning-continuity-events" in planning_workspace
    assert "queueTriageSummary" in planning_workspace
    assert "unresolvedEvidenceProposalIds" in planning_workspace

    bootstrap_code = (SRC_DIR / "app" / "bootstrap.js").read_text(encoding="utf-8")
    assert "ROLE_PRESET_CONFIG" in bootstrap_code
    assert "setPresenterActor" in bootstrap_code
    assert "setFollowPresenter" in bootstrap_code
    assert "refreshContinuity" in bootstrap_code

    styles = (SRC_DIR / "styles" / "shell.css").read_text(encoding="utf-8")
    assert ".queue-triage-chip" in styles
    assert "data-workspace-role=\"facilitator\"" in styles
    assert "data-workspace-role=\"analyst\"" in styles
    assert "data-workspace-role=\"delegate\"" in styles
    assert "data-workspace-role=\"observer\"" in styles


def test_world_game_studio_next_wg_p6_cutover_and_playbook_docs_exist():
    decision_doc = STUDIO_NEXT_DIR / "WG-P6_CUTOVER_CONTAINMENT_DECISION.md"
    assert decision_doc.exists()
    assert (REPO_ROOT / "playbooks" / "world-game-studio-next-demo.md").exists()
    decision_text = decision_doc.read_text(encoding="utf-8")
    assert "Legacy retirement is now complete" in decision_text
    assert not (REPO_ROOT / "labs" / "world_game_studio").exists()


def test_world_game_studio_next_wg_p10_browser_e2e_and_stabilization_surfaces_exist():
    planning_workspace = (SRC_DIR / "world_canvas" / "planningWorkspace.js").read_text(encoding="utf-8")
    assert "RESPONSIVENESS_BUDGETS_MS" in planning_workspace
    assert "__WG_STUDIO_NEXT_DIAGNOSTICS" in planning_workspace
    assert "planning-performance-summary" in planning_workspace
    assert "map_redraw_p95" in planning_workspace
    assert "replay_scrub_p95" in planning_workspace
    assert "overlay_toggle_p95" in planning_workspace

    browser_e2e_test = REPO_ROOT / "tests" / "labs" / "test_world_game_studio_next_browser_e2e.py"
    assert browser_e2e_test.exists()
    browser_e2e_code = browser_e2e_test.read_text(encoding="utf-8")
    assert "safaridriver" in browser_e2e_code
    assert "WebDriverSession" in browser_e2e_code
    assert "__WG_STUDIO_NEXT_DIAGNOSTICS" in browser_e2e_code
    assert "#/compare" in browser_e2e_code
    assert "#/replay" in browser_e2e_code
    assert "#/facilitate" in browser_e2e_code

    readme = (STUDIO_NEXT_DIR / "README.md").read_text(encoding="utf-8")
    assert "WG-P10" in readme
    assert "browser E2E" in readme
    assert "replay scrub" in readme

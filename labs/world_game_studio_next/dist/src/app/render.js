import { deriveRegionInspector } from "../world_canvas/mapAdapters.js";

const ROUTE_COPY = {
  onboard: {
    title: "Onboard",
    description:
      "Onboard mode guides first-run setup and demo flow across scenario loading, proposal adoption, simulation, compare, replay, provenance, and facilitation.",
  },
  plan: {
    title: "Plan",
    description: "Plan mode keeps the Dymaxion canvas, proposal scope, and branch focus synchronized.",
  },
  simulate: {
    title: "Simulate",
    description: "Simulation mode runs turns through runtime and reflects deltas in map and inspector surfaces.",
  },
  compare: {
    title: "Compare",
    description: "Compare mode supports baseline-vs-branch and branch-vs-branch reasoning with delta, split, and ghost views.",
  },
  replay: {
    title: "Replay",
    description: "Replay mode provides timeline loading, stepping, scrubbing, and turn-linked map and inspector state.",
  },
  facilitate: {
    title: "Facilitate",
    description: "Facilitation mode keeps stage controls, participant context, proposal moderation, and persistence cues visible around the map.",
  },
};

function summarizeSelection(selection) {
  const scopedRegions = selection.proposalRegionIds || [];
  if (scopedRegions.length > 1) {
    return `${scopedRegions.length} scoped regions (${scopedRegions.join(", ")})`;
  }
  if (scopedRegions.length === 1) {
    return `region ${scopedRegions[0]}`;
  }
  if (selection.proposalId) {
    return `proposal ${selection.proposalId}`;
  }
  if (selection.annotationId) {
    return `annotation ${selection.annotationId}`;
  }
  return "none";
}

function updateScenarioOptions(shell, scenarios, activeScenarioId) {
  shell.scenarioSelect.innerHTML = "";

  if (!Array.isArray(scenarios) || scenarios.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "(no scenarios loaded)";
    shell.scenarioSelect.appendChild(option);
    return;
  }

  for (const scenario of scenarios) {
    const option = document.createElement("option");
    option.value = scenario.scenario_id;
    option.textContent = `${scenario.label} (${scenario.scenario_id})`;
    if (activeScenarioId && scenario.scenario_id === activeScenarioId) {
      option.selected = true;
    }
    shell.scenarioSelect.appendChild(option);
  }
}

function updateServiceList(shell) {
  const services = [
    "scenarioService",
    "sessionService",
    "simulationService",
    "proposalService",
    "branchService",
    "replayService",
    "annotationService",
    "provenanceService",
    "authoringService",
  ];

  shell.serviceList.innerHTML = "";
  for (const service of services) {
    const item = document.createElement("li");
    item.textContent = service;
    shell.serviceList.appendChild(item);
  }
}

function updateWorkspace(shell, route, state) {
  const copy = ROUTE_COPY[route] || ROUTE_COPY.plan;
  const role = state.experience?.workspaceRole || "facilitator";
  const densityMode = state.experience?.densityMode || "default";
  shell.workspaceTitle.textContent = copy.title;
  shell.workspaceDescription.textContent = `${copy.description} Preset: ${role}. Density: ${densityMode}.`;
}

function updateScreenReaderStatus(shell, state) {
  const route = state.route || "onboard";
  const stage = state.session.sessionState?.facilitation_state?.stage || "setup";
  const selection = summarizeSelection(state.selection);
  const compareTarget = state.compare.targetBranchIds?.[0] || "none";
  const replayFrames = Array.isArray(state.replay.frames) ? state.replay.frames.length : 0;
  const attention = state.facilitation.presenterActorId || "none";
  shell.screenReaderStatus.textContent =
    `Mode ${route}. Stage ${stage}. Selection ${selection}. ` +
    `Compare target ${compareTarget}. Replay frames ${replayFrames}. Presenter ${attention}.`;
}

function updateStageBanner(shell, state) {
  const facilitationState = state.session.sessionState?.facilitation_state || {};
  const stage = facilitationState.stage || "setup";
  const allowed = facilitationState.allowed_actions?.[stage] || [];
  const spotlight = state.facilitation.spotlightRegionId || "none";
  const attentionStatus = state.facilitation.sharedAttentionStatus || "local-only";
  const presenter = state.facilitation.presenterActorId || "none";
  const followPresenter = state.facilitation.followPresenter ? "follow on" : "follow off";
  const workspaceRole = state.experience?.workspaceRole || "facilitator";
  const densityMode = state.experience?.densityMode || "default";

  shell.stageBannerStage.textContent = `Stage: ${stage}`;
  shell.stageBannerActions.textContent = allowed.length
    ? `Allowed actions: ${allowed.join(", ")}`
    : "Allowed actions: (runtime defaults)";
  shell.stageBannerSpotlight.textContent = `Spotlight: ${spotlight}`;
  shell.stageBannerAttention.textContent = `Attention: ${attentionStatus} · Presenter ${presenter} (${followPresenter})`;
  shell.stageBannerExperience.textContent = `Workspace: ${workspaceRole} · Density: ${densityMode}`;
}

function renderFallbackWorkspace(shell, state) {
  shell.workspaceContent.innerHTML = "";

  const content = document.createElement("div");
  content.className = "workspace-grid";
  content.innerHTML = `
    <article class="workspace-card">
      <h3>Scenario</h3>
      <p>${state.scenario.activeScenarioId || "No scenario selected"}</p>
    </article>
    <article class="workspace-card">
      <h3>Session</h3>
      <p>${state.session.sessionId || "No session"}</p>
    </article>
    <article class="workspace-card">
      <h3>Branch</h3>
      <p>${state.branch.activeBranchId || "No branch"}</p>
    </article>
    <article class="workspace-card">
      <h3>Pending Requests</h3>
      <p>${state.runtime.pendingRequests}</p>
    </article>
  `;
  shell.workspaceContent.appendChild(content);
}

function updateWorkspaceContent(shell, state, integrations) {
  const planningWorkspace = integrations?.planningWorkspace || null;
  if (!planningWorkspace) {
    renderFallbackWorkspace(shell, state);
    return;
  }

  if (!shell.workspaceContent.contains(planningWorkspace.root)) {
    shell.workspaceContent.innerHTML = "";
    shell.workspaceContent.appendChild(planningWorkspace.root);
  }
  planningWorkspace.render(state, integrations.geometryPackage);
}

function updateInspector(shell, state, route) {
  shell.inspectorRoute.textContent = `Mode: ${route}`;
  shell.inspectorStage.textContent = `Stage: ${
    state.session.sessionState?.facilitation_state?.stage || "setup"
  }`;
  shell.inspectorBranch.textContent = `Branch: ${state.branch.activeBranchId || "none"}`;
  shell.inspectorSelection.textContent = `Selection: ${summarizeSelection(state.selection)}`;

  const regionMetrics = deriveRegionInspector(state, state.selection.regionId);
  shell.inspectorRegionMetrics.innerHTML = "";
  if (!regionMetrics.length) {
    const empty = document.createElement("li");
    empty.textContent = "Region metrics will appear after selecting a region.";
    shell.inspectorRegionMetrics.appendChild(empty);
  } else {
    for (const metric of regionMetrics) {
      const item = document.createElement("li");
      item.textContent = `${metric.label}: ${metric.value}`;
      shell.inspectorRegionMetrics.appendChild(item);
    }
  }

  const provenanceType = state.provenance.artifactType || "none";
  const provenanceId = state.provenance.artifactId || "none";
  shell.inspectorProvenance.textContent = `Provenance: ${provenanceType}:${provenanceId}`;
}

function updateNotifications(shell, notifications) {
  shell.notificationList.innerHTML = "";

  if (!notifications.length) {
    const empty = document.createElement("li");
    empty.textContent = "No notifications yet.";
    shell.notificationList.appendChild(empty);
    return;
  }

  for (const notification of notifications) {
    const item = document.createElement("li");
    item.textContent = `[${notification.level}] ${notification.message}`;
    shell.notificationList.appendChild(item);
  }
}

export function renderStudioShell(shell, state, integrations = null) {
  const route = state.route;
  const densityMode = state.experience?.densityMode || "default";
  const workspaceRole = state.experience?.workspaceRole || "facilitator";
  shell.root.classList.toggle("presentation-mode", Boolean(state.facilitation.presentationMode));
  shell.root.classList.toggle("reduced-motion", Boolean(state.accessibility?.reducedMotion));
  shell.root.classList.toggle("density-default", densityMode === "default");
  shell.root.classList.toggle("density-analysis", densityMode === "analysis");
  shell.root.classList.toggle("density-presentation", densityMode === "presentation");
  shell.root.classList.toggle("role-facilitator", workspaceRole === "facilitator");
  shell.root.classList.toggle("role-analyst", workspaceRole === "analyst");
  shell.root.classList.toggle("role-delegate", workspaceRole === "delegate");
  shell.root.classList.toggle("role-observer", workspaceRole === "observer");
  shell.root.setAttribute("data-route", route);
  shell.root.setAttribute("data-density-mode", densityMode);
  shell.root.setAttribute("data-workspace-role", workspaceRole);
  if (shell.reducedMotionToggle && document.activeElement !== shell.reducedMotionToggle) {
    shell.reducedMotionToggle.checked = Boolean(state.accessibility?.reducedMotion);
  }
  if (shell.workspaceRoleSelect && document.activeElement !== shell.workspaceRoleSelect) {
    shell.workspaceRoleSelect.value = workspaceRole;
  }
  if (shell.densityModeSelect && document.activeElement !== shell.densityModeSelect) {
    shell.densityModeSelect.value = densityMode;
  }

  for (const button of shell.routeButtons) {
    button.classList.toggle("active", button.dataset.route === route);
  }

  const runtimeBusy = state.runtime.pendingRequests > 0;
  shell.runtimeStatusPill.textContent = runtimeBusy
    ? `Running ${state.runtime.lastMethod || "request"}`
    : "Idle";
  shell.runtimeStatusPill.classList.toggle("busy", runtimeBusy);
  shell.runtimeStatusPill.setAttribute("aria-busy", runtimeBusy ? "true" : "false");

  shell.sessionSummary.textContent = state.session.sessionId
    ? `Session ${state.session.sessionId}`
    : "No active session.";
  shell.roomStateSummary.textContent = state.session.sessionId
    ? `Room state: ${state.session.sessionState?.session_meta?.label || "Workshop room"}`
    : "Room state: waiting for session.";
  const actors = state.session.sessionState?.actors || [];
  shell.participantSummary.textContent = actors.length
    ? `${actors.length} actor(s) in session`
    : "No actors in session.";
  shell.participantList.innerHTML = "";
  for (const actor of actors.slice(0, 6)) {
    const item = document.createElement("li");
    item.textContent = `${actor.display_name || actor.actor_id} (${(actor.roles || []).join(", ") || "observer"})`;
    shell.participantList.appendChild(item);
  }
  if (!actors.length) {
    const empty = document.createElement("li");
    empty.textContent = "Add participants in Facilitate mode.";
    shell.participantList.appendChild(empty);
  }
  shell.proposalQueueSummary.textContent = state.planning.proposals.length
    ? `${state.planning.proposals.length} proposal(s), ${state.planning.proposals.filter((item) => item.status === "submitted").length} submitted`
    : "No proposals.";

  shell.branchSummary.textContent = state.branch.activeBranchId
    ? `Active branch ${state.branch.activeBranchId}`
    : "No branch loaded.";

  shell.layerSummary.textContent = state.layers.visibleLayerIds.length
    ? `${state.layers.visibleLayerIds.length} layer(s) visible`
    : "Layer manifest not loaded yet.";

  updateInspector(shell, state, route);
  const compareTarget = state.compare.targetBranchIds?.[0] || null;
  const selectedHotspotRegionId = state.compare.selectedHotspotRegionId || null;
  shell.inspectorCompare.textContent = compareTarget
    ? `Compare: ${state.compare.baselineBranchId || "baseline"} vs ${compareTarget} (${state.compare.visualizationMode || "delta"})${selectedHotspotRegionId ? ` · hotspot ${selectedHotspotRegionId}` : ""}`
    : "Compare set: none";

  const replayFrames = state.replay.frames || [];
  const replayCheckpoint = state.replay.selectedCheckpointTurn;
  shell.dockReplay.textContent = state.replay.branchId
    ? `Replay: ${state.replay.branchId} @ ${state.replay.cursorIndex ?? 0}/${Math.max(0, replayFrames.length - 1)}${replayCheckpoint === null ? "" : ` · checkpoint ${replayCheckpoint}`}`
    : "Replay: not started";

  updateScenarioOptions(shell, state.scenario.list, state.scenario.activeScenarioId);
  updateStageBanner(shell, state);
  updateWorkspace(shell, route, state);
  updateWorkspaceContent(shell, state, integrations);
  updateServiceList(shell);
  updateNotifications(shell, state.notifications.items);
  updateScreenReaderStatus(shell, state);
}

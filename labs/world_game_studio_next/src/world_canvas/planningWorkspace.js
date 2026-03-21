import { createCompareWorkspace } from "../compare/compareWorkspace.js";
import { createProvenanceDrawer } from "../provenance/provenanceDrawer.js";
import { createReplayWorkspace } from "../replay/replayWorkspace.js";
import { createDymaxionCanvas } from "./dymaxionCanvas.js";
import {
  DOMINANT_REGION_LAYER_OPTIONS,
  WORLD_CANVAS_LAYER_DEFINITIONS,
  deriveCanvasModel,
} from "./mapAdapters.js";

const STAGE_OPTIONS = ["setup", "proposal_intake", "deliberation", "selection", "simulation", "review", "closed"];
const ACTOR_ROLE_OPTIONS = ["facilitator", "analyst", "approver", "observer"];
const PROPOSAL_QUEUE_FILTERS = ["all", "draft", "submitted", "under_review", "adopted", "rejected"];
const WORKSPACE_ROLE_OPTIONS = ["facilitator", "analyst", "delegate", "observer"];
const DENSITY_MODE_OPTIONS = ["default", "analysis", "presentation"];
const ROLE_EMPHASIS = {
  facilitator: {
    queueFilter: "submitted",
    summary: "Facilitator emphasis: room controls, queue decisions, and shared spotlight cues.",
  },
  analyst: {
    queueFilter: "under_review",
    summary: "Analyst emphasis: unresolved evidence, compare context, and replay-informed triage.",
  },
  delegate: {
    queueFilter: "draft",
    summary: "Delegate emphasis: proposal drafting, submission readiness, and regional concerns.",
  },
  observer: {
    queueFilter: "submitted",
    summary: "Observer emphasis: session transparency, spotlight context, and debrief visibility.",
  },
};

function routeGroupVisibility(route) {
  const normalizedRoute = route || "plan";
  return {
    showBranch: normalizedRoute !== "onboard",
    showFacilitation: normalizedRoute === "facilitate",
    showParticipants: normalizedRoute === "facilitate",
    showLayers: normalizedRoute !== "onboard",
    showProposal: normalizedRoute === "plan" || normalizedRoute === "simulate" || normalizedRoute === "facilitate",
    showQueue: normalizedRoute === "plan" || normalizedRoute === "facilitate",
    showTurn: normalizedRoute === "simulate" || normalizedRoute === "plan" || normalizedRoute === "facilitate",
    showAnnotation: normalizedRoute === "plan" || normalizedRoute === "simulate" || normalizedRoute === "facilitate",
    showSpotlight: normalizedRoute === "facilitate",
    showPersistence: normalizedRoute === "facilitate",
    showSnapshot: normalizedRoute !== "onboard",
  };
}

function roleCapabilitySet(role) {
  const normalized = role || "facilitator";
  if (normalized === "observer") {
    return {
      canStageManage: false,
      canManageParticipants: false,
      canModerateQueue: false,
      canCreateProposal: false,
      canSubmitProposal: false,
      canAdoptProposal: false,
      canRejectProposal: false,
      canRunTurn: false,
      canAnnotate: false,
      canSpotlight: false,
      canPersist: false,
    };
  }
  if (normalized === "analyst") {
    return {
      canStageManage: false,
      canManageParticipants: false,
      canModerateQueue: false,
      canCreateProposal: true,
      canSubmitProposal: true,
      canAdoptProposal: false,
      canRejectProposal: false,
      canRunTurn: true,
      canAnnotate: true,
      canSpotlight: false,
      canPersist: false,
    };
  }
  if (normalized === "delegate") {
    return {
      canStageManage: false,
      canManageParticipants: false,
      canModerateQueue: false,
      canCreateProposal: true,
      canSubmitProposal: true,
      canAdoptProposal: false,
      canRejectProposal: false,
      canRunTurn: false,
      canAnnotate: true,
      canSpotlight: false,
      canPersist: false,
    };
  }
  return {
    canStageManage: true,
    canManageParticipants: true,
    canModerateQueue: true,
    canCreateProposal: true,
    canSubmitProposal: true,
    canAdoptProposal: true,
    canRejectProposal: true,
    canRunTurn: true,
    canAnnotate: true,
    canSpotlight: true,
    canPersist: true,
  };
}

function updateSelectOptions(select, options, selectedValue, emptyLabel) {
  const normalizedOptions = Array.isArray(options) ? options : [];
  select.innerHTML = "";
  if (!normalizedOptions.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = emptyLabel;
    select.appendChild(option);
    select.value = "";
    return;
  }

  for (const item of normalizedOptions) {
    const option = document.createElement("option");
    option.value = item.value;
    option.textContent = item.label;
    select.appendChild(option);
  }
  select.value = selectedValue && normalizedOptions.some((item) => item.value === selectedValue)
    ? selectedValue
    : normalizedOptions[0].value;
}

function branchOptions(state) {
  const entries = Object.entries(state.branch.branches || {});
  return entries
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([branchId, summary]) => ({
      value: branchId,
      label: `${branchId} (turn ${summary.turn ?? 0})`,
    }));
}

function proposalOptions(state) {
  const proposals = state.planning.proposals || [];
  return proposals.map((proposal) => ({
    value: proposal.proposal_id,
    label: `${proposal.title} (${proposal.status})`,
  }));
}

function interventionOptions(state) {
  return (state.scenario.loadedScenario?.intervention_ids || []).map((interventionId) => ({
    value: interventionId,
    label: interventionId,
  }));
}

function shockOptions(state) {
  const options = (state.scenario.loadedScenario?.shock_ids || []).map((shockId) => ({
    value: shockId,
    label: shockId,
  }));
  return [{ value: "", label: "(none)" }, ...options];
}

function regionOptions(geometryPackage) {
  const regions = geometryPackage?.regions?.regions || [];
  return regions
    .filter((region) => region?.region_id)
    .slice()
    .sort((left, right) => String(left.label || left.region_id).localeCompare(String(right.label || right.region_id)))
    .map((region) => ({
      value: region.region_id,
      label: `${region.label || region.region_id} (${region.region_id})`,
    }));
}

function onboardingChecklist(state) {
  const proposals = state.planning.proposals || [];
  const actors = state.session.sessionState?.actors || [];
  const stage = state.session.sessionState?.facilitation_state?.stage || "setup";
  return [
    { label: "Create a session", complete: Boolean(state.session.sessionId) },
    { label: "Load a scenario", complete: Boolean(state.scenario.loadedScenario) },
    {
      label: "Create and submit a proposal",
      complete: proposals.some((proposal) =>
        ["submitted", "under_review", "adopted", "rejected"].includes(proposal.status),
      ),
    },
    { label: "Run one turn", complete: Boolean(state.planning.lastTurnResult) },
    { label: "Run branch compare", complete: Boolean(state.compare.result) },
    { label: "Load replay timeline", complete: Array.isArray(state.replay.frames) && state.replay.frames.length > 0 },
    { label: "Inspect provenance", complete: Boolean(state.provenance.result) },
    {
      label: "Use facilitation controls",
      complete: actors.length > 1 || stage !== "setup" || Boolean(state.facilitation.persistenceSummary),
    },
  ];
}

function routeAllowsPlanningLoop(route) {
  return route === "plan" || route === "simulate" || route === "facilitate";
}

function inferProvenanceContext(state) {
  if (state.compare.selectedHotspotRegionId) {
    const target = state.compare.targetBranchIds?.[0] || state.branch.activeBranchId || null;
    if (target) {
      return {
        artifactType: "branch",
        artifactId: target,
        contextLabel: `compare hotspot ${state.compare.selectedHotspotRegionId}`,
      };
    }
  }

  if (state.replay.selectedCheckpointTurn !== null && state.replay.selectedCheckpointTurn !== undefined) {
    const replayBranchId = state.replay.branchId || state.branch.activeBranchId || null;
    if (replayBranchId) {
      return {
        artifactType: "branch",
        artifactId: replayBranchId,
        contextLabel: `replay checkpoint turn ${state.replay.selectedCheckpointTurn}`,
      };
    }
  }

  if (state.selection.regionId) {
    const regionBranchId = state.branch.activeBranchId || null;
    if (regionBranchId) {
      return {
        artifactType: "branch",
        artifactId: regionBranchId,
        contextLabel: `selected region ${state.selection.regionId}`,
      };
    }
  }

  if (state.route === "compare") {
    const target = state.compare.targetBranchIds?.[0] || null;
    if (target) {
      return { artifactType: "branch", artifactId: target, contextLabel: "compare target" };
    }
  }

  if (state.route === "replay") {
    const replayBranchId = state.replay.branchId || null;
    if (replayBranchId) {
      return { artifactType: "branch", artifactId: replayBranchId, contextLabel: "replay branch" };
    }
  }

  if (state.selection.proposalId) {
    return {
      artifactType: "proposal",
      artifactId: state.selection.proposalId,
      contextLabel: "selected proposal",
    };
  }

  if (state.selection.annotationId) {
    return {
      artifactType: "annotation",
      artifactId: state.selection.annotationId,
      contextLabel: "selected annotation",
    };
  }

  if (state.branch.activeBranchId) {
    return {
      artifactType: "branch",
      artifactId: state.branch.activeBranchId,
      contextLabel: "active branch",
    };
  }

  return null;
}

function snapshotPayload(state) {
  const turnResult = state.planning.lastTurnResult?.turn_result || null;
  const branchSummary = state.branch.activeBranchId
    ? state.branch.branches?.[state.branch.activeBranchId] || null
    : null;
  const replayFrames = Array.isArray(state.replay.frames) ? state.replay.frames : [];
  const replayCursor = Math.max(0, Math.min(replayFrames.length - 1, Number(state.replay.cursorIndex ?? 0)));
  const replayFrame = replayFrames[replayCursor] || null;

  return {
    route: state.route,
    active_branch_id: state.branch.activeBranchId,
    turn: branchSummary?.turn ?? 0,
    composite_score: branchSummary?.composite_score ?? null,
    policy_outcome: turnResult?.policy_outcome || null,
    committed: turnResult?.committed ?? null,
    proposal_id: state.planning.activeProposalId || null,
    network_mode: state.planning.networkSnapshot?.latest_turn_diagnostics?.mode || null,
    facilitation: {
      stage: state.session.sessionState?.facilitation_state?.stage || "setup",
      queue_filter: state.facilitation.queueFilter,
      spotlight_region_id: state.facilitation.spotlightRegionId || null,
      presentation_mode: Boolean(state.facilitation.presentationMode),
      presenter_actor_id: state.facilitation.presenterActorId || null,
      follow_presenter: Boolean(state.facilitation.followPresenter),
      attention_sync: state.facilitation.sharedAttentionStatus || "local-only",
    },
    compare_pair: {
      baseline: state.compare.baselineBranchId,
      target: state.compare.targetBranchIds?.[0] || null,
      mode: state.compare.visualizationMode,
      has_result: Boolean(state.compare.result),
    },
    replay: {
      branch_id: state.replay.branchId,
      frame_count: replayFrames.length,
      cursor_index: replayFrame ? replayCursor : null,
      turn_index: replayFrame?.turn_index ?? null,
      replay_matches_live: state.replay.result?.replay_matches_live ?? null,
    },
    provenance: {
      artifact_type: state.provenance.artifactType || null,
      artifact_id: state.provenance.artifactId || null,
      loaded: Boolean(state.provenance.result),
    },
  };
}

function queueProposals(state) {
  const proposals = state.planning.proposals || [];
  const filter = state.facilitation.queueFilter || "all";
  const filtered = filter === "all" ? proposals : proposals.filter((proposal) => proposal.status === filter);
  return filtered.slice().sort((left, right) => String(left.proposal_id).localeCompare(String(right.proposal_id)));
}

function unresolvedEvidenceProposalIds(state) {
  const annotations = state.planning.annotations || [];
  const missingFromEvidenceRefs = (state.planning.proposals || [])
    .filter((proposal) => (proposal.evidence_refs || []).length === 0)
    .map((proposal) => proposal.proposal_id);
  const evidenceGapTargets = annotations
    .filter((annotation) => annotation.target_type === "proposal" && annotation.annotation_type === "evidence-gap")
    .map((annotation) => annotation.target_id);
  return new Set([...missingFromEvidenceRefs, ...evidenceGapTargets].filter((proposalId) => Boolean(proposalId)));
}

function queueTriageSummary(state) {
  const proposals = state.planning.proposals || [];
  const unresolvedIds = unresolvedEvidenceProposalIds(state);
  const submitted = proposals.filter((proposal) => proposal.status === "submitted" || proposal.status === "under_review");
  const readyToAdopt = submitted.filter((proposal) => !unresolvedIds.has(proposal.proposal_id));
  return {
    reviewCount: submitted.length,
    unresolvedCount: unresolvedIds.size,
    readyCount: readyToAdopt.length,
    unresolvedIds,
  };
}

function continuityEvents(state) {
  const timeline = state.session.sessionState?.timeline || [];
  if (!Array.isArray(timeline) || !timeline.length) {
    return [];
  }
  return timeline.slice(-5).reverse();
}

function stageActionSet(state) {
  const facilitationState = state.session.sessionState?.facilitation_state || {};
  const stage = facilitationState.stage || "setup";
  const actions = facilitationState.allowed_actions?.[stage] || [];
  return new Set(actions);
}

function isStageActionAllowed(allowedActions, actionId) {
  return !allowedActions.size || allowedActions.has(actionId);
}

function canvasRenderFingerprint(canvasModel) {
  return JSON.stringify({
    route: canvasModel.route,
    dominantLayerId: canvasModel.dominantLayerId,
    dominantScale: canvasModel.dominantScale,
    dominantValues: canvasModel.dominantValues,
    visibleLayerIds: canvasModel.visibleLayerIds,
    selectedRegionId: canvasModel.selectedRegionId,
    hoveredRegionId: canvasModel.hoveredRegionId,
    proposalRegionIds: canvasModel.proposalRegionIds,
    annotationCounts: canvasModel.annotationCounts,
    viewport: canvasModel.viewport,
    spotlightRegionId: canvasModel.spotlightRegionId,
    presentationMode: canvasModel.presentationMode,
    flowLines: (canvasModel.flowLines || []).map((line) => ({
      flowId: line.flowId,
      transfer: line.transfer,
      capacity: line.capacity,
    })),
    compareOverlay: canvasModel.compareOverlay
      ? {
          mode: canvasModel.compareOverlay.mode,
          baselineBranchId: canvasModel.compareOverlay.baselineBranchId,
          targetBranchId: canvasModel.compareOverlay.targetBranchId,
          topDeltaRegionIds: canvasModel.compareOverlay.topDeltaRegionIds,
          selectedHotspotRegionId: canvasModel.compareOverlay.selectedHotspotRegionId,
          ghostRegionIds: canvasModel.compareOverlay.ghostRegionIds,
        }
      : null,
    replayOverlay: canvasModel.replayOverlay
      ? {
          branchId: canvasModel.replayOverlay.branchId,
          cursorIndex: canvasModel.replayOverlay.cursorIndex,
          frameCount: canvasModel.replayOverlay.frameCount,
          selectedCheckpointTurn: canvasModel.replayOverlay.selectedCheckpointTurn,
          checkpointRegionIds: canvasModel.replayOverlay.checkpointRegionIds,
        }
      : null,
  });
}

const RESPONSIVENESS_BUDGETS_MS = {
  map_redraw_p95: 120,
  replay_scrub_p95: 180,
  overlay_toggle_p95: 150,
};

function percentile(values, fraction) {
  if (!Array.isArray(values) || !values.length) {
    return null;
  }
  const sorted = values.slice().sort((left, right) => left - right);
  const index = Math.min(sorted.length - 1, Math.max(0, Math.ceil(sorted.length * fraction) - 1));
  return Number(sorted[index].toFixed(2));
}

function createResponsivenessDiagnostics() {
  const samples = {
    map_redraw: [],
    replay_scrub: [],
    overlay_toggle: [],
  };

  function record(metric, value) {
    if (!Object.prototype.hasOwnProperty.call(samples, metric) || !Number.isFinite(value)) {
      return;
    }
    const bucket = samples[metric];
    bucket.push(Number(value.toFixed(2)));
    if (bucket.length > 80) {
      bucket.shift();
    }
  }

  function summary(metric) {
    const bucket = samples[metric] || [];
    return {
      sample_count: bucket.length,
      last_ms: bucket.length ? bucket[bucket.length - 1] : null,
      p95_ms: percentile(bucket, 0.95),
      max_ms: bucket.length ? Number(Math.max(...bucket).toFixed(2)) : null,
    };
  }

  function snapshot() {
    return {
      budgets_ms: RESPONSIVENESS_BUDGETS_MS,
      map_redraw: summary("map_redraw"),
      replay_scrub: summary("replay_scrub"),
      overlay_toggle: summary("overlay_toggle"),
    };
  }

  function publish() {
    if (typeof window === "undefined") {
      return;
    }
    window.__WG_STUDIO_NEXT_DIAGNOSTICS = snapshot();
  }

  return {
    record,
    snapshot,
    publish,
  };
}

export function createPlanningWorkspace(container, actions) {
  const root = document.createElement("div");
  root.id = "world-planning-workspace";
  root.className = "planning-workspace";
  root.innerHTML = `
    <section class="planning-map-pane panel-block">
      <header class="planning-pane-header">
        <h3>Dymaxion Canvas</h3>
        <p class="muted">Shift-click to build proposal scope. Drag to pan. Compare and replay routes stay map-linked.</p>
      </header>
      <div id="planning-map-hud" class="planning-map-hud" role="status" aria-live="polite">
        <p id="planning-hud-route">Mode: plan</p>
        <p id="planning-hud-branch">Branch: none</p>
        <p id="planning-hud-selection">Selection: none</p>
        <p id="planning-hud-experience">Preset: facilitator · Density: default</p>
        <p id="planning-hud-attention">Attention: local-only</p>
      </div>
      <div id="world-canvas-root" class="world-canvas-root"></div>
    </section>
    <aside class="planning-control-pane panel-block">
      <section class="planning-control-group" id="planning-experience-group">
        <h3>Workspace Preset</h3>
        <label>
          Role
          <select id="planning-workspace-role"></select>
        </label>
        <label>
          Density mode
          <select id="planning-density-mode"></select>
        </label>
        <p class="muted" id="planning-role-emphasis-summary">Facilitator emphasis: room controls and queue triage.</p>
      </section>
      <section class="planning-control-group" id="planning-branch-group">
        <h3>Branch Focus</h3>
        <label>
          Active branch
          <select id="planning-branch-select"></select>
        </label>
        <label>
          Region navigator
          <select id="planning-region-select"></select>
        </label>
        <button type="button" id="planning-focus-region">Focus region</button>
        <p class="muted" id="planning-stage">Stage: setup</p>
        <button type="button" id="planning-refresh-network">Refresh network snapshot</button>
      </section>
      <section class="planning-control-group" id="planning-facilitation-group">
        <h3>Facilitation</h3>
        <label>
          Stage
          <select id="planning-stage-select"></select>
        </label>
        <div class="planning-button-row">
          <button type="button" id="planning-set-stage">Set stage</button>
          <button type="button" id="planning-advance-stage">Advance stage</button>
        </div>
      </section>
      <section class="planning-control-group" id="planning-participants-group">
        <h3>Participants</h3>
        <label>
          Actor ID
          <input id="planning-actor-id" type="text" placeholder="actor.delegate.1" />
        </label>
        <label>
          Role
          <select id="planning-actor-role"></select>
        </label>
        <button type="button" id="planning-add-actor">Add actor</button>
        <ul id="planning-actor-roster" class="planning-inline-list"></ul>
      </section>
      <section class="planning-control-group" id="planning-layers-group">
        <h3>Layers</h3>
        <label>
          Dominant region layer
          <select id="planning-dominant-layer"></select>
        </label>
        <div id="planning-layer-toggles" class="planning-layer-toggles"></div>
      </section>
      <section class="planning-control-group" id="planning-proposal-group">
        <h3>Proposal Loop</h3>
        <label>
          Proposal title
          <input id="planning-proposal-title" type="text" placeholder="Distributed resilience path" />
        </label>
        <label>
          Actor
          <input id="planning-proposal-actor" type="text" placeholder="actor.facilitator" />
        </label>
        <label>
          Active proposal
          <select id="planning-proposal-select"></select>
        </label>
        <div class="planning-button-row">
          <button type="button" id="planning-create-proposal">Create</button>
          <button type="button" id="planning-submit-proposal">Submit</button>
          <button type="button" id="planning-adopt-proposal">Adopt</button>
          <button type="button" id="planning-reject-proposal">Reject</button>
        </div>
      </section>
      <section class="planning-control-group" id="planning-queue-group">
        <h3>Proposal Queue</h3>
        <label>
          Status filter
          <select id="planning-queue-filter"></select>
        </label>
        <p class="muted" id="planning-queue-triage-summary">Review 0 · unresolved evidence 0 · ready 0</p>
        <ul id="planning-proposal-queue" class="planning-inline-list planning-proposal-queue"></ul>
      </section>
      <section class="planning-control-group" id="planning-turn-group">
        <h3>Turn Runner</h3>
        <label>
          Intervention
          <select id="planning-intervention-select"></select>
        </label>
        <label>
          Shock (optional)
          <select id="planning-shock-select"></select>
        </label>
        <button type="button" id="planning-run-turn">Run turn</button>
      </section>
      <section class="planning-control-group" id="planning-annotation-group">
        <h3>Annotations</h3>
        <label>
          Annotation text
          <input id="planning-annotation-body" type="text" placeholder="Note for selected region or branch" />
        </label>
        <button type="button" id="planning-create-annotation">Add annotation</button>
      </section>
      <section class="planning-control-group" id="planning-spotlight-group">
        <h3>Spotlight</h3>
        <p class="muted" id="planning-spotlight-summary">No spotlight region selected.</p>
        <label>
          Presenter
          <select id="planning-presenter-select"></select>
        </label>
        <label class="planning-checkbox">
          <input id="planning-follow-presenter" type="checkbox" />
          Follow presenter focus
        </label>
        <p class="muted" id="planning-attention-sync-summary">Shared attention sync: local-only in this runtime.</p>
        <div class="planning-button-row">
          <button type="button" id="planning-set-spotlight">Spotlight selection</button>
          <button type="button" id="planning-clear-spotlight">Clear spotlight</button>
        </div>
        <label class="planning-checkbox">
          <input id="planning-presentation-mode" type="checkbox" />
          Presentation mode
        </label>
      </section>
      <section class="planning-control-group" id="planning-persistence-group">
        <h3>Session Continuity</h3>
        <div class="planning-button-row">
          <button type="button" id="planning-refresh-continuity">Refresh room state</button>
          <button type="button" id="planning-export-session">Export session</button>
          <button type="button" id="planning-import-session">Import session</button>
        </div>
        <label>
          Session bundle (.json)
          <input id="planning-import-file" type="file" accept=".json,application/json" />
        </label>
        <p class="muted" id="planning-persistence-summary">No persistence actions yet.</p>
        <ul id="planning-continuity-events" class="planning-inline-list"></ul>
      </section>
      <div id="planning-route-panels"></div>
      <section class="planning-control-group" id="planning-snapshot-group">
        <h3>Workspace Snapshot</h3>
        <p class="muted" id="planning-selection-summary">Selection scope: none</p>
        <pre id="planning-result-summary" class="planning-result-summary">{}</pre>
        <pre id="planning-performance-summary" class="planning-result-summary">{"budgets_ms":{}}</pre>
      </section>
    </aside>
  `;
  container.appendChild(root);

  const elements = {
    branchSelect: root.querySelector("#planning-branch-select"),
    branchGroup: root.querySelector("#planning-branch-group"),
    regionSelect: root.querySelector("#planning-region-select"),
    focusRegion: root.querySelector("#planning-focus-region"),
    stage: root.querySelector("#planning-stage"),
    facilitationGroup: root.querySelector("#planning-facilitation-group"),
    stageSelect: root.querySelector("#planning-stage-select"),
    setStage: root.querySelector("#planning-set-stage"),
    advanceStage: root.querySelector("#planning-advance-stage"),
    actorId: root.querySelector("#planning-actor-id"),
    actorRole: root.querySelector("#planning-actor-role"),
    addActor: root.querySelector("#planning-add-actor"),
    participantsGroup: root.querySelector("#planning-participants-group"),
    actorRoster: root.querySelector("#planning-actor-roster"),
    refreshNetwork: root.querySelector("#planning-refresh-network"),
    dominantLayer: root.querySelector("#planning-dominant-layer"),
    layersGroup: root.querySelector("#planning-layers-group"),
    layerToggles: root.querySelector("#planning-layer-toggles"),
    mapHudRoute: root.querySelector("#planning-hud-route"),
    mapHudBranch: root.querySelector("#planning-hud-branch"),
    mapHudSelection: root.querySelector("#planning-hud-selection"),
    mapHudExperience: root.querySelector("#planning-hud-experience"),
    mapHudAttention: root.querySelector("#planning-hud-attention"),
    experienceGroup: root.querySelector("#planning-experience-group"),
    workspaceRole: root.querySelector("#planning-workspace-role"),
    densityMode: root.querySelector("#planning-density-mode"),
    roleEmphasisSummary: root.querySelector("#planning-role-emphasis-summary"),
    proposalGroup: root.querySelector("#planning-proposal-group"),
    proposalTitle: root.querySelector("#planning-proposal-title"),
    proposalActor: root.querySelector("#planning-proposal-actor"),
    proposalSelect: root.querySelector("#planning-proposal-select"),
    createProposal: root.querySelector("#planning-create-proposal"),
    submitProposal: root.querySelector("#planning-submit-proposal"),
    adoptProposal: root.querySelector("#planning-adopt-proposal"),
    rejectProposal: root.querySelector("#planning-reject-proposal"),
    queueGroup: root.querySelector("#planning-queue-group"),
    queueFilter: root.querySelector("#planning-queue-filter"),
    queueTriageSummary: root.querySelector("#planning-queue-triage-summary"),
    proposalQueue: root.querySelector("#planning-proposal-queue"),
    turnGroup: root.querySelector("#planning-turn-group"),
    interventionSelect: root.querySelector("#planning-intervention-select"),
    shockSelect: root.querySelector("#planning-shock-select"),
    runTurn: root.querySelector("#planning-run-turn"),
    annotationGroup: root.querySelector("#planning-annotation-group"),
    annotationBody: root.querySelector("#planning-annotation-body"),
    createAnnotation: root.querySelector("#planning-create-annotation"),
    spotlightGroup: root.querySelector("#planning-spotlight-group"),
    spotlightSummary: root.querySelector("#planning-spotlight-summary"),
    presenterSelect: root.querySelector("#planning-presenter-select"),
    followPresenter: root.querySelector("#planning-follow-presenter"),
    attentionSyncSummary: root.querySelector("#planning-attention-sync-summary"),
    setSpotlight: root.querySelector("#planning-set-spotlight"),
    clearSpotlight: root.querySelector("#planning-clear-spotlight"),
    presentationMode: root.querySelector("#planning-presentation-mode"),
    persistenceGroup: root.querySelector("#planning-persistence-group"),
    refreshContinuity: root.querySelector("#planning-refresh-continuity"),
    exportSession: root.querySelector("#planning-export-session"),
    importSession: root.querySelector("#planning-import-session"),
    importFile: root.querySelector("#planning-import-file"),
    persistenceSummary: root.querySelector("#planning-persistence-summary"),
    continuityEvents: root.querySelector("#planning-continuity-events"),
    routePanels: root.querySelector("#planning-route-panels"),
    snapshotGroup: root.querySelector("#planning-snapshot-group"),
    selectionSummary: root.querySelector("#planning-selection-summary"),
    resultSummary: root.querySelector("#planning-result-summary"),
    performanceSummary: root.querySelector("#planning-performance-summary"),
  };

  for (const layer of WORLD_CANVAS_LAYER_DEFINITIONS) {
    const wrapper = document.createElement("label");
    wrapper.className = "planning-layer-toggle";
    wrapper.innerHTML = `
      <input type="checkbox" data-layer-id="${layer.id}" />
      ${layer.label}
    `;
    elements.layerToggles.appendChild(wrapper);
  }

  updateSelectOptions(
    elements.dominantLayer,
    DOMINANT_REGION_LAYER_OPTIONS.map((item) => ({ value: item.id, label: item.label })),
    "state.water_security",
    "(no dominant layer)",
  );
  updateSelectOptions(
    elements.stageSelect,
    STAGE_OPTIONS.map((stage) => ({ value: stage, label: stage })),
    "setup",
    "(no stages)",
  );
  updateSelectOptions(
    elements.actorRole,
    ACTOR_ROLE_OPTIONS.map((role) => ({ value: role, label: role })),
    "analyst",
    "(no roles)",
  );
  updateSelectOptions(
    elements.queueFilter,
    PROPOSAL_QUEUE_FILTERS.map((filter) => ({ value: filter, label: filter })),
    "all",
    "(no filters)",
  );
  updateSelectOptions(
    elements.workspaceRole,
    WORKSPACE_ROLE_OPTIONS.map((role) => ({ value: role, label: role })),
    "facilitator",
    "(no roles)",
  );
  updateSelectOptions(
    elements.densityMode,
    DENSITY_MODE_OPTIONS.map((mode) => ({ value: mode, label: mode })),
    "default",
    "(no modes)",
  );
  updateSelectOptions(
    elements.presenterSelect,
    [{ value: "actor.facilitator", label: "actor.facilitator" }],
    "actor.facilitator",
    "(no actors)",
  );

  const compareWorkspace = createCompareWorkspace({
    onSetCompareBaseline: actions.onSetCompareBaseline,
    onSetCompareTarget: actions.onSetCompareTarget,
    onSetCompareMode: actions.onSetCompareMode,
    onSetCompareThreshold: actions.onSetCompareThreshold,
    onSetCompareHotspot: actions.onSetCompareHotspot,
    onRunCompare: actions.onRunCompare,
    onInspectProvenance: actions.onInspectProvenance,
    onInspectProvenanceFromCompareHotspot: actions.onInspectProvenanceFromCompareHotspot,
  });

  const replayWorkspace = createReplayWorkspace({
    onSetReplayBranch: actions.onSetReplayBranch,
    onLoadReplay: actions.onLoadReplay,
    onSetReplayCursor: (cursorIndex) => {
      pendingReplayScrubStart = performance.now();
      actions.onSetReplayCursor?.(cursorIndex);
    },
    onStepReplay: (delta) => {
      pendingReplayScrubStart = performance.now();
      actions.onStepReplay?.(delta);
    },
    onJumpReplayCheckpoint: (turnIndex) => {
      pendingReplayScrubStart = performance.now();
      actions.onJumpReplayCheckpoint?.(turnIndex);
    },
    onInspectProvenance: actions.onInspectProvenance,
    onInspectProvenanceFromReplayCheckpoint: actions.onInspectProvenanceFromReplayCheckpoint,
  });

  const provenanceDrawer = createProvenanceDrawer({
    onInspectProvenance: actions.onInspectProvenance,
    onInspectProvenanceFromContext: () => {
      const state = actions.onRequestState?.();
      const inferred = state ? inferProvenanceContext(state) : null;
      if (!inferred) {
        return;
      }
      actions.onInspectProvenance?.(inferred.artifactType, inferred.artifactId, inferred.contextLabel);
    },
  });

  const onboardingWorkspace = document.createElement("section");
  onboardingWorkspace.className = "planning-control-group onboarding-workspace";
  onboardingWorkspace.innerHTML = `
    <h3>Onboarding and Demo Flow</h3>
    <p class="muted" id="onboarding-progress">0 of 0 steps complete.</p>
    <div class="planning-button-row onboarding-route-row">
      <button type="button" id="onboarding-start">Start quickstart</button>
      <button type="button" data-onboarding-route="plan">Open plan</button>
      <button type="button" data-onboarding-route="compare">Open compare</button>
      <button type="button" data-onboarding-route="replay">Open replay</button>
      <button type="button" data-onboarding-route="facilitate">Open facilitate</button>
    </div>
    <ol id="onboarding-step-list" class="planning-inline-list onboarding-step-list"></ol>
  `;

  const onboardingElements = {
    root: onboardingWorkspace,
    progress: onboardingWorkspace.querySelector("#onboarding-progress"),
    start: onboardingWorkspace.querySelector("#onboarding-start"),
    steps: onboardingWorkspace.querySelector("#onboarding-step-list"),
    routeRow: onboardingWorkspace.querySelector(".onboarding-route-row"),
  };

  elements.routePanels.append(onboardingWorkspace, compareWorkspace.root, replayWorkspace.root, provenanceDrawer.root);

  const canvas = createDymaxionCanvas(root.querySelector("#world-canvas-root"), {
    onRegionSelect: (regionId, options) => {
      actions.onRegionSelect?.(regionId, options);
    },
    onRegionHover: (regionId) => {
      actions.onRegionHover?.(regionId);
    },
    onViewportChange: (viewport) => {
      actions.onViewportChange?.(viewport);
    },
  });
  let lastCanvasFingerprint = null;
  let pendingOverlayToggleStart = null;
  let pendingReplayScrubStart = null;
  const diagnostics = createResponsivenessDiagnostics();
  diagnostics.publish();

  elements.branchSelect.addEventListener("change", () => {
    actions.onSetActiveBranch?.(elements.branchSelect.value);
  });
  elements.focusRegion.addEventListener("click", () => {
    actions.onFocusRegion?.(elements.regionSelect.value || null);
  });
  elements.stageSelect.addEventListener("change", () => {
    actions.onSetStageDraft?.(elements.stageSelect.value);
  });
  elements.setStage.addEventListener("click", () => {
    actions.onSetSessionStage?.(elements.stageSelect.value);
  });
  elements.advanceStage.addEventListener("click", () => {
    actions.onAdvanceSessionStage?.();
  });
  elements.addActor.addEventListener("click", () => {
    actions.onAddActor?.(elements.actorId.value.trim(), elements.actorRole.value);
  });
  elements.refreshNetwork.addEventListener("click", () => {
    actions.onRefreshNetwork?.();
  });
  elements.dominantLayer.addEventListener("change", () => {
    actions.onSetDominantLayer?.(elements.dominantLayer.value);
  });
  elements.layerToggles.addEventListener("change", (event) => {
    const input = event.target.closest("input[data-layer-id]");
    if (!input) {
      return;
    }
    pendingOverlayToggleStart = performance.now();
    actions.onToggleLayer?.(input.getAttribute("data-layer-id"), input.checked);
  });
  elements.proposalTitle.addEventListener("input", () => {
    actions.onSetProposalTitle?.(elements.proposalTitle.value);
  });
  elements.proposalActor.addEventListener("input", () => {
    actions.onSetProposalActor?.(elements.proposalActor.value);
  });
  elements.proposalSelect.addEventListener("change", () => {
    actions.onSetActiveProposal?.(elements.proposalSelect.value);
  });
  elements.createProposal.addEventListener("click", () => {
    actions.onCreateProposal?.();
  });
  elements.submitProposal.addEventListener("click", () => {
    actions.onSubmitProposal?.();
  });
  elements.adoptProposal.addEventListener("click", () => {
    actions.onAdoptProposal?.();
  });
  elements.rejectProposal.addEventListener("click", () => {
    actions.onRejectProposal?.();
  });
  elements.queueFilter.addEventListener("change", () => {
    actions.onSetQueueFilter?.(elements.queueFilter.value);
  });
  elements.workspaceRole.addEventListener("change", () => {
    actions.onSetWorkspaceRole?.(elements.workspaceRole.value);
  });
  elements.densityMode.addEventListener("change", () => {
    actions.onSetDensityMode?.(elements.densityMode.value);
  });
  elements.presenterSelect.addEventListener("change", () => {
    actions.onSetPresenterActor?.(elements.presenterSelect.value);
  });
  elements.followPresenter.addEventListener("change", () => {
    actions.onSetFollowPresenter?.(elements.followPresenter.checked);
  });
  elements.proposalQueue.addEventListener("click", (event) => {
    const button = event.target.closest("[data-proposal-id][data-queue-action]");
    if (!button) {
      return;
    }
    const proposalId = button.getAttribute("data-proposal-id");
    const queueAction = button.getAttribute("data-queue-action");
    if (!proposalId || !queueAction) {
      return;
    }
    if (queueAction === "focus") {
      actions.onSetActiveProposal?.(proposalId);
      return;
    }
    if (queueAction === "submit") {
      actions.onSubmitProposal?.(proposalId);
      return;
    }
    if (queueAction === "adopt") {
      actions.onAdoptProposal?.(proposalId);
      return;
    }
    if (queueAction === "reject") {
      actions.onRejectProposal?.(proposalId);
    }
  });
  elements.interventionSelect.addEventListener("change", () => {
    actions.onSetIntervention?.(elements.interventionSelect.value);
  });
  elements.shockSelect.addEventListener("change", () => {
    actions.onSetShock?.(elements.shockSelect.value);
  });
  elements.runTurn.addEventListener("click", () => {
    actions.onRunTurn?.();
  });
  elements.createAnnotation.addEventListener("click", () => {
    actions.onCreateAnnotation?.(elements.annotationBody.value.trim());
  });
  elements.setSpotlight.addEventListener("click", () => {
    actions.onSetSpotlightFromSelection?.();
  });
  elements.clearSpotlight.addEventListener("click", () => {
    actions.onClearSpotlight?.();
  });
  elements.presentationMode.addEventListener("change", () => {
    actions.onSetPresentationMode?.(elements.presentationMode.checked);
  });
  elements.exportSession.addEventListener("click", () => {
    actions.onExportSession?.();
  });
  elements.refreshContinuity.addEventListener("click", () => {
    actions.onRefreshContinuity?.();
  });
  elements.importSession.addEventListener("click", async () => {
    const file = elements.importFile.files?.[0];
    if (!file) {
      actions.onImportSessionError?.("Choose a session bundle file before importing.");
      return;
    }
    try {
      const text = await file.text();
      const bundle = JSON.parse(text);
      actions.onImportSession?.(bundle);
    } catch (error) {
      actions.onImportSessionError?.(error?.message || "Invalid JSON bundle.");
    }
  });
  onboardingElements.start.addEventListener("click", () => {
    actions.onStartOnboarding?.();
  });
  onboardingElements.routeRow.addEventListener("click", (event) => {
    const button = event.target.closest("[data-onboarding-route]");
    if (!button) {
      return;
    }
    const route = button.getAttribute("data-onboarding-route");
    if (!route) {
      return;
    }
    actions.onNavigateRoute?.(route);
  });

  function renderQueue(state) {
    const stageActions = stageActionSet(state);
    const proposals = queueProposals(state);
    const triage = queueTriageSummary(state);
    elements.proposalQueue.innerHTML = "";
    elements.queueTriageSummary.textContent = `Review ${triage.reviewCount} · unresolved evidence ${triage.unresolvedCount} · ready ${triage.readyCount}`;

    if (!proposals.length) {
      const empty = document.createElement("li");
      empty.textContent = "No proposals for this filter.";
      elements.proposalQueue.appendChild(empty);
      return;
    }

    for (const proposal of proposals) {
      const item = document.createElement("li");
      item.className = "planning-queue-item";
      const canSubmit = proposal.status === "draft" && isStageActionAllowed(stageActions, "proposal.submit");
      const canAdopt =
        (proposal.status === "submitted" || proposal.status === "under_review" || proposal.status === "draft") &&
        isStageActionAllowed(stageActions, "proposal.adopt");
      const canReject =
        proposal.status !== "adopted" &&
        proposal.status !== "rejected" &&
        isStageActionAllowed(stageActions, "proposal.reject");
      const unresolvedEvidence = triage.unresolvedIds.has(proposal.proposal_id);
      item.innerHTML = `
        <p>
          <strong>${proposal.title || proposal.proposal_id}</strong>
          <span class="muted">[${proposal.status}]</span>
          <span class="${unresolvedEvidence ? "queue-triage-chip unresolved" : "queue-triage-chip ready"}">
            ${unresolvedEvidence ? "Evidence needed" : "Evidence ready"}
          </span>
        </p>
        <p class="muted">${proposal.author_actor_id || "unknown actor"} · ${proposal.proposal_id}</p>
        <div class="planning-button-row">
          <button type="button" data-queue-action="focus" data-proposal-id="${proposal.proposal_id}">Focus</button>
          <button type="button" data-queue-action="submit" data-proposal-id="${proposal.proposal_id}" ${canSubmit ? "" : "disabled"}>Submit</button>
          <button type="button" data-queue-action="adopt" data-proposal-id="${proposal.proposal_id}" ${canAdopt ? "" : "disabled"}>Adopt</button>
          <button type="button" data-queue-action="reject" data-proposal-id="${proposal.proposal_id}" ${canReject ? "" : "disabled"}>Reject</button>
        </div>
      `;
      elements.proposalQueue.appendChild(item);
    }
  }

  function renderActors(state) {
    const actors = state.session.sessionState?.actors || [];
    elements.actorRoster.innerHTML = "";
    if (!actors.length) {
      const empty = document.createElement("li");
      empty.textContent = "No participants yet.";
      elements.actorRoster.appendChild(empty);
      return;
    }
    for (const actor of actors) {
      const item = document.createElement("li");
      const roleLabel = (actor.roles || []).join(", ") || "observer";
      item.textContent = `${actor.display_name || actor.actor_id} (${roleLabel})`;
      elements.actorRoster.appendChild(item);
    }
  }

  function renderOnboarding(state) {
    const steps = onboardingChecklist(state);
    const completed = steps.filter((step) => step.complete).length;
    onboardingElements.progress.textContent = `${completed} of ${steps.length} steps complete.`;
    onboardingElements.steps.innerHTML = "";
    for (const step of steps) {
      const item = document.createElement("li");
      item.className = "onboarding-step-item";
      item.textContent = `${step.complete ? "Done" : "Next"}: ${step.label}`;
      onboardingElements.steps.appendChild(item);
    }
    onboardingElements.root.classList.toggle("is-active", state.route === "onboard");
  }

  function renderContinuity(state) {
    const events = continuityEvents(state);
    elements.continuityEvents.innerHTML = "";
    if (!events.length) {
      const empty = document.createElement("li");
      empty.textContent = "No timeline events yet. Refresh room state after session actions.";
      elements.continuityEvents.appendChild(empty);
      return;
    }

    for (const event of events) {
      const item = document.createElement("li");
      item.textContent = `${event.timestamp || "unknown time"} · ${event.event_type || "event"}`;
      elements.continuityEvents.appendChild(item);
    }
  }

  function render(state, geometryPackage) {
    updateSelectOptions(elements.branchSelect, branchOptions(state), state.branch.activeBranchId, "(no branches)");
    updateSelectOptions(
      elements.regionSelect,
      regionOptions(geometryPackage),
      state.selection.regionId,
      "(select region)",
    );
    updateSelectOptions(
      elements.proposalSelect,
      proposalOptions(state),
      state.planning.activeProposalId,
      "(no proposals)",
    );
    updateSelectOptions(
      elements.interventionSelect,
      interventionOptions(state),
      state.planning.activeInterventionId,
      "(no interventions)",
    );
    updateSelectOptions(elements.shockSelect, shockOptions(state), state.planning.activeShockId, "(none)");
    updateSelectOptions(
      elements.queueFilter,
      PROPOSAL_QUEUE_FILTERS.map((filter) => ({ value: filter, label: filter })),
      state.facilitation.queueFilter || "all",
      "(no filters)",
    );
    updateSelectOptions(
      elements.presenterSelect,
      (state.session.sessionState?.actors || []).map((actor) => ({
        value: actor.actor_id,
        label: `${actor.display_name || actor.actor_id} (${(actor.roles || []).join(", ") || "observer"})`,
      })),
      state.facilitation.presenterActorId || state.planning.proposalActorId || "actor.facilitator",
      "(no actors)",
    );

    if (document.activeElement !== elements.proposalTitle) {
      elements.proposalTitle.value = state.planning.proposalTitle || "";
    }
    if (document.activeElement !== elements.proposalActor) {
      elements.proposalActor.value = state.planning.proposalActorId || "";
    }

    const stage = state.session.sessionState?.facilitation_state?.stage || "setup";
    elements.stage.textContent = `Stage: ${stage}`;
    elements.stageSelect.value = stage;
    elements.focusRegion.disabled = !elements.regionSelect.value;

    for (const input of elements.layerToggles.querySelectorAll("input[data-layer-id]")) {
      const layerId = input.getAttribute("data-layer-id");
      input.checked = state.layers.visibleLayerIds.includes(layerId);
    }
    elements.dominantLayer.value = state.layers.dominantLayerId || "state.water_security";

    const scope = state.selection.proposalRegionIds?.length
      ? state.selection.proposalRegionIds.join(", ")
      : state.selection.regionId || "none";
    elements.selectionSummary.textContent = `Selection scope: ${scope}`;
    elements.resultSummary.textContent = JSON.stringify(snapshotPayload(state), null, 2);

    const planningRouteActive = routeAllowsPlanningLoop(state.route);
    const visibility = routeGroupVisibility(state.route);
    const workspaceRole = state.experience?.workspaceRole || "facilitator";
    const roleEmphasis = ROLE_EMPHASIS[workspaceRole] || ROLE_EMPHASIS.facilitator;
    const capabilities = roleCapabilitySet(workspaceRole);
    const densityMode = state.experience?.densityMode || "default";

    root.setAttribute("data-route", state.route || "plan");
    root.setAttribute("data-density-mode", densityMode);
    root.setAttribute("data-workspace-role", workspaceRole);

    elements.branchGroup.hidden = !visibility.showBranch;
    elements.facilitationGroup.hidden = !visibility.showFacilitation;
    elements.participantsGroup.hidden = !visibility.showParticipants;
    elements.layersGroup.hidden = !visibility.showLayers;
    elements.proposalGroup.hidden = !planningRouteActive || !visibility.showProposal;
    elements.queueGroup.hidden = !planningRouteActive || !visibility.showQueue;
    elements.turnGroup.hidden = !planningRouteActive || !visibility.showTurn;
    elements.annotationGroup.hidden = !planningRouteActive || !visibility.showAnnotation;
    elements.spotlightGroup.hidden = !visibility.showSpotlight;
    elements.persistenceGroup.hidden = !visibility.showPersistence;
    elements.snapshotGroup.hidden = !visibility.showSnapshot;

    const stageActions = stageActionSet(state);
    elements.createProposal.disabled = !capabilities.canCreateProposal || !isStageActionAllowed(stageActions, "proposal.create");
    elements.submitProposal.disabled = !capabilities.canSubmitProposal || !isStageActionAllowed(stageActions, "proposal.submit");
    elements.adoptProposal.disabled = !capabilities.canAdoptProposal || !isStageActionAllowed(stageActions, "proposal.adopt");
    elements.rejectProposal.disabled = !capabilities.canRejectProposal || !isStageActionAllowed(stageActions, "proposal.reject");
    elements.runTurn.disabled = !capabilities.canRunTurn || !isStageActionAllowed(stageActions, "turn.run");
    elements.createAnnotation.disabled = !capabilities.canAnnotate || !isStageActionAllowed(stageActions, "annotation.create");
    elements.setStage.disabled = !capabilities.canStageManage;
    elements.advanceStage.disabled = !capabilities.canStageManage;
    elements.addActor.disabled = !capabilities.canManageParticipants;
    elements.queueFilter.disabled = !capabilities.canModerateQueue;
    elements.setSpotlight.disabled = !capabilities.canSpotlight;
    elements.clearSpotlight.disabled = !capabilities.canSpotlight;
    elements.exportSession.disabled = !capabilities.canPersist;
    elements.importSession.disabled = !capabilities.canPersist;
    elements.importFile.disabled = !capabilities.canPersist;
    elements.refreshContinuity.disabled = !state.session.sessionId;
    elements.presenterSelect.disabled = !capabilities.canSpotlight;
    elements.followPresenter.disabled = !state.session.sessionId;

    renderActors(state);
    renderQueue(state);
    renderOnboarding(state);
    renderContinuity(state);

    elements.mapHudRoute.textContent = `Mode: ${state.route}`;
    elements.mapHudBranch.textContent = `Branch: ${state.branch.activeBranchId || "none"}`;
    elements.mapHudSelection.textContent = `Selection: ${scope}`;
    elements.mapHudExperience.textContent = `Preset: ${workspaceRole} · Density: ${densityMode}`;
    elements.mapHudAttention.textContent = `Attention: ${state.facilitation.sharedAttentionStatus || "local-only"} · ${state.facilitation.presenterActorId || "none"}`;
    elements.workspaceRole.value = workspaceRole;
    elements.densityMode.value = densityMode;
    elements.roleEmphasisSummary.textContent = roleEmphasis.summary;

    elements.spotlightSummary.textContent = state.facilitation.spotlightRegionId
      ? `Spotlighting ${state.facilitation.spotlightRegionId}`
      : "No spotlight region selected.";
    elements.followPresenter.checked = Boolean(state.facilitation.followPresenter);
    elements.attentionSyncSummary.textContent = `Shared attention sync: ${state.facilitation.sharedAttentionStatus || "local-only"} in this runtime.`;
    elements.presentationMode.checked = Boolean(state.facilitation.presentationMode);
    elements.persistenceSummary.textContent = state.facilitation.persistenceSummary || "No persistence actions yet.";

    onboardingWorkspace.hidden = state.route !== "onboard";
    compareWorkspace.root.hidden = state.route !== "compare";
    replayWorkspace.root.hidden = state.route !== "replay";
    provenanceDrawer.root.hidden = !(state.route === "compare" || state.route === "replay" || state.route === "facilitate");

    compareWorkspace.render(state);
    replayWorkspace.render(state);
    provenanceDrawer.render(state);

    if (geometryPackage) {
      const canvasModel = deriveCanvasModel(state, geometryPackage);
      const fingerprint = canvasRenderFingerprint(canvasModel);
      if (fingerprint !== lastCanvasFingerprint) {
        const drawStartedAt = performance.now();
        canvas.render(canvasModel);
        diagnostics.record("map_redraw", performance.now() - drawStartedAt);
        lastCanvasFingerprint = fingerprint;
      }
    }

    const renderCompletedAt = performance.now();
    if (pendingOverlayToggleStart !== null) {
      diagnostics.record("overlay_toggle", renderCompletedAt - pendingOverlayToggleStart);
      pendingOverlayToggleStart = null;
    }
    if (pendingReplayScrubStart !== null) {
      diagnostics.record("replay_scrub", renderCompletedAt - pendingReplayScrubStart);
      pendingReplayScrubStart = null;
    }
    const diagnosticsSnapshot = diagnostics.snapshot();
    elements.performanceSummary.textContent = JSON.stringify(diagnosticsSnapshot, null, 2);
    diagnostics.publish();
  }

  return {
    root,
    render,
  };
}

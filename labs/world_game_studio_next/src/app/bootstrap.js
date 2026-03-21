import { createHashRouter } from "./router.js";
import { renderStudioShell } from "./render.js";
import { createStudioShell } from "./shell.js";
import { createRuntimeClient } from "../services/runtimeClient.js";
import { createStudioServices } from "../services/index.js";
import { createStudioStore } from "../state/store.js";
import { loadGeometryPackage } from "../world_canvas/geometryLoader.js";
import {
  DOMINANT_REGION_LAYER_OPTIONS,
  WORLD_CANVAS_LAYER_DEFINITIONS,
} from "../world_canvas/mapAdapters.js";
import { createPlanningWorkspace } from "../world_canvas/planningWorkspace.js";

const STAGE_ORDER = ["setup", "proposal_intake", "deliberation", "selection", "simulation", "review", "closed"];
const DEFAULT_ACTOR_ID = "actor.facilitator";
const KEYBOARD_ROUTE_SHORTCUTS = ["onboard", "plan", "simulate", "compare", "replay", "facilitate"];
const WORKSPACE_ROLE_OPTIONS = new Set(["facilitator", "analyst", "delegate", "observer"]);
const DENSITY_MODE_OPTIONS = new Set(["default", "analysis", "presentation"]);
const ROLE_PRESET_CONFIG = {
  facilitator: { queueFilter: "submitted", followPresenter: false },
  analyst: { queueFilter: "under_review", followPresenter: false },
  delegate: { queueFilter: "draft", followPresenter: false },
  observer: { queueFilter: "submitted", followPresenter: true },
};

function normalizeScenarioList(payload) {
  if (!payload || !Array.isArray(payload.scenarios)) {
    return [];
  }
  return payload.scenarios;
}

function pickScenarioId(shell, currentState) {
  const selected = shell.scenarioSelect.value;
  if (selected) {
    return selected;
  }
  return currentState.scenario.activeScenarioId;
}

function slugProposalBranchId(proposalId) {
  return `${proposalId.replaceAll(".", "-")}.branch`;
}

function uniqueBranchIds(ids) {
  return Array.from(new Set((ids || []).filter((id) => Boolean(id))));
}

function isEditableTarget(target) {
  if (!target) {
    return false;
  }
  const tag = String(target.tagName || "").toLowerCase();
  return tag === "input" || tag === "select" || tag === "textarea" || Boolean(target.isContentEditable);
}

function triggerJsonDownload(filename, payload) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(objectUrl);
}

export function bootstrapStudioApp(root) {
  const store = createStudioStore();
  const runtimeClient = createRuntimeClient();
  const services = createStudioServices(runtimeClient);
  const shell = createStudioShell(root);
  let geometryPackage = null;

  function render() {
    renderStudioShell(shell, store.getState(), {
      planningWorkspace,
      geometryPackage,
    });
  }

  function beginRuntime(method) {
    store.beginRequest(method);
    render();
  }

  function completeRuntime() {
    store.endRequest();
    render();
  }

  function failRuntime(error) {
    store.failRequest(error);
    store.addNotification("error", error?.message || String(error));
    render();
  }

  async function runRuntime(method, operation, onSuccessMessage) {
    beginRuntime(method);
    try {
      const result = await operation();
      if (onSuccessMessage) {
        store.addNotification("info", onSuccessMessage);
      }
      return result;
    } catch (error) {
      failRuntime(error);
      throw error;
    } finally {
      completeRuntime();
    }
  }

  function preferredActorId() {
    const actor = store.getState().planning.proposalActorId?.trim();
    return actor || DEFAULT_ACTOR_ID;
  }

  function setReducedMotion(enabled) {
    store.patchDomain("accessibility", {
      reducedMotion: Boolean(enabled),
    });
    render();
  }

  function patchSessionState(sessionStatePatch) {
    const current = store.getState().session.sessionState || {};
    store.patchDomain("session", {
      sessionState: {
        ...current,
        ...sessionStatePatch,
      },
    });
  }

  async function ensureSession() {
    const state = store.getState();
    if (state.session.sessionId) {
      return state.session.sessionId;
    }

    const created = await runRuntime(
      "world_game.session.create",
      () => services.session.create("WG Studio Next Session", preferredActorId(), ["facilitator"]),
      "Session created",
    );

    const sessionId = created.session_id || created.session?.session_meta?.session_id || null;
    store.patchDomain("session", {
      sessionId,
      sessionState: created.session || created,
    });
    render();
    return sessionId;
  }

  async function refreshSession(options = {}) {
    const { notify = true } = options;
    const sessionId = await ensureSession();
    const result = await runRuntime(
      "world_game.session.get",
      () => services.session.get(sessionId),
      notify ? "Session refreshed" : null,
    );
    store.patchDomain("session", {
      sessionState: result.session || result,
    });
    render();
    return result;
  }

  async function refreshContinuity() {
    const result = await refreshSession({ notify: true });
    await refreshProposals();
    await refreshAnnotations();
    const activeBranchId = store.getState().branch.activeBranchId;
    if (activeBranchId) {
      await refreshNetworkSnapshot(activeBranchId);
    }
    store.patchDomain("facilitation", {
      persistenceSummary: `Room state refreshed at ${new Date().toISOString()}.`,
    });
    render();
    return result;
  }

  function currentStage() {
    return store.getState().session.sessionState?.facilitation_state?.stage || "setup";
  }

  function currentAllowedActions() {
    const facilitationState = store.getState().session.sessionState?.facilitation_state || {};
    const stage = facilitationState.stage || "setup";
    return new Set(facilitationState.allowed_actions?.[stage] || []);
  }

  async function ensureActionAllowed(action, fallbackStage) {
    await refreshSession({ notify: false });
    const allowed = currentAllowedActions();
    if (!allowed.size || allowed.has(action)) {
      return true;
    }
    store.addNotification(
      "warn",
      `Action ${action} is not available during stage ${currentStage()}. Set stage to ${fallbackStage} first.`,
    );
    render();
    return false;
  }

  async function setSessionStage(stage) {
    const normalizedStage = STAGE_ORDER.includes(stage) ? stage : null;
    if (!normalizedStage) {
      store.addNotification("warn", `Unknown stage: ${stage}`);
      render();
      return;
    }
    const sessionId = await ensureSession();
    const result = await runRuntime(
      "world_game.session.stage.set",
      () => services.session.setStage(sessionId, normalizedStage, preferredActorId()),
      `Stage set to ${normalizedStage}`,
    );
    patchSessionState({
      facilitation_state: result.facilitation_state,
    });
    render();
  }

  async function advanceSessionStage() {
    const sessionId = await ensureSession();
    const result = await runRuntime(
      "world_game.session.stage.advance",
      () => services.session.advanceStage(sessionId, preferredActorId()),
      "Stage advanced",
    );
    patchSessionState({
      facilitation_state: result.facilitation_state,
    });
    render();
  }

  async function addActor(actorId, role) {
    if (!actorId) {
      store.addNotification("warn", "Enter an actor id before adding a participant.");
      render();
      return;
    }
    const sessionId = await ensureSession();
    const normalizedRole = role || "observer";
    const result = await runRuntime(
      "world_game.session.actor.add",
      () => services.session.addActor(sessionId, actorId, [normalizedRole], preferredActorId(), actorId),
      `Added actor ${actorId} (${normalizedRole})`,
    );
    patchSessionState({
      actors: result.actors || [],
    });
    render();
  }

  async function refreshScenarios() {
    const result = await runRuntime(
      "world_game.scenario.list",
      () => services.scenario.list(),
      "Scenarios refreshed",
    );
    const scenarios = normalizeScenarioList(result);
    const activeScenarioId = scenarios[0]?.scenario_id || null;
    store.patchDomain("scenario", {
      list: scenarios,
      activeScenarioId,
    });
    render();
  }

  async function refreshProposals() {
    const state = store.getState();
    if (!state.scenario.loadedScenario) {
      return;
    }
    const sessionId = await ensureSession();
    const result = await runRuntime("world_game.proposal.list", () => services.proposal.list(sessionId));
    const proposals = result.proposals || [];
    const activeProposalId = proposals.some((proposal) => proposal.proposal_id === state.planning.activeProposalId)
      ? state.planning.activeProposalId
      : proposals[0]?.proposal_id || null;
    store.patchDomain("planning", {
      proposals,
      activeProposalId,
    });
    store.patchDomain("selection", {
      proposalId: activeProposalId,
    });
    render();
  }

  async function refreshAnnotations() {
    const state = store.getState();
    if (!state.scenario.loadedScenario) {
      return;
    }
    const sessionId = await ensureSession();
    const result = await runRuntime("world_game.annotation.list", () => services.annotation.list(sessionId));
    store.patchDomain("planning", {
      annotations: result.annotations || [],
    });
    render();
  }

  async function refreshNetworkSnapshot(branchId = null) {
    const state = store.getState();
    if (!state.scenario.loadedScenario) {
      return;
    }
    const sessionId = await ensureSession();
    const focusedBranchId = branchId || state.branch.activeBranchId;
    if (!focusedBranchId) {
      return;
    }
    const result = await runRuntime(
      "world_game.network.inspect",
      () => services.simulation.inspectNetwork(sessionId, focusedBranchId),
      "Network snapshot refreshed",
    );
    store.patchDomain("planning", {
      networkSnapshot: result,
    });
    render();
  }

  function focusRegion(regionId) {
    if (!regionId) {
      store.addNotification("warn", "Choose a region from the navigator first.");
      render();
      return;
    }
    setProposalScope(regionId, { append: false });
  }

  function setCompareBaseline(branchId) {
    const state = store.getState();
    const nextBaseline = branchId || state.compare.baselineBranchId || state.branch.activeBranchId || null;
    let nextTargets = uniqueBranchIds(state.compare.targetBranchIds).filter((id) => id !== nextBaseline);
    if (!nextTargets.length) {
      const fallbackTarget = Object.keys(state.branch.branches || {}).find((id) => id !== nextBaseline);
      nextTargets = fallbackTarget ? [fallbackTarget] : [];
    }
    store.patchDomain("compare", {
      baselineBranchId: nextBaseline,
      targetBranchIds: nextTargets,
      selectedHotspotRegionId: null,
      result: null,
      error: null,
    });
    render();
  }

  function setCompareTarget(branchId) {
    const state = store.getState();
    const baselineBranchId = state.compare.baselineBranchId || state.branch.activeBranchId || null;
    const nextTarget = branchId && branchId !== baselineBranchId ? branchId : null;
    store.patchDomain("compare", {
      targetBranchIds: nextTarget ? [nextTarget] : [],
      selectedHotspotRegionId: null,
      result: null,
      error: null,
    });
    render();
  }

  function setCompareMode(mode) {
    const normalized = mode === "split" || mode === "ghost" ? mode : "delta";
    store.patchDomain("compare", {
      visualizationMode: normalized,
    });
    render();
  }

  function setCompareThreshold(value) {
    const numeric = Number(value);
    const hotspotThreshold = Number.isFinite(numeric) ? Math.max(0, Number(numeric.toFixed(4))) : 0.25;
    store.patchDomain("compare", {
      hotspotThreshold,
      selectedHotspotRegionId: null,
    });
    render();
  }

  function setCompareHotspot(regionId) {
    const normalizedRegionId = regionId || null;
    store.patchDomain("compare", {
      selectedHotspotRegionId: normalizedRegionId,
    });
    if (normalizedRegionId) {
      store.patchDomain("selection", {
        regionId: normalizedRegionId,
      });
    }
    render();
  }

  function maybeSeedCompareTarget(candidateBranchId) {
    const state = store.getState();
    if (!candidateBranchId) {
      return;
    }
    if (!state.compare.baselineBranchId || state.compare.targetBranchIds.length) {
      return;
    }
    if (candidateBranchId === state.compare.baselineBranchId) {
      return;
    }
    store.patchDomain("compare", {
      targetBranchIds: [candidateBranchId],
    });
  }

  async function runCompare() {
    const state = store.getState();
    if (!state.scenario.loadedScenario) {
      store.addNotification("warn", "Load a scenario before running compare.");
      render();
      return;
    }
    const baselineBranchId = state.compare.baselineBranchId || state.branch.activeBranchId;
    const targetBranchId =
      state.compare.targetBranchIds?.[0] ||
      Object.keys(state.branch.branches || {}).find((id) => id !== baselineBranchId) ||
      null;
    const branchIds = uniqueBranchIds([baselineBranchId, targetBranchId]);
    if (branchIds.length < 2) {
      store.addNotification("warn", "Select baseline and target branches before compare.");
      render();
      return;
    }

    const sessionId = await ensureSession();
    store.patchDomain("compare", {
      loading: true,
      error: null,
    });
    render();

    try {
      const result = await runRuntime(
        "world_game.branch.compare",
        () => services.branch.compare(sessionId, branchIds, true),
        `Compared ${branchIds.join(" vs ")}`,
      );
      const equity = await runRuntime(
        "world_game.equity.report",
        () => services.simulation.equityReport(sessionId, null, branchIds),
      );
      store.patchDomain("compare", {
        baselineBranchId,
        targetBranchIds: [targetBranchId],
        result: {
          ...result,
          equity_reports: equity.reports || (equity.equity_report ? [{ branch_id: equity.branch_id, equity_report: equity.equity_report }] : []),
        },
        selectedHotspotRegionId: null,
        loading: false,
        error: null,
      });
    } catch (error) {
      store.patchDomain("compare", {
        loading: false,
        error: error?.message || String(error),
      });
      throw error;
    } finally {
      render();
    }
  }

  function setReplayBranch(branchId) {
    store.patchDomain("replay", {
      branchId: branchId || null,
      selectedCheckpointTurn: null,
    });
    render();
  }

  function setReplayCursor(cursorIndex) {
    const frames = store.getState().replay.frames || [];
    const maxIndex = Math.max(0, frames.length - 1);
    const nextIndex = Math.max(0, Math.min(maxIndex, Number(cursorIndex || 0)));
    store.patchDomain("replay", {
      cursorIndex: nextIndex,
      selectedCheckpointTurn: frames[nextIndex]?.turn_index ?? null,
    });
    render();
  }

  function stepReplay(offset) {
    const current = Number(store.getState().replay.cursorIndex || 0);
    setReplayCursor(current + Number(offset || 0));
  }

  function jumpReplayCheckpoint(turnIndex) {
    const frames = store.getState().replay.frames || [];
    if (!frames.length) {
      return;
    }
    const targetTurn = Number(turnIndex);
    const frameIndex = frames.findIndex((frame) => Number(frame.turn_index) === targetTurn);
    if (frameIndex >= 0) {
      setReplayCursor(frameIndex);
      return;
    }
    setReplayCursor(targetTurn);
  }

  async function loadReplay(branchId = null) {
    const state = store.getState();
    if (!state.scenario.loadedScenario) {
      store.addNotification("warn", "Load a scenario before replay.");
      render();
      return;
    }
    const selectedBranchId = branchId || state.replay.branchId || state.branch.activeBranchId;
    if (!selectedBranchId) {
      store.addNotification("warn", "Select a branch before replay.");
      render();
      return;
    }

    const sessionId = await ensureSession();
    store.patchDomain("replay", {
      loading: true,
      error: null,
    });
    render();
    try {
      const result = await runRuntime(
        "world_game.replay.run",
        () => services.replay.run(sessionId, selectedBranchId),
        `Replay loaded for ${selectedBranchId}`,
      );
      const frames = Array.isArray(result.replay_frames) ? result.replay_frames : [];
      store.patchDomain("replay", {
        branchId: selectedBranchId,
        result,
        frames,
        cursorIndex: Math.max(0, frames.length - 1),
        selectedCheckpointTurn: frames[Math.max(0, frames.length - 1)]?.turn_index ?? null,
        loading: false,
        error: null,
      });
    } catch (error) {
      store.patchDomain("replay", {
        loading: false,
        error: error?.message || String(error),
      });
      throw error;
    } finally {
      render();
    }
  }

  async function inspectProvenance(artifactType, artifactId, contextLabel = null) {
    if (!artifactType || !artifactId) {
      store.addNotification("warn", "Select artifact type and id before provenance inspect.");
      render();
      return;
    }
    const sessionId = await ensureSession();
    store.patchDomain("provenance", {
      artifactType,
      artifactId,
      contextLabel: contextLabel || null,
      loading: true,
      error: null,
    });
    render();
    try {
      const result = await runRuntime(
        "world_game.provenance.inspect",
        () => services.provenance.inspect(sessionId, artifactType, artifactId),
        `Provenance loaded for ${artifactType}:${artifactId}`,
      );
      store.patchDomain("provenance", {
        artifactType,
        artifactId,
        contextLabel: contextLabel || null,
        result,
        loading: false,
        error: null,
      });
    } catch (error) {
      store.patchDomain("provenance", {
        loading: false,
        error: error?.message || String(error),
      });
      throw error;
    } finally {
      render();
    }
  }

  async function loadScenario() {
    const sessionId = await ensureSession();
    const state = store.getState();
    const scenarioId = pickScenarioId(shell, state);
    if (!scenarioId) {
      store.addNotification("warn", "Select a scenario first");
      render();
      return;
    }

    const loaded = await runRuntime(
      "world_game.scenario.load",
      () => services.scenario.load(sessionId, scenarioId),
      `Scenario loaded: ${scenarioId}`,
    );

    const branch = loaded.branch || null;
    const branches = branch ? { [branch.branch_id]: branch } : {};
    store.patchDomain("scenario", {
      activeScenarioId: loaded.scenario_id,
      loadedScenario: loaded,
      error: null,
    });
    store.patchDomain("branch", {
      activeBranchId: branch?.branch_id || null,
      branches,
      compareBranchIds: [],
      error: null,
    });
    store.patchDomain("selection", {
      regionId: null,
      hoverRegionId: null,
      proposalRegionIds: [],
      proposalId: null,
      annotationId: null,
    });
    store.patchDomain("planning", {
      activeInterventionId: loaded.intervention_ids?.[0] || null,
      activeShockId: null,
      activeProposalId: null,
      proposals: [],
      lastTurnResult: null,
      networkSnapshot: null,
      annotations: [],
    });
    store.patchDomain("compare", {
      baselineBranchId: branch?.branch_id || null,
      targetBranchIds: [],
      visualizationMode: "delta",
      selectedHotspotRegionId: null,
      result: null,
      loading: false,
      error: null,
    });
    store.patchDomain("replay", {
      branchId: branch?.branch_id || null,
      cursorIndex: 0,
      selectedCheckpointTurn: null,
      result: null,
      frames: [],
      loading: false,
      error: null,
    });
    store.patchDomain("provenance", {
      artifactType: branch?.branch_id ? "branch" : null,
      artifactId: branch?.branch_id || null,
      contextLabel: branch?.branch_id ? "active branch" : null,
      result: null,
      loading: false,
      error: null,
    });
    store.patchDomain("facilitation", {
      queueFilter: "all",
      spotlightRegionId: null,
      presentationMode: false,
      persistenceSummary: null,
      presenterActorId: preferredActorId(),
      followPresenter: false,
      sharedAttentionStatus: "local-only",
    });
    render();

    await refreshProposals();
    await refreshNetworkSnapshot(branch?.branch_id || null);
    await refreshAnnotations();
  }

  async function createProposal() {
    const state = store.getState();
    if (!state.scenario.loadedScenario) {
      store.addNotification("warn", "Load a scenario before creating proposals.");
      render();
      return;
    }

    const scope = state.selection.proposalRegionIds.length
      ? state.selection.proposalRegionIds
      : state.selection.regionId
        ? [state.selection.regionId]
        : [];
    const title = state.planning.proposalTitle.trim();
    if (!title) {
      store.addNotification("warn", "Enter a proposal title before creating.");
      render();
      return;
    }
    if (!scope.length) {
      store.addNotification("warn", "Select at least one region on the canvas before creating a proposal.");
      render();
      return;
    }
    if (!(await ensureActionAllowed("proposal.create", "proposal_intake"))) {
      return;
    }
    const sessionId = await ensureSession();
    const payload = {
      title,
      rationale: `Target regions: ${scope.join(", ")}`,
      intended_interventions: state.planning.activeInterventionId ? [state.planning.activeInterventionId] : [],
      expected_outcomes: [`Improve outcomes in ${scope.join(", ")}`],
      actor_id: preferredActorId(),
    };
    const result = await runRuntime(
      "world_game.proposal.create",
      () => services.proposal.create(sessionId, payload),
      "Proposal created",
    );
    store.patchDomain("planning", {
      activeProposalId: result.proposal?.proposal_id || null,
    });
    store.patchDomain("selection", {
      proposalId: result.proposal?.proposal_id || null,
    });
    await refreshProposals();
    render();
  }

  async function submitActiveProposal(proposalIdOverride = null) {
    const state = store.getState();
    const proposalId = proposalIdOverride || state.planning.activeProposalId;
    if (!proposalId) {
      store.addNotification("warn", "Select a proposal before submitting.");
      render();
      return;
    }
    if (!(await ensureActionAllowed("proposal.submit", "proposal_intake"))) {
      return;
    }
    const sessionId = await ensureSession();
    await runRuntime(
      "world_game.proposal.submit",
      () => services.proposal.submit(sessionId, proposalId, preferredActorId()),
      `Proposal submitted: ${proposalId}`,
    );
    store.patchDomain("planning", {
      activeProposalId: proposalId,
    });
    store.patchDomain("selection", {
      proposalId,
    });
    await refreshProposals();
  }

  async function adoptActiveProposal(proposalIdOverride = null) {
    const state = store.getState();
    const proposalId = proposalIdOverride || state.planning.activeProposalId;
    if (!proposalId) {
      store.addNotification("warn", "Select a proposal before adopting.");
      render();
      return;
    }
    if (!(await ensureActionAllowed("proposal.adopt", "selection"))) {
      return;
    }
    const sessionId = await ensureSession();
    const branchId = slugProposalBranchId(proposalId);
    const result = await runRuntime(
      "world_game.proposal.adopt",
      () =>
        services.proposal.adopt(
          sessionId,
          proposalId,
          preferredActorId(),
          branchId,
          state.branch.activeBranchId || "baseline",
        ),
      `Proposal adopted into ${branchId}`,
    );

    const nextBranches = {
      ...store.getState().branch.branches,
      [result.branch.branch_id]: result.branch,
    };
    store.patchDomain("branch", {
      branches: nextBranches,
      activeBranchId: result.branch.branch_id,
    });
    maybeSeedCompareTarget(result.branch.branch_id);
    store.patchDomain("selection", {
      proposalId,
    });
    await refreshProposals();
    await refreshNetworkSnapshot(result.branch.branch_id);
    await refreshAnnotations();
    render();
  }

  async function rejectActiveProposal(proposalIdOverride = null) {
    const state = store.getState();
    const proposalId = proposalIdOverride || state.planning.activeProposalId;
    if (!proposalId) {
      store.addNotification("warn", "Select a proposal before rejecting.");
      render();
      return;
    }
    if (!(await ensureActionAllowed("proposal.reject", "deliberation"))) {
      return;
    }
    const sessionId = await ensureSession();
    await runRuntime(
      "world_game.proposal.reject",
      () => services.proposal.reject(sessionId, proposalId, preferredActorId(), "Rejected in WG-P5 facilitation queue"),
      `Proposal rejected: ${proposalId}`,
    );
    store.patchDomain("planning", {
      activeProposalId: proposalId,
    });
    store.patchDomain("selection", {
      proposalId,
    });
    await refreshProposals();
    render();
  }

  async function runTurn() {
    const state = store.getState();
    if (!state.branch.activeBranchId) {
      store.addNotification("warn", "Select an active branch before running a turn.");
      render();
      return;
    }
    if (!state.planning.activeInterventionId) {
      store.addNotification("warn", "Select an intervention before running a turn.");
      render();
      return;
    }
    if (!(await ensureActionAllowed("turn.run", "simulation"))) {
      return;
    }
    const sessionId = await ensureSession();
    const result = await runRuntime(
      "world_game.turn.run",
      () =>
        services.simulation.runTurn(
          sessionId,
          state.branch.activeBranchId,
          [state.planning.activeInterventionId],
          state.planning.activeShockId ? [state.planning.activeShockId] : [],
          "approved",
          preferredActorId(),
          state.planning.activeProposalId,
        ),
      `Turn executed on ${state.branch.activeBranchId}`,
    );

    const nextBranches = {
      ...store.getState().branch.branches,
      [result.branch.branch_id]: result.branch,
    };
    store.patchDomain("branch", {
      branches: nextBranches,
      activeBranchId: result.branch.branch_id,
    });
    maybeSeedCompareTarget(result.branch.branch_id);
    store.patchDomain("replay", {
      branchId: store.getState().replay.branchId || result.branch.branch_id,
    });
    store.patchDomain("planning", {
      lastTurnResult: result,
    });
    await refreshNetworkSnapshot(result.branch.branch_id);
    await refreshAnnotations();
    render();
  }

  async function createAnnotation(body) {
    if (!body) {
      store.addNotification("warn", "Enter annotation text before adding an annotation.");
      render();
      return;
    }
    const state = store.getState();
    if (!state.scenario.loadedScenario) {
      store.addNotification("warn", "Load a scenario before creating annotations.");
      render();
      return;
    }
    if (!(await ensureActionAllowed("annotation.create", "proposal_intake"))) {
      return;
    }
    const sessionId = await ensureSession();
    const targetType = state.selection.regionId ? "region" : "branch";
    const targetId = state.selection.regionId || state.branch.activeBranchId;
    if (!targetId) {
      store.addNotification("warn", "Select a region or branch before creating annotations.");
      render();
      return;
    }

    await runRuntime(
      "world_game.annotation.create",
      () => services.annotation.create(sessionId, "note", targetType, targetId, body, preferredActorId()),
      `Annotation added to ${targetType} ${targetId}`,
    );
    await refreshAnnotations();
  }

  async function exportSessionBundle() {
    const sessionId = await ensureSession();
    const result = await runRuntime(
      "world_game.session.export",
      () => services.session.exportSession(sessionId, null, preferredActorId()),
      "Session bundle exported",
    );
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    triggerJsonDownload(`world-game-session-${sessionId}-${timestamp}.json`, result.bundle);
    store.patchDomain("facilitation", {
      persistenceSummary: `Exported ${result.summary?.proposal_count ?? 0} proposals and ${result.summary?.annotation_count ?? 0} annotations.`,
    });
    render();
  }

  function applyImportedSessionResult(result) {
    const importedSession = result.session || null;
    const importedScenario = result.scenario || null;
    const importedBranches = result.branches || {};
    const importedProposals = result.proposals || [];
    const importedAnnotations = result.annotations || [];
    const branchIds = Object.keys(importedBranches);
    const activeBranchId = branchIds[0] || null;

    store.patchDomain("session", {
      sessionState: importedSession,
    });
    store.patchDomain("scenario", {
      activeScenarioId: importedScenario?.scenario_id || null,
      loadedScenario: importedScenario
        ? {
            scenario_id: importedScenario.scenario_id,
            label: importedScenario.label,
            description: importedScenario.description,
            intervention_ids: importedScenario.intervention_ids || [],
            shock_ids: importedScenario.shock_ids || [],
          }
        : null,
      error: null,
    });
    store.patchDomain("branch", {
      activeBranchId,
      branches: importedBranches,
      compareBranchIds: [],
      error: null,
    });
    store.patchDomain("planning", {
      activeInterventionId: importedScenario?.intervention_ids?.[0] || null,
      activeShockId: null,
      activeProposalId: importedProposals[0]?.proposal_id || null,
      proposals: importedProposals,
      annotations: importedAnnotations,
    });
    store.patchDomain("selection", {
      proposalId: importedProposals[0]?.proposal_id || null,
    });
    store.patchDomain("compare", {
      baselineBranchId: activeBranchId,
      targetBranchIds: [],
      visualizationMode: "delta",
      selectedHotspotRegionId: null,
      result: null,
      loading: false,
      error: null,
    });
    store.patchDomain("replay", {
      branchId: activeBranchId,
      cursorIndex: 0,
      selectedCheckpointTurn: null,
      result: null,
      frames: [],
      loading: false,
      error: null,
    });
    store.patchDomain("provenance", {
      artifactType: activeBranchId ? "branch" : null,
      artifactId: activeBranchId,
      contextLabel: activeBranchId ? "active branch" : null,
      result: null,
      loading: false,
      error: null,
    });
    store.patchDomain("facilitation", {
      queueFilter: "all",
      spotlightRegionId: null,
      presentationMode: false,
      persistenceSummary: `Imported bundle with ${result.summary?.actor_count ?? 0} actor(s), ${result.summary?.proposal_count ?? 0} proposal(s), and ${result.summary?.branch_count ?? 0} branch(es).`,
      presenterActorId: preferredActorId(),
      followPresenter: false,
      sharedAttentionStatus: "local-only",
    });
    render();
  }

  async function importSessionBundle(bundle) {
    const sessionId = await ensureSession();
    const result = await runRuntime(
      "world_game.session.import",
      () => services.session.importSession(sessionId, bundle, null, preferredActorId()),
      "Session bundle imported",
    );
    applyImportedSessionResult(result);

    const activeBranchId = store.getState().branch.activeBranchId;
    if (activeBranchId) {
      await refreshNetworkSnapshot(activeBranchId);
    }
  }

  async function startOnboardingQuickstart() {
    const state = store.getState();
    if (!state.scenario.list.length) {
      await refreshScenarios();
    }
    await ensureSession();
    if (!store.getState().scenario.loadedScenario) {
      await loadScenario();
    }
    if (currentStage() === "setup") {
      await setSessionStage("proposal_intake");
    }
    const currentProposalTitle = store.getState().planning.proposalTitle?.trim();
    if (!currentProposalTitle) {
      store.patchDomain("planning", {
        proposalTitle: "Distributed resilience path",
      });
    }
    store.addNotification(
      "info",
      "Quickstart ready: select a region, create a proposal, run a turn, then open compare/replay/facilitate routes.",
    );
    render();
  }

  function setActiveBranch(branchId) {
    if (!branchId) {
      return;
    }
    store.patchDomain("branch", {
      activeBranchId: branchId,
    });
    maybeSeedCompareTarget(branchId);
    if (!store.getState().replay.branchId) {
      store.patchDomain("replay", {
        branchId,
      });
    }
    render();
    refreshNetworkSnapshot(branchId).catch(() => {
      // Errors are surfaced through runtime notifications.
    });
    refreshAnnotations().catch(() => {
      // Errors are surfaced through runtime notifications.
    });
  }

  function setDominantLayer(layerId) {
    store.patchDomain("layers", {
      dominantLayerId: layerId || "state.water_security",
    });
    render();
  }

  function toggleLayer(layerId, visible) {
    const state = store.getState();
    const existing = new Set(state.layers.visibleLayerIds || []);
    if (visible) {
      existing.add(layerId);
    } else {
      existing.delete(layerId);
    }
    store.patchDomain("layers", {
      visibleLayerIds: Array.from(existing),
    });
    render();
  }

  function setQueueFilter(filter) {
    const allowed = new Set(["all", "draft", "submitted", "under_review", "adopted", "rejected"]);
    store.patchDomain("facilitation", {
      queueFilter: allowed.has(filter) ? filter : "all",
    });
    render();
  }

  function setWorkspaceRole(role) {
    const normalizedRole = WORKSPACE_ROLE_OPTIONS.has(role) ? role : "facilitator";
    const rolePreset = ROLE_PRESET_CONFIG[normalizedRole] || ROLE_PRESET_CONFIG.facilitator;
    store.patchDomain("experience", {
      workspaceRole: normalizedRole,
    });
    store.patchDomain("facilitation", {
      queueFilter: rolePreset.queueFilter,
      followPresenter: rolePreset.followPresenter,
    });
    render();
  }

  function setDensityMode(mode) {
    const densityMode = DENSITY_MODE_OPTIONS.has(mode) ? mode : "default";
    store.patchDomain("experience", {
      densityMode,
    });
    store.patchDomain("facilitation", {
      presentationMode: densityMode === "presentation",
    });
    render();
  }

  function setPresentationMode(enabled) {
    const nextDensity = enabled ? "presentation" : "default";
    store.patchDomain("experience", {
      densityMode: nextDensity,
    });
    store.patchDomain("facilitation", {
      presentationMode: Boolean(enabled),
    });
    render();
  }

  function setSpotlightFromSelection() {
    const state = store.getState();
    const spotlightRegionId = state.selection.regionId || state.selection.proposalRegionIds?.[0] || null;
    if (!spotlightRegionId) {
      store.addNotification("warn", "Select a region before enabling spotlight.");
      render();
      return;
    }
    store.patchDomain("facilitation", {
      spotlightRegionId,
      sharedAttentionStatus: "local-only",
    });
    store.addNotification("info", `Spotlight set to ${spotlightRegionId}`);
    render();
  }

  function clearSpotlight() {
    store.patchDomain("facilitation", {
      spotlightRegionId: null,
      sharedAttentionStatus: "local-only",
    });
    render();
  }

  function setPresenterActor(actorId) {
    const normalized = actorId || preferredActorId();
    store.patchDomain("facilitation", {
      presenterActorId: normalized,
      sharedAttentionStatus: "local-only",
    });
    render();
  }

  function setFollowPresenter(enabled) {
    store.patchDomain("facilitation", {
      followPresenter: Boolean(enabled),
      sharedAttentionStatus: "local-only",
    });
    render();
  }

  function setProposalScope(regionId, options = { append: false }) {
    const state = store.getState();
    const current = new Set(state.selection.proposalRegionIds || []);
    if (options.append) {
      if (current.has(regionId)) {
        current.delete(regionId);
      } else {
        current.add(regionId);
      }
    } else {
      current.clear();
      current.add(regionId);
    }

    store.patchDomain("selection", {
      regionId,
      proposalRegionIds: Array.from(current),
    });
    render();
  }

  const planningWorkspace = createPlanningWorkspace(shell.workspaceContent, {
    onRequestState: () => store.getState(),
    onNavigateRoute: (route) => {
      router.navigate(route);
    },
    onStartOnboarding: () => {
      startOnboardingQuickstart()
        .then(() => {
          router.navigate("plan");
        })
        .catch(() => {
          // Errors are surfaced through runtime notifications.
        });
    },
    onSetSessionStage: (stage) => {
      setSessionStage(stage).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onAdvanceSessionStage: () => {
      advanceSessionStage().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onAddActor: (actorId, role) => {
      addActor(actorId, role).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onSetQueueFilter: (filter) => {
      setQueueFilter(filter);
    },
    onSetWorkspaceRole: (role) => {
      setWorkspaceRole(role);
    },
    onSetDensityMode: (mode) => {
      setDensityMode(mode);
    },
    onSetPresenterActor: (actorId) => {
      setPresenterActor(actorId);
    },
    onSetFollowPresenter: (enabled) => {
      setFollowPresenter(enabled);
    },
    onSetSpotlightFromSelection: () => {
      setSpotlightFromSelection();
    },
    onClearSpotlight: () => {
      clearSpotlight();
    },
    onSetPresentationMode: (enabled) => {
      setPresentationMode(enabled);
    },
    onExportSession: () => {
      exportSessionBundle().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onRefreshContinuity: () => {
      refreshContinuity().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onImportSession: (bundle) => {
      importSessionBundle(bundle).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onImportSessionError: (message) => {
      store.addNotification("warn", message);
      render();
    },
    onSetActiveBranch: (branchId) => setActiveBranch(branchId),
    onFocusRegion: (regionId) => {
      focusRegion(regionId);
    },
    onRefreshNetwork: () => {
      refreshNetworkSnapshot().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onSetDominantLayer: (layerId) => setDominantLayer(layerId),
    onToggleLayer: (layerId, visible) => toggleLayer(layerId, visible),
    onSetProposalTitle: (value) => {
      store.patchDomain("planning", { proposalTitle: value });
      render();
    },
    onSetProposalActor: (value) => {
      store.patchDomain("planning", { proposalActorId: value || DEFAULT_ACTOR_ID });
      render();
    },
    onSetActiveProposal: (proposalId) => {
      store.patchDomain("planning", { activeProposalId: proposalId || null });
      store.patchDomain("selection", { proposalId: proposalId || null });
      render();
    },
    onCreateProposal: () => {
      createProposal().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onSubmitProposal: (proposalId) => {
      submitActiveProposal(proposalId).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onAdoptProposal: (proposalId) => {
      adoptActiveProposal(proposalId).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onRejectProposal: (proposalId) => {
      rejectActiveProposal(proposalId).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onSetIntervention: (interventionId) => {
      store.patchDomain("planning", { activeInterventionId: interventionId || null });
      render();
    },
    onSetShock: (shockId) => {
      store.patchDomain("planning", { activeShockId: shockId || null });
      render();
    },
    onRunTurn: () => {
      runTurn().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onCreateAnnotation: (body) => {
      createAnnotation(body).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onSetCompareBaseline: (branchId) => {
      setCompareBaseline(branchId);
    },
    onSetCompareTarget: (branchId) => {
      setCompareTarget(branchId);
    },
    onSetCompareMode: (mode) => {
      setCompareMode(mode);
    },
    onSetCompareThreshold: (value) => {
      setCompareThreshold(value);
    },
    onSetCompareHotspot: (regionId) => {
      setCompareHotspot(regionId);
    },
    onRunCompare: () => {
      runCompare().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onInspectProvenanceFromCompareHotspot: (regionId) => {
      const state = store.getState();
      const targetBranchId = state.compare.targetBranchIds?.[0] || state.branch.activeBranchId;
      if (!targetBranchId) {
        return;
      }
      inspectProvenance("branch", targetBranchId, `compare hotspot ${regionId || "selection"}`).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onSetReplayBranch: (branchId) => {
      setReplayBranch(branchId);
    },
    onLoadReplay: () => {
      loadReplay().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onSetReplayCursor: (cursorIndex) => {
      setReplayCursor(cursorIndex);
    },
    onStepReplay: (offset) => {
      stepReplay(offset);
    },
    onJumpReplayCheckpoint: (turnIndex) => {
      jumpReplayCheckpoint(turnIndex);
    },
    onInspectProvenanceFromReplayCheckpoint: (turnIndex) => {
      const state = store.getState();
      const branchId = state.replay.branchId || state.branch.activeBranchId;
      if (!branchId) {
        return;
      }
      inspectProvenance("branch", branchId, `replay checkpoint turn ${turnIndex}`).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onInspectProvenance: (artifactType, artifactId, contextLabel) => {
      inspectProvenance(artifactType, artifactId, contextLabel).catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    },
    onRegionSelect: (regionId, options) => {
      setProposalScope(regionId, options);
    },
    onRegionHover: (regionId) => {
      store.patchDomain("selection", { hoverRegionId: regionId });
      render();
    },
    onViewportChange: (viewport) => {
      store.patchDomain("canvas", { viewport });
      render();
    },
  });

  const router = createHashRouter((route) => {
    store.setRoute(route);
    render();

    const state = store.getState();
    if (!state.scenario.loadedScenario) {
      return;
    }

    if (route === "compare" && !state.compare.result) {
      runCompare().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    }

    if (route === "replay" && !(state.replay.frames || []).length) {
      loadReplay().catch(() => {
        // Errors are surfaced through runtime notifications.
      });
    }
  });

  shell.routeButtons.forEach((button) => {
    button.addEventListener("click", () => router.navigate(button.dataset.route));
  });

  shell.scenarioRefreshButton.addEventListener("click", () => {
    refreshScenarios().catch(() => {
      // Error is already handled via notification state.
    });
  });

  shell.scenarioLoadButton.addEventListener("click", () => {
    loadScenario().catch(() => {
      // Error is already handled via notification state.
    });
  });

  shell.sessionCreateButton.addEventListener("click", () => {
    ensureSession().catch(() => {
      // Error is already handled via notification state.
    });
  });

  shell.sessionRefreshButton.addEventListener("click", () => {
    refreshSession().catch(() => {
      // Error is already handled via notification state.
    });
  });

  shell.reducedMotionToggle.addEventListener("change", () => {
    setReducedMotion(shell.reducedMotionToggle.checked);
  });
  shell.workspaceRoleSelect.addEventListener("change", () => {
    setWorkspaceRole(shell.workspaceRoleSelect.value);
  });
  shell.densityModeSelect.addEventListener("change", () => {
    setDensityMode(shell.densityModeSelect.value);
  });

  window.addEventListener("keydown", (event) => {
    if (event.defaultPrevented || isEditableTarget(event.target)) {
      return;
    }
    if (event.altKey && !event.ctrlKey && !event.metaKey) {
      const shortcut = Number(event.key);
      if (Number.isInteger(shortcut) && shortcut >= 1 && shortcut <= KEYBOARD_ROUTE_SHORTCUTS.length) {
        event.preventDefault();
        router.navigate(KEYBOARD_ROUTE_SHORTCUTS[shortcut - 1]);
      }
      if (event.key.toLowerCase() === "m") {
        event.preventDefault();
        setReducedMotion(!store.getState().accessibility.reducedMotion);
      }
    }
  });

  if (typeof window.matchMedia === "function") {
    const reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReducedMotion(reducedMotionQuery.matches);
    if (typeof reducedMotionQuery.addEventListener === "function") {
      reducedMotionQuery.addEventListener("change", (event) => {
        setReducedMotion(event.matches);
      });
    }
  }

  store.subscribe(render);
  router.start();
  render();

  loadGeometryPackage()
    .then((loadedGeometry) => {
      geometryPackage = loadedGeometry;
      store.patchDomain("layers", {
        manifest: {
          availableLayerIds: [
            ...WORLD_CANVAS_LAYER_DEFINITIONS.map((item) => item.id),
            ...DOMINANT_REGION_LAYER_OPTIONS.map((item) => item.id),
          ],
          defaultDominantLayerId: "state.water_security",
        },
      });
      store.addNotification("info", "Dymaxion geometry package loaded");
      render();
    })
    .catch((error) => {
      failRuntime(error);
    });

  refreshScenarios().catch(() => {
    // Error is already handled via notification state.
  });

  runRuntime(
    "world_game.authoring.template.list",
    () => services.authoring.listTemplates(),
    "Authoring templates discovered",
  ).catch(() => {
    // Error is already handled via notification state.
  });
}

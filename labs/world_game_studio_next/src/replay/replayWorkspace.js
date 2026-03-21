import { deriveReplayContext } from "./mapReplayAdapter.js";

function updateSelectOptions(select, options, selectedValue, emptyLabel) {
  const normalized = Array.isArray(options) ? options : [];
  select.innerHTML = "";
  if (!normalized.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = emptyLabel;
    select.appendChild(option);
    select.value = "";
    return;
  }

  for (const item of normalized) {
    const option = document.createElement("option");
    option.value = item.value;
    option.textContent = item.label;
    select.appendChild(option);
  }

  const preferred = selectedValue && normalized.some((item) => item.value === selectedValue)
    ? selectedValue
    : normalized[0].value;
  select.value = preferred;
}

function branchOptions(state) {
  return Object.entries(state.branch.branches || {})
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([branchId, summary]) => ({
      value: branchId,
      label: `${branchId} (turn ${summary.turn ?? 0})`,
    }));
}

function frameSummary(state) {
  const frames = Array.isArray(state.replay.frames) ? state.replay.frames : [];
  const cursorIndex = Math.max(0, Math.min(frames.length - 1, Number(state.replay.cursorIndex ?? 0)));
  const frame = frames[cursorIndex] || null;

  if (!frame) {
    return {
      branch_id: state.replay.branchId || state.branch.activeBranchId || null,
      summary: "Load replay to inspect turn checkpoints.",
    };
  }

  return {
    branch_id: state.replay.branchId || null,
    cursor_index: cursorIndex,
    frame_count: frames.length,
    turn_index: frame.turn_index ?? cursorIndex,
    policy_outcome: frame.policy_outcome ?? null,
    approval_status: frame.approval_status ?? null,
    applied_intervention_ids: frame.applied_intervention_ids || [],
    applied_shock_ids: frame.applied_shock_ids || [],
    replay_matches_live: state.replay.result?.replay_matches_live ?? null,
    replay_composite_score: state.replay.result?.replay_composite_score ?? null,
    live_composite_score: state.replay.result?.live_composite_score ?? null,
  };
}

export function createReplayWorkspace(actions) {
  const root = document.createElement("section");
  root.className = "planning-control-group replay-workspace";
  root.innerHTML = `
    <h3>Replay Timeline</h3>
    <label>
      Replay branch
      <select id="replay-branch-select"></select>
    </label>
    <div class="planning-button-row">
      <button type="button" id="replay-load">Load replay</button>
      <button type="button" id="replay-provenance">Branch provenance</button>
    </div>
    <label>
      Turn cursor
      <input id="replay-cursor" type="range" min="0" max="0" step="1" value="0" />
    </label>
    <div class="planning-button-row">
      <button type="button" id="replay-step-back">Step -1</button>
      <button type="button" id="replay-step-forward">Step +1</button>
    </div>
    <p class="muted" id="replay-headline">Replay not loaded.</p>
    <p class="muted" id="replay-checkpoint-context">Checkpoint: none selected.</p>
    <ul class="planning-inline-list replay-checkpoint-list" id="replay-checkpoints"></ul>
    <pre id="replay-summary" class="planning-result-summary">{}</pre>
  `;

  const elements = {
    branchSelect: root.querySelector("#replay-branch-select"),
    load: root.querySelector("#replay-load"),
    provenance: root.querySelector("#replay-provenance"),
    cursor: root.querySelector("#replay-cursor"),
    stepBack: root.querySelector("#replay-step-back"),
    stepForward: root.querySelector("#replay-step-forward"),
    headline: root.querySelector("#replay-headline"),
    checkpointContext: root.querySelector("#replay-checkpoint-context"),
    checkpoints: root.querySelector("#replay-checkpoints"),
    summary: root.querySelector("#replay-summary"),
  };

  elements.branchSelect.addEventListener("change", () => {
    actions.onSetReplayBranch?.(elements.branchSelect.value || null);
  });
  elements.load.addEventListener("click", () => {
    actions.onLoadReplay?.();
  });
  elements.provenance.addEventListener("click", () => {
    const branchId = elements.branchSelect.value;
    if (!branchId) {
      return;
    }
    actions.onInspectProvenance?.("branch", branchId, "replay branch");
  });
  elements.cursor.addEventListener("input", () => {
    actions.onSetReplayCursor?.(Number(elements.cursor.value));
  });
  elements.stepBack.addEventListener("click", () => {
    actions.onStepReplay?.(-1);
  });
  elements.stepForward.addEventListener("click", () => {
    actions.onStepReplay?.(1);
  });
  elements.checkpoints.addEventListener("click", (event) => {
    const button = event.target.closest("[data-turn-index][data-checkpoint-action]");
    if (!button) {
      return;
    }
    const turnIndex = Number(button.getAttribute("data-turn-index"));
    const action = button.getAttribute("data-checkpoint-action");
    if (!Number.isFinite(turnIndex) || !action) {
      return;
    }
    if (action === "focus") {
      actions.onJumpReplayCheckpoint?.(turnIndex);
      return;
    }
    if (action === "provenance") {
      actions.onJumpReplayCheckpoint?.(turnIndex);
      actions.onInspectProvenanceFromReplayCheckpoint?.(turnIndex);
    }
  });

  function render(state) {
    updateSelectOptions(
      elements.branchSelect,
      branchOptions(state),
      state.replay.branchId || state.branch.activeBranchId,
      "(select replay branch)",
    );

    const frames = Array.isArray(state.replay.frames) ? state.replay.frames : [];
    const maxCursor = Math.max(0, frames.length - 1);
    const cursor = Math.max(0, Math.min(maxCursor, Number(state.replay.cursorIndex ?? 0)));
    elements.cursor.max = String(maxCursor);
    elements.cursor.value = String(cursor);
    elements.cursor.disabled = frames.length <= 1;

    const summary = frameSummary(state);
    const replayContext = deriveReplayContext(state);
    if (!frames.length) {
      elements.headline.textContent = "Replay not loaded.";
    } else {
      elements.headline.textContent = `Turn ${summary.turn_index} of ${maxCursor} on ${summary.branch_id}`;
    }

    elements.checkpoints.innerHTML = "";
    if (!replayContext?.checkpoints?.length) {
      const item = document.createElement("li");
      item.textContent = "Checkpoints appear after replay loads.";
      elements.checkpoints.appendChild(item);
      elements.checkpointContext.textContent = "Checkpoint: none selected.";
    } else {
      const selectedTurn = replayContext.selectedCheckpointTurn;
      elements.checkpointContext.textContent =
        selectedTurn === null ? "Checkpoint: none selected." : `Checkpoint turn ${selectedTurn}`;
      for (const checkpoint of replayContext.checkpoints) {
        const item = document.createElement("li");
        item.className = "planning-queue-item";
        const selectedFlag = checkpoint.turnIndex === selectedTurn ? "*" : "-";
        const cue = checkpoint.branchPoint
          ? `branch point from ${checkpoint.branchSource}`
          : checkpoint.policyOutcome || (checkpoint.appliedShocks.length ? "shock checkpoint" : "checkpoint");
        item.innerHTML = `
          <p><strong>${selectedFlag} Turn ${checkpoint.turnIndex}</strong> <span class="muted">[${cue}]</span></p>
          <p class="muted">max delta ${checkpoint.maxDelta.toFixed(4)} · regions ${checkpoint.changedRegions.join(", ") || "(none)"}</p>
          <div class="planning-button-row">
            <button type="button" data-checkpoint-action="focus" data-turn-index="${checkpoint.turnIndex}">Focus</button>
            <button type="button" data-checkpoint-action="provenance" data-turn-index="${checkpoint.turnIndex}">Provenance</button>
          </div>
        `;
        elements.checkpoints.appendChild(item);
      }
    }
    elements.summary.textContent = JSON.stringify(summary, null, 2);

    root.classList.toggle("is-active", state.route === "replay");
  }

  return {
    root,
    render,
  };
}

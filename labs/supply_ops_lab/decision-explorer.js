const DOM = {
  statusBanner: document.getElementById("explorer-status-banner"),
  boundaryNotes: document.getElementById("explorer-boundary-notes"),
  truthNotes: document.getElementById("explorer-truth-notes"),
  commitmentSummary: document.getElementById("explorer-commitment-summary"),
  proposalCards: document.getElementById("explorer-proposal-cards"),
  weightControls: document.getElementById("explorer-weight-controls"),
  simulationControls: document.getElementById("explorer-simulation-controls"),
  planCards: document.getElementById("explorer-plan-cards"),
  decisionCard: document.getElementById("explorer-decision-card"),
  whySelected: document.getElementById("explorer-why-selected"),
  whyNotSelected: document.getElementById("explorer-why-not-selected"),
  rawJson: document.getElementById("explorer-raw-json"),
  resetDefaultsButton: document.getElementById("explorer-reset-defaults"),
  applyServiceHeavyButton: document.getElementById("explorer-apply-service-heavy"),
};

let bootstrapPayload = null;
let currentEvaluation = null;
let currentWeights = {};
let currentSimulationMode = "include";

init();

function init() {
  DOM.resetDefaultsButton.addEventListener("click", () => {
    if (!bootstrapPayload) {
      return;
    }
    const request = bootstrapPayload.controls.default_request;
    applyRequest(request.weights, request.simulation_mode);
  });
  DOM.applyServiceHeavyButton.addEventListener("click", () => {
    if (!bootstrapPayload) {
      return;
    }
    const request = bootstrapPayload.controls.service_heavy_example;
    applyRequest(request.weights, request.simulation_mode);
  });
  renderPlaceholder();
  loadBootstrap();
}

async function loadBootstrap() {
  setStatus("loading", "Loading the SO-P4 Decision Explorer concept surface...");
  try {
    const payload = await fetchJson("/api/supply-ops/decision-explorer/bootstrap");
    bootstrapPayload = payload;
    currentWeights = { ...payload.controls.default_request.weights };
    currentSimulationMode = payload.controls.default_request.simulation_mode;
    renderBootstrap(payload);
    renderEvaluation(payload.initial_evaluation);
    setStatus(
      "ready",
      `${payload.initial_evaluation.selected_plan_id} is the default recommendation. Adjust weights to compare the parallel plan.`,
    );
  } catch (error) {
    DOM.rawJson.textContent = pretty({ error: error.message });
    setStatus("error", `Decision Explorer bootstrap failed: ${error.message}`);
  }
}

function renderBootstrap(payload) {
  renderStringList(DOM.boundaryNotes, payload.boundary_notes);
  renderStringList(DOM.truthNotes, payload.truth_notes);
  renderCommitment(payload.commitment);
  renderProposals(payload.proposal_catalog);
  renderControls(payload.controls);
}

function renderCommitment(commitment) {
  renderSummaryGrid(DOM.commitmentSummary, [
    ["Commitment", commitment.commitment_id],
    ["Customer", commitment.customer],
    ["SKU", commitment.sku],
    ["At-Risk Units", String(commitment.at_risk_units)],
    ["Promise Date", commitment.promised_date],
    ["Anchor", commitment.anchor_note],
    ["Risk", commitment.current_risk],
  ]);
}

function renderProposals(proposals) {
  DOM.proposalCards.innerHTML = proposals
    .map(
      (proposal) => `
        <article class="explorer-card">
          <p class="explorer-chip">${escapeHtml(proposal.label)}</p>
          <h3>${escapeHtml(proposal.headline)}</h3>
          <p class="panel-copy">${escapeHtml(proposal.summary)}</p>
          <div class="summary-grid compact-grid">
            ${summaryCard("Recovery Units", proposal.recovery_units)}
            ${summaryCard("Lane", proposal.lane_id)}
          </div>
          <p class="card-footnote">${escapeHtml(proposal.effect)}</p>
        </article>
      `,
    )
    .join("");
}

function renderControls(controls) {
  DOM.weightControls.innerHTML = controls.weights
    .map(
      (item) => `
        <label class="control-card" for="weight-${escapeHtml(item.id)}">
          <span class="control-label">${escapeHtml(item.label)}</span>
          <div class="control-input-row">
            <input
              id="weight-${escapeHtml(item.id)}"
              data-weight-id="${escapeHtml(item.id)}"
              type="range"
              min="${item.min}"
              max="${item.max}"
              step="${item.step}"
              value="${item.default_value}"
            />
            <output id="weight-output-${escapeHtml(item.id)}">${item.default_value}</output>
          </div>
        </label>
      `,
    )
    .join("");

  DOM.weightControls.querySelectorAll("[data-weight-id]").forEach((input) => {
    input.addEventListener("input", () => {
      const weightId = input.getAttribute("data-weight-id");
      currentWeights[weightId] = Number(input.value);
      const output = document.getElementById(`weight-output-${weightId}`);
      if (output) {
        output.textContent = input.value;
      }
    });
    input.addEventListener("change", submitEvaluation);
  });

  DOM.simulationControls.innerHTML = controls.simulation_modes
    .map(
      (item) => `
        <label class="toggle-card">
          <input
            type="radio"
            name="simulation-mode"
            value="${escapeHtml(item.id)}"
            ${item.id === controls.default_request.simulation_mode ? "checked" : ""}
          />
          <span>
            <strong>${escapeHtml(item.label)}</strong>
            <small>${escapeHtml(item.description)}</small>
          </span>
        </label>
      `,
    )
    .join("");

  DOM.simulationControls.querySelectorAll('input[name="simulation-mode"]').forEach((input) => {
    input.addEventListener("change", () => {
      currentSimulationMode = input.value;
      submitEvaluation();
    });
  });
}

async function applyRequest(weights, simulationMode) {
  currentWeights = { ...weights };
  currentSimulationMode = simulationMode;
  Object.entries(currentWeights).forEach(([weightId, value]) => {
    const input = document.getElementById(`weight-${weightId}`);
    const output = document.getElementById(`weight-output-${weightId}`);
    if (input) {
      input.value = value;
    }
    if (output) {
      output.textContent = String(value);
    }
  });
  DOM.simulationControls.querySelectorAll('input[name="simulation-mode"]').forEach((input) => {
    input.checked = input.value === simulationMode;
  });
  await submitEvaluation();
}

async function submitEvaluation() {
  if (!bootstrapPayload) {
    return;
  }
  setStatus("loading", "Re-evaluating the curated plans on the server...");
  try {
    const payload = await fetchJson("/api/supply-ops/decision-explorer/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        weights: currentWeights,
        simulation_mode: currentSimulationMode,
      }),
    });
    renderEvaluation(payload);
    setStatus(
      "ready",
      `${payload.selected_plan_id} is selected with a score gap of ${payload.decision_summary.score_gap}.`,
    );
  } catch (error) {
    DOM.rawJson.textContent = pretty({
      weights: currentWeights,
      simulation_mode: currentSimulationMode,
      error: error.message,
    });
    setStatus("error", `Decision Explorer evaluation failed: ${error.message}`);
  }
}

function renderEvaluation(payload) {
  currentEvaluation = payload;
  renderPlanCards(payload.plans, payload.selected_plan_id);
  renderDecision(payload.decision_summary);
  renderStringList(DOM.whySelected, payload.why_selected);
  renderStringList(DOM.whyNotSelected, payload.why_not_selected);
  DOM.rawJson.textContent = pretty(payload);
}

function renderPlanCards(plans, selectedPlanId) {
  DOM.planCards.innerHTML = plans
    .map((item) => {
      const isSelected = item.plan.plan_id === selectedPlanId;
      const outcome = item.policy_surface.final_outcome || "neutral";
      const breakdown = item.score.breakdown
        .map(
          (entry) => `
            <li>${escapeHtml(entry.label)}: weight ${entry.weight}, score ${entry.score}, contribution ${entry.contribution}</li>
          `,
        )
        .join("");

      return `
        <article class="explorer-card ${isSelected ? "explorer-card-selected" : ""}">
          <div class="explorer-card-header">
            <div>
              <p class="explorer-chip">${escapeHtml(item.plan.label)}</p>
              <h3>${escapeHtml(item.plan.headline)}</h3>
            </div>
            <p class="score-pill">${item.score.total}</p>
          </div>
          <p class="panel-copy">${escapeHtml(item.plan.summary)}</p>
          <div class="summary-grid compact-grid">
            ${summaryCard("Late Units", item.plan.metrics.late_units_after_action)}
            ${summaryCard("Fill Rate", `${item.plan.metrics.projected_fill_rate_percent}%`)}
            ${summaryCard("Inventory Cover", `${item.plan.metrics.projected_post_action_inventory_days} days`)}
            ${summaryCard("Expedite Delta", `${item.plan.metrics.expedite_cost_delta_percent}%`)}
            ${summaryCard("Margin Delta", `${item.plan.metrics.projected_margin_delta_percent}%`)}
            ${summaryCard("Policy", outcome.replaceAll("_", " "))}
          </div>
          <p class="card-footnote">Includes: ${item.plan.proposal_ids.join(", ")}</p>
          <ul class="note-list compact-list">${breakdown}</ul>
        </article>
      `;
    })
    .join("");
}

function renderDecision(summary) {
  DOM.decisionCard.className = `gate-card gate-${escapeHtml(summary.selected_policy_outcome || "neutral")}`;
  DOM.decisionCard.innerHTML = `
    <p class="gate-title">${escapeHtml(summary.headline)}</p>
    <p class="gate-copy">${escapeHtml(summary.policy_shift_copy)}</p>
    <p class="gate-copy">Top weight: ${escapeHtml(summary.top_weight_label)}. Score gap: ${summary.score_gap}.</p>
  `;
}

function renderPlaceholder() {
  renderSummaryGrid(DOM.commitmentSummary, [], "Commitment context loads with bootstrap.");
  renderStringList(
    DOM.boundaryNotes,
    [],
    "Boundary notes will load with the Decision Explorer bootstrap payload.",
  );
  renderStringList(
    DOM.truthNotes,
    [],
    "Truth notes will load with the Decision Explorer bootstrap payload.",
  );
  DOM.proposalCards.innerHTML = '<p class="empty-copy">Proposal cards load with bootstrap.</p>';
  DOM.weightControls.innerHTML = '<p class="empty-copy">Weight controls load with bootstrap.</p>';
  DOM.simulationControls.innerHTML = '<p class="empty-copy">Simulation controls load with bootstrap.</p>';
  DOM.planCards.innerHTML = '<p class="empty-copy">Plan comparison loads after bootstrap.</p>';
  renderStringList(DOM.whySelected, [], "Selected-plan reasoning will appear after evaluation.");
  renderStringList(DOM.whyNotSelected, [], "Runner-up reasoning will appear after evaluation.");
}

async function fetchJson(url, init = {}) {
  const headers = {
    Accept: "application/json",
    ...(init.headers || {}),
  };
  const response = await fetch(url, {
    ...init,
    headers,
  });
  const bodyText = await response.text();
  let payload = null;
  if (bodyText) {
    payload = JSON.parse(bodyText);
  }
  if (!response.ok || !payload?.ok) {
    throw new Error(payload?.error?.message || "Request failed");
  }
  return payload.result;
}

function renderSummaryGrid(container, entries, emptyMessage = "No summary data is available yet.") {
  if (!entries || entries.length === 0) {
    container.innerHTML = `<p class="empty-copy">${escapeHtml(emptyMessage)}</p>`;
    return;
  }
  container.innerHTML = entries
    .map(
      ([label, value]) => `
        <dl class="summary-card">
          <dt>${escapeHtml(label)}</dt>
          <dd>${escapeHtml(String(value))}</dd>
        </dl>
      `,
    )
    .join("");
}

function renderStringList(container, items, emptyMessage = "No items are available yet.") {
  if (!items || items.length === 0) {
    container.innerHTML = `<li class="empty-copy">${escapeHtml(emptyMessage)}</li>`;
    return;
  }
  container.innerHTML = items.map((item) => `<li>${escapeHtml(String(item))}</li>`).join("");
}

function summaryCard(label, value) {
  return `
    <dl class="summary-card">
      <dt>${escapeHtml(String(label))}</dt>
      <dd>${escapeHtml(String(value))}</dd>
    </dl>
  `;
}

function setStatus(state, message) {
  DOM.statusBanner.dataset.state = state;
  DOM.statusBanner.textContent = message;
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

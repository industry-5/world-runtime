const DOM = {
  statusBanner: document.getElementById("status-banner"),
  boundaryNotes: document.getElementById("boundary-notes"),
  startupCommands: document.getElementById("startup-commands"),
  demoChecklist: document.getElementById("demo-checklist"),
  smokeChecks: document.getElementById("smoke-checks"),
  presetCards: document.getElementById("preset-cards"),
  apiWiring: document.getElementById("api-wiring"),
  ingressSummary: document.getElementById("ingress-summary"),
  proposalStory: document.getElementById("proposal-story"),
  proposalSummary: document.getElementById("proposal-summary"),
  proposalJson: document.getElementById("proposal-json"),
  policyGate: document.getElementById("policy-gate"),
  policyDetails: document.getElementById("policy-details"),
  replaySummary: document.getElementById("replay-summary"),
  simulationSummary: document.getElementById("simulation-summary"),
  simulationDiffRows: document.getElementById("simulation-diff-rows"),
  timelineFlow: document.getElementById("timeline-flow"),
  scenarioEvidence: document.getElementById("scenario-evidence"),
  rawJson: document.getElementById("raw-json"),
  runButton: document.getElementById("run-reviewed-path"),
  retryButton: document.getElementById("retry-bootstrap"),
};

let bootstrapPayload = null;
let selectedFixtureName = null;
let currentRunPayload = null;

init();

function init() {
  DOM.runButton.addEventListener("click", runSelectedFlow);
  DOM.retryButton.addEventListener("click", loadBootstrap);
  renderStartupGuide(null);
  renderSelectionPlaceholder(
    "Loading the supported Supply Ops snapshot. The browser stays render-only while the lab server assembles the documented adapter path.",
  );
  loadBootstrap();
}

async function loadBootstrap() {
  setStatusBanner(
    "loading",
    "Loading lab bootstrap and the documented SO-P3 runbook...",
  );
  bootstrapPayload = null;
  currentRunPayload = null;
  DOM.runButton.disabled = true;
  DOM.retryButton.disabled = true;
  try {
    const response = await fetchJson("/api/supply-ops/bootstrap");
    bootstrapPayload = response;
    selectedFixtureName =
      response.preset_snapshots?.[selectedFixtureName]
        ? selectedFixtureName
        : response.default_preset_fixture_name;
    renderBootstrap(response);
    setStatusBanner(
      "ready",
      "Bootstrap loaded. Choose a preset to inspect the supported SO-P3 flow, then run it through the stable API path.",
    );
  } catch (error) {
    selectedFixtureName = null;
    renderStartupGuide(null);
    renderPresetCards([]);
    renderApiWiring([]);
    renderStringList(
      DOM.boundaryNotes,
      [],
      "Bootstrap must load before the thin-client/runtime-authoritative boundary notes can be rendered.",
    );
    renderSelectionPlaceholder(
      "Bootstrap is unavailable. Start the upstream API and the lab server, then reload bootstrap to repopulate the supported preset flow.",
    );
    DOM.rawJson.textContent = pretty({ error: error.message });
    setStatusBanner("error", `Bootstrap failed: ${error.message}`);
  } finally {
    DOM.retryButton.disabled = false;
    updateRunButtonState();
  }
}

async function runSelectedFlow() {
  const snapshot = getSelectedSnapshot();
  if (!snapshot) {
    setStatusBanner("error", "Select a preset before running the flow.");
    return;
  }

  setStatusBanner(
    "loading",
    `Running ${snapshot.preset.label} through the stable API path...`,
  );
  DOM.runButton.disabled = true;

  try {
    const response = await fetchJson("/api/supply-ops/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fixture_name: selectedFixtureName }),
    });
    currentRunPayload = response;
    renderSelectedState();
    setStatusBanner(
      "ready",
      `${response.preset.label} completed with outcome ${response.policy_summary.final_outcome}.`,
    );
  } catch (error) {
    DOM.rawJson.textContent = pretty({
      fixture_name: selectedFixtureName,
      error: error.message,
    });
    setStatusBanner("error", `Run failed: ${error.message}`);
  } finally {
    updateRunButtonState();
  }
}

function renderBootstrap(payload) {
  renderStringList(DOM.boundaryNotes, payload.boundary_notes);
  renderStartupGuide(payload.startup_guide);
  renderApiWiring(payload.stable_api_wiring);
  renderPresetCards(payload.preset_catalog);
  renderSelectedState();
}

function renderSelectedState() {
  const snapshot = getSelectedSnapshot();
  if (!snapshot) {
    renderSelectionPlaceholder(
      "Choose a preset to inspect the translated proposal, policy gate, replay summary, and simulation summary before running the supported path.",
    );
    DOM.runButton.textContent = "Run Selected Preset";
    updateRunButtonState();
    return;
  }

  const activePayload = getActivePayload(snapshot);
  renderPresetCards(bootstrapPayload.preset_catalog);
  renderIngressSummary(snapshot.ingress);
  renderProposalOverview(snapshot.proposal_overview, snapshot.translated_proposal);
  renderPolicyGate(
    activePayload.policy_summary || snapshot.policy_preview,
    activePayload.policy_gate || snapshot.policy_preview,
  );
  renderReplaySummary(snapshot.replay_summary);
  renderSimulationSummary(snapshot.simulation_summary);
  renderTimeline(activePayload.timeline || snapshot.timeline);
  renderScenarioEvidence(snapshot.scenario_evidence);
  DOM.proposalJson.textContent = pretty(snapshot.translated_proposal);
  DOM.rawJson.textContent = pretty(activePayload);
  DOM.runButton.textContent = `Run ${snapshot.preset.label}`;
  updateRunButtonState();
}

function getSelectedSnapshot() {
  return bootstrapPayload?.preset_snapshots?.[selectedFixtureName] || null;
}

function getActivePayload(snapshot) {
  if (
    currentRunPayload &&
    currentRunPayload.preset &&
    currentRunPayload.preset.fixture_name === snapshot.preset.fixture_name
  ) {
    return currentRunPayload;
  }
  return snapshot;
}

function renderSelectionPlaceholder(message) {
  DOM.proposalStory.textContent = message;
  renderSummaryGrid(DOM.ingressSummary, [], "Ingress metadata appears after bootstrap loads a preset.");
  renderSummaryGrid(DOM.proposalSummary, [], "Readable proposal metrics appear after you choose a preset.");
  DOM.proposalJson.textContent = message;
  renderPolicyGate(
    {
      final_outcome: "neutral",
      headline: message,
      approval_copy: "Run a preset to inspect the upstream approval posture.",
      details: [],
    },
    null,
  );
  renderSummaryGrid(DOM.replaySummary, [], "Replay summary appears after you choose a preset.");
  renderSummaryGrid(
    DOM.simulationSummary,
    [],
    "Simulation summary appears after you choose a preset.",
  );
  DOM.simulationDiffRows.innerHTML =
    '<tr><td colspan="3" class="empty-copy">No simulation diff is loaded yet.</td></tr>';
  renderTimeline([], "Timeline appears after you choose a preset.");
  renderStringList(
    DOM.scenarioEvidence,
    [],
    "Scenario artifact references appear after bootstrap loads the selected preset.",
  );
  DOM.rawJson.textContent = pretty({});
}

function renderPresetCards(presets) {
  if (!presets || presets.length === 0) {
    DOM.presetCards.innerHTML = '<p class="empty-copy">No preset catalog is available yet.</p>';
    return;
  }

  DOM.presetCards.innerHTML = (presets || [])
    .map((preset) => {
      const isActive = preset.fixture_name === selectedFixtureName;
      return `
        <button
          class="preset-card preset-${escapeHtml(preset.expected_outcome)}${isActive ? " preset-active" : ""}"
          type="button"
          data-fixture-name="${escapeHtml(preset.fixture_name)}"
        >
          <span class="preset-outcome">${escapeHtml(preset.expected_outcome.replaceAll("_", " "))}</span>
          <strong>${escapeHtml(preset.label)}</strong>
          <span>${escapeHtml(preset.headline)}</span>
        </button>
      `;
    })
    .join("");

  DOM.presetCards.querySelectorAll("[data-fixture-name]").forEach((element) => {
    element.addEventListener("click", () => {
      selectedFixtureName = element.getAttribute("data-fixture-name");
      renderSelectedState();
      const snapshot = getSelectedSnapshot();
      if (snapshot) {
        setStatusBanner(
          "ready",
          `${snapshot.preset.label} selected. Review the readable summaries, then run when ready.`,
        );
      }
    });
  });
}

function renderApiWiring(items) {
  const rows = items.map((item) => `${item.method} ${item.path} - ${item.label}`);
  renderStringList(
    DOM.apiWiring,
    rows,
    "Stable API wiring details load with bootstrap.",
  );
}

function renderStartupGuide(guide) {
  renderCommandList(
    DOM.startupCommands,
    guide?.commands || [],
    "Startup commands load with the bootstrap payload.",
  );
  renderStringList(
    DOM.demoChecklist,
    guide?.demo_steps || [],
    "Demo steps load with the bootstrap payload.",
  );
  renderCommandList(
    DOM.smokeChecks,
    guide?.smoke_checks || [],
    "Smoke checks load with the bootstrap payload.",
  );
}

function renderIngressSummary(ingress) {
  const entries = [
    ["Connector", ingress.connector_id],
    ["Provider", ingress.provider],
    ["Direction", ingress.direction],
    ["Boundary", ingress.governance.translation_boundary],
    ["Envelope", ingress.envelope_id],
    ["Received", ingress.received_at],
  ];
  renderSummaryGrid(DOM.ingressSummary, entries);
}

function renderProposalOverview(overview, proposal) {
  DOM.proposalStory.textContent = `${overview.operator_goal} ${overview.tradeoff}`;
  renderSummaryGrid(DOM.proposalSummary, overview.metrics);
  DOM.proposalJson.textContent = pretty(proposal);
}

function renderPolicyGate(summary, rawPolicyGate) {
  const outcome = summary.final_outcome || "unknown";
  const title = outcome.replaceAll("_", " ");
  DOM.policyGate.className = `gate-card gate-${outcome}`;
  DOM.policyGate.innerHTML = `
    <p class="gate-title">${title}</p>
    <p class="gate-copy">${escapeHtml(summary.headline || "Policy completed without rule detail.")}</p>
    <p class="gate-copy">${escapeHtml(summary.approval_copy || "No approval detail available.")}</p>
  `;
  renderStringList(
    DOM.policyDetails,
    summary.details || (rawPolicyGate?.evaluations || []).map((item) => item.message),
  );
}

function renderReplaySummary(summary) {
  renderSummaryGrid(DOM.replaySummary, [
    ["Projection", summary.projection_name],
    ["Offset", String(summary.source_event_offset)],
    ["Events", String(summary.events_processed)],
    ["Commitment Status", summary.commitment_state.status],
    ["At-Risk Units", String(summary.commitment_state.at_risk_units)],
    ["Reviewed Example", `${summary.reviewed_example_projection_name} @ ${summary.reviewed_example_offset}`],
  ]);
}

function renderSimulationSummary(summary) {
  if (!summary) {
    renderSummaryGrid(
      DOM.simulationSummary,
      [],
      "Simulation summary appears after you choose a preset.",
    );
    DOM.simulationDiffRows.innerHTML =
      '<tr><td colspan="3" class="empty-copy">No simulation diff is loaded yet.</td></tr>';
    return;
  }
  renderSummaryGrid(DOM.simulationSummary, [
    ["Simulation", summary.simulation_id],
    ["Status", summary.status],
    ["Hypothetical Events", String(summary.hypothetical_events_applied)],
    ["Changed Paths", String(summary.changed_path_count)],
    ["Base Commitment", summary.base_commitment.status],
    ["Simulated Commitment", summary.simulated_commitment.status],
    ["Late Units", `${summary.baseline_late_units} -> ${summary.projected_late_units_after_action}`],
    ["Inventory Cover", `${summary.projected_post_action_inventory_days} days`],
  ]);

  const rows = Object.entries(summary.state_diff || {})
    .slice(0, 12)
    .map(([path, values]) => {
      return `<tr>
        <td>${escapeHtml(path)}</td>
        <td><code>${escapeHtml(stringifyInline(values.base))}</code></td>
        <td><code>${escapeHtml(stringifyInline(values.simulated))}</code></td>
      </tr>`;
    })
    .join("");

  DOM.simulationDiffRows.innerHTML =
    rows || '<tr><td colspan="3">No diff rows were returned.</td></tr>';
}

function renderTimeline(items, emptyMessage = "Choose a preset to render the supported operator flow.") {
  if (!items || items.length === 0) {
    DOM.timelineFlow.innerHTML = `
      <li class="timeline-item timeline-neutral">
        <p class="timeline-title">Waiting for a preset</p>
        <p class="timeline-meta">timeline</p>
        <p class="timeline-copy">${escapeHtml(emptyMessage)}</p>
      </li>
    `;
    return;
  }
  DOM.timelineFlow.innerHTML = (items || [])
    .map((item) => {
      return `
        <li class="timeline-item timeline-${escapeHtml(item.status || "neutral")}">
          <p class="timeline-title">${escapeHtml(item.title)}</p>
          <p class="timeline-meta">${escapeHtml(item.stage || "stage")}</p>
          <p class="timeline-copy">${escapeHtml(item.detail || "")}</p>
        </li>
      `;
    })
    .join("");
}

function renderScenarioEvidence(evidence) {
  if (!evidence) {
    renderStringList(
      DOM.scenarioEvidence,
      [],
      "Scenario artifact references appear after you choose a preset.",
    );
    return;
  }
  const items = [
    `Scenario: ${evidence.scenario_id}`,
    `Preset proposal: ${evidence.proposal.proposal_id} (${evidence.proposal.action_type})`,
    `Reviewed example proposal: ${evidence.proposal.reviewed_example_proposal_id}`,
    `Simulation artifact: ${evidence.simulation.simulation_id} -> projected late units ${evidence.simulation.projected_late_units_after_action}`,
    `Decision artifact: ${evidence.decision.decision_id} (${evidence.decision.approval_status})`,
    `Projection artifact: ${evidence.projection.projection_name} @ offset ${evidence.projection.source_event_offset}`,
    `Reviewed example match: ${evidence.reviewed_example_match ? "yes" : "no"}`,
    ...evidence.notes,
    ...evidence.artifact_paths,
  ];
  renderStringList(DOM.scenarioEvidence, items);
}

function renderSummaryGrid(
  container,
  entries,
  emptyMessage = "No summary data is available yet.",
) {
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
  container.innerHTML = (items || [])
    .map((item) => `<li>${escapeHtml(String(item))}</li>`)
    .join("");
}

function renderCommandList(container, items, emptyMessage) {
  if (!items || items.length === 0) {
    container.innerHTML = `<li class="empty-copy">${escapeHtml(emptyMessage)}</li>`;
    return;
  }
  container.innerHTML = items
    .map(
      (item) => `
        <li class="command-item">
          <p class="command-label">${escapeHtml(item.label)}</p>
          <code class="command-line">${escapeHtml(item.command)}</code>
        </li>
      `,
    )
    .join("");
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
    try {
      payload = JSON.parse(bodyText);
    } catch (error) {
      if (!response.ok) {
        throw new Error(bodyText.trim() || `Request failed with ${response.status}`);
      }
      throw new Error("Response was not valid JSON.");
    }
  }
  if (!payload || typeof payload !== "object") {
    throw new Error("Response payload was empty.");
  }
  if (!response.ok || !payload.ok) {
    const message = payload.error?.message || "Request failed";
    throw new Error(message);
  }
  return payload.result;
}

function updateRunButtonState() {
  DOM.runButton.disabled = !getSelectedSnapshot();
}

function setStatusBanner(state, message) {
  DOM.statusBanner.dataset.state = state;
  DOM.statusBanner.textContent = message;
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function stringifyInline(value) {
  return JSON.stringify(value);
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

/**
 * @typedef {Object} RunRequest
 * @property {Object} proposal
 * @property {Object|null} policy
 * @property {Object} simulation
 */

/**
 * @typedef {Object} GateState
 * @property {"allow"|"warn"|"require_approval"|"deny"|"unknown"} outcome
 * @property {string} label
 * @property {string} detail
 * @property {string} approvalStatus
 */

/**
 * @typedef {Object} RunResult
 * @property {Object} session
 * @property {Object} proposalResult
 * @property {Object} simulationResult
 * @property {Object} decisionResult
 * @property {Object} telemetrySummary
 * @property {Object} dashboard
 * @property {Array<Object>} traces
 * @property {Array<Object>} telemetryEvents
 * @property {Array<Object>} sessionEvents
 * @property {Array<Object>} timeline
 */

const PRESETS = {
  baseline_reroute: {
    label: "Baseline reroute (allow/warn)",
    proposal: {
      proposal_id: "proposal.world-run-lab.baseline",
      proposer: "world-run-lab",
      proposed_action: {
        action_type: "reroute_shipment",
        target_ref: "shipment.88421",
        payload: { new_route: "route.delta" },
      },
      rationale: "Use alternate route to reduce delay risk.",
    },
    policy: null,
    simulation: {
      simulation_id: "sim.world-run-lab.baseline",
      projection_name: "world_state",
      scenario_name: "baseline reroute impact",
      assumptions: ["route.delta capacity remains stable"],
      inputs: { shipment_id: "shipment.88421" },
      hypothetical_events: [
        {
          event_type: "shipment_rerouted",
          payload: { shipment_id: "shipment.88421", new_route: "route.delta" },
        },
      ],
    },
  },
  approval_gate: {
    label: "Requires approval",
    proposal: {
      proposal_id: "proposal.world-run-lab.approval",
      proposer: "world-run-lab",
      proposed_action: {
        action_type: "reroute_shipment",
        target_ref: "shipment.88421",
        payload: { new_route: "route.gamma" },
      },
      rationale: "Emergency reroute through partner lane.",
    },
    policy: {
      policy_id: "policy.world-run-lab.approval",
      policy_name: "reroute requires approval",
      default_outcome: "allow",
      rules: [
        {
          rule_id: "rule.world-run-lab.approval",
          rule_name: "approval gate for reroute",
          condition: {
            field: "proposed_action.action_type",
            operator: "equals",
            value: "reroute_shipment",
          },
          outcome: "require_approval",
          message_template: "Operator approval required for reroute_shipment",
        },
      ],
    },
    simulation: {
      simulation_id: "sim.world-run-lab.approval",
      projection_name: "world_state",
      scenario_name: "approval path what-if",
      assumptions: ["approval delay under 15 minutes"],
      inputs: { shipment_id: "shipment.88421" },
      hypothetical_events: [
        {
          event_type: "shipment_delayed",
          payload: {
            shipment_id: "shipment.88421",
            delay_hours: 2,
            cause: "weather",
          },
        },
      ],
    },
  },
  deny_case: {
    label: "Policy deny",
    proposal: {
      proposal_id: "proposal.world-run-lab.deny",
      proposer: "world-run-lab",
      proposed_action: {
        action_type: "reroute_shipment",
        target_ref: "shipment.88421",
        payload: { new_route: "route.risky" },
      },
      rationale: "Route has known compliance risk.",
    },
    policy: {
      policy_id: "policy.world-run-lab.deny",
      policy_name: "deny risky route",
      default_outcome: "allow",
      rules: [
        {
          rule_id: "rule.world-run-lab.deny",
          rule_name: "deny route.risky",
          condition: {
            field: "proposed_action.payload.new_route",
            operator: "equals",
            value: "route.risky",
          },
          outcome: "deny",
          message_template: "Route route.risky is blocked by policy",
        },
      ],
    },
    simulation: {
      simulation_id: "sim.world-run-lab.deny",
      projection_name: "world_state",
      scenario_name: "deny path what-if",
      assumptions: ["blocked route would trigger fallback"],
      inputs: { shipment_id: "shipment.88421" },
      hypothetical_events: [
        {
          event_type: "shipment_route_blocked",
          payload: {
            shipment_id: "shipment.88421",
            route_id: "route.risky",
            reason: "policy_block",
          },
        },
      ],
    },
  },
};

const STEP_NAMES = [
  "create session",
  "submit proposal",
  "run simulation",
  "create decision",
  "refresh telemetry",
  "refresh dashboard",
  "list traces",
  "list telemetry events",
  "fetch session events",
];

const DOM = {
  presetSelect: document.getElementById("preset-select"),
  applyPresetBtn: document.getElementById("apply-preset"),
  runDemoBtn: document.getElementById("run-demo"),
  clearResultsBtn: document.getElementById("clear-results"),
  apiBaseInput: document.getElementById("api-base"),
  apiTokenInput: document.getElementById("api-token"),
  proposalJson: document.getElementById("proposal-json"),
  simulationJson: document.getElementById("simulation-json"),
  policyJson: document.getElementById("policy-json"),
  stepStrip: document.getElementById("step-strip"),
  runMessage: document.getElementById("run-message"),
  gateCard: document.getElementById("policy-gate-card"),
  simulationSummary: document.getElementById("simulation-delta-summary"),
  simulationRows: document.getElementById("simulation-delta-rows"),
  timeline: document.getElementById("results-timeline"),
  rawJson: document.getElementById("raw-json"),
};

let currentStepState = STEP_NAMES.map((name) => ({ name, status: "pending" }));

function init() {
  Object.entries(PRESETS).forEach(([id, preset]) => {
    const opt = document.createElement("option");
    opt.value = id;
    opt.textContent = preset.label;
    DOM.presetSelect.appendChild(opt);
  });

  DOM.presetSelect.value = "baseline_reroute";
  applyPreset("baseline_reroute");
  renderStepStrip();

  DOM.applyPresetBtn.addEventListener("click", () => applyPreset(DOM.presetSelect.value));
  DOM.runDemoBtn.addEventListener("click", runDemo);
  DOM.clearResultsBtn.addEventListener("click", clearResults);
}

function applyPreset(presetId) {
  const preset = PRESETS[presetId];
  if (!preset) {
    return;
  }
  DOM.proposalJson.value = pretty(preset.proposal);
  DOM.simulationJson.value = pretty(preset.simulation);
  DOM.policyJson.value = preset.policy ? pretty(preset.policy) : "";
  DOM.runMessage.textContent = `Preset loaded: ${preset.label}`;
}

function clearResults() {
  currentStepState = STEP_NAMES.map((name) => ({ name, status: "pending" }));
  renderStepStrip();
  renderGate({ outcome: "unknown", label: "Not run yet", detail: "", approvalStatus: "not_required" });
  DOM.simulationSummary.innerHTML = "";
  DOM.simulationRows.innerHTML = "";
  DOM.timeline.innerHTML = "";
  DOM.rawJson.textContent = "{}";
  DOM.runMessage.textContent = "Cleared. Ready.";
}

async function runDemo() {
  let request;
  try {
    request = readRequest();
  } catch (err) {
    DOM.runMessage.textContent = `Invalid input: ${err.message}`;
    return;
  }

  currentStepState = STEP_NAMES.map((name) => ({ name, status: "pending" }));
  renderStepStrip();

  const apiBase = DOM.apiBaseInput.value.trim();
  const token = DOM.apiTokenInput.value.trim();
  const timeline = [];

  try {
    setRunMessage("Running demo...");

    setStepStatus(0, "running");
    const session = await apiPost(apiBase, "/v1/sessions", {}, token);
    setStepStatus(0, "done");
    timelinePush(timeline, "session.created", `Session ${session.session_id} opened`);

    setStepStatus(1, "running");
    const proposalResult = await apiPost(
      apiBase,
      "/v1/proposals/submit",
      {
        session_id: session.session_id,
        proposal: request.proposal,
        policies: request.policy ? [request.policy] : [],
      },
      token,
    );
    setStepStatus(1, "done");
    const gate = normalizeGateState(proposalResult);
    renderGate(gate);
    timelinePush(timeline, "proposal.submitted", gate.label);

    setStepStatus(2, "running");
    const simulation = await apiPost(
      apiBase,
      "/v1/simulations/run",
      {
        session_id: session.session_id,
        simulation_id: request.simulation.simulation_id,
        projection_name: request.simulation.projection_name,
        hypothetical_events: request.simulation.hypothetical_events,
        scenario_name: request.simulation.scenario_name,
        assumptions: request.simulation.assumptions,
        inputs: request.simulation.inputs,
      },
      token,
    );
    setStepStatus(2, "done");
    renderSimulationDelta(simulation);
    timelinePush(
      timeline,
      "simulation.completed",
      `Applied ${simulation.hypothetical_events_applied} hypothetical event(s)`,
    );

    setStepStatus(3, "running");
    const decision = await runtimeCall(
      apiBase,
      {
        method: "decision.create",
        params: {
          session_id: session.session_id,
          proposal: request.proposal,
          policy_report: proposalResult.policy_report,
          approval_status: gate.approvalStatus,
          approval_id: proposalResult.approval ? proposalResult.approval.approval_id : null,
          approval_chain: proposalResult.approval ? proposalResult.approval.approval_chain : [],
        },
      },
      token,
    );
    setStepStatus(3, "done");
    timelinePush(timeline, "decision.created", `Decision ${decision.decision_id}: ${decision.status}`);

    setStepStatus(4, "running");
    const telemetrySummary = await apiGet(apiBase, "/v1/observability/telemetry/summary", token);
    setStepStatus(4, "done");

    setStepStatus(5, "running");
    const dashboard = await runtimeCall(apiBase, { method: "diagnostics.dashboard", params: {} }, token);
    setStepStatus(5, "done");

    setStepStatus(6, "running");
    const traceList = await runtimeCall(apiBase, { method: "trace.list", params: { limit: 30 } }, token);
    setStepStatus(6, "done");

    setStepStatus(7, "running");
    const telemetryEventsRaw = await runtimeCall(
      apiBase,
      { method: "telemetry.events", params: { since: 0, limit: 60 } },
      token,
    );
    setStepStatus(7, "done");

    setStepStatus(8, "running");
    const sessionEventsRaw = await runtimeCall(
      apiBase,
      {
        method: "task.events.subscribe",
        params: {
          session_id: session.session_id,
          since: 0,
        },
      },
      token,
    );
    setStepStatus(8, "done");

    const runResult = {
      session,
      proposalResult,
      simulationResult: simulation,
      decisionResult: decision,
      telemetrySummary,
      dashboard,
      traces: traceList.traces || [],
      telemetryEvents: telemetryEventsRaw.events || [],
      sessionEvents: sessionEventsRaw.events || [],
      timeline,
    };

    renderTimeline(buildTimeline(runResult));
    DOM.rawJson.textContent = pretty(runResult);
    setRunMessage("Run completed.");
  } catch (err) {
    failRunningStep();
    setRunMessage(`Run failed: ${err.message}`);
  }
}

function readRequest() {
  const proposal = parseJsonStrict(DOM.proposalJson.value || "{}");
  const simulation = parseJsonStrict(DOM.simulationJson.value || "{}");
  const policy = DOM.policyJson.value.trim() ? parseJsonStrict(DOM.policyJson.value) : null;

  if (!proposal.proposed_action || !proposal.proposed_action.action_type) {
    throw new Error("proposal.proposed_action.action_type is required");
  }

  if (!simulation.simulation_id || !simulation.projection_name) {
    throw new Error("simulation.simulation_id and simulation.projection_name are required");
  }

  return {
    proposal,
    simulation,
    policy,
  };
}

function parseJsonStrict(text) {
  try {
    return JSON.parse(text);
  } catch (err) {
    throw new Error(err.message);
  }
}

function normalizeGateState(proposalResult) {
  const policyReport = proposalResult.policy_report || {};
  const outcome = policyReport.final_outcome || "unknown";
  const approvalStatus = proposalResult.approval ? proposalResult.approval.status : "not_required";

  if (outcome === "deny") {
    return {
      outcome,
      label: "Denied by policy",
      detail: "Execution blocked before runtime action.",
      approvalStatus,
    };
  }

  if (policyReport.requires_approval) {
    return {
      outcome: "require_approval",
      label: "Approval required",
      detail: `Approval status: ${approvalStatus}`,
      approvalStatus,
    };
  }

  if (outcome === "warn") {
    return {
      outcome,
      label: "Allowed with warning",
      detail: "Run can continue, but policy emitted a warning.",
      approvalStatus,
    };
  }

  if (outcome === "allow") {
    return {
      outcome,
      label: "Allowed",
      detail: "No blocking policy conditions were triggered.",
      approvalStatus,
    };
  }

  return {
    outcome: "unknown",
    label: "Unknown policy state",
    detail: "Policy report did not include a recognized final outcome.",
    approvalStatus,
  };
}

function renderGate(gateState) {
  DOM.gateCard.className = `gate-card gate-${gateState.outcome.replace("_", "-")}`;
  DOM.gateCard.innerHTML = `
    <p class="gate-title">${escapeHtml(gateState.label)}</p>
    <p class="gate-detail">${escapeHtml(gateState.detail)}</p>
  `;
}

function renderSimulationDelta(simulation) {
  const summaryPairs = [
    { label: "Simulation", value: simulation.simulation_id || "-" },
    { label: "Status", value: simulation.status || "-" },
    { label: "Hypothetical Events", value: String(simulation.hypothetical_events_applied || 0) },
    { label: "Changed Paths", value: String((simulation.comparison_summary || {}).changed_path_count || 0) },
  ];

  DOM.simulationSummary.innerHTML = summaryPairs
    .map(
      (pair) => `
      <article class="kpi">
        <p class="label">${escapeHtml(pair.label)}</p>
        <p class="value">${escapeHtml(pair.value)}</p>
      </article>
    `,
    )
    .join("");

  const diff = simulation.state_diff || {};
  const rows = Object.keys(diff)
    .sort()
    .slice(0, 24)
    .map((path) => {
      const values = diff[path] || {};
      return `
        <tr>
          <td>${escapeHtml(path)}</td>
          <td>${escapeHtml(compactJson(values.base))}</td>
          <td>${escapeHtml(compactJson(values.simulated))}</td>
        </tr>
      `;
    })
    .join("");

  DOM.simulationRows.innerHTML = rows || "<tr><td colspan=\"3\">No state differences reported.</td></tr>";
}

function buildTimeline(runResult) {
  const timeline = [...runResult.timeline];
  timelinePush(
    timeline,
    "telemetry.summary",
    `Events: ${(runResult.telemetrySummary.events || {}).total || 0}, Traces: ${(runResult.telemetrySummary.traces || {}).total || 0}`,
  );

  const traces = runResult.traces.slice(0, 3);
  traces.forEach((trace) => {
    timelinePush(
      timeline,
      "trace",
      `${trace.name || "trace"} [${trace.status || "unknown"}] ${trace.duration_ms || 0}ms`,
      trace.finished_at || trace.started_at,
    );
  });

  const sessionEvents = runResult.sessionEvents.slice(0, 6);
  sessionEvents.forEach((event) => {
    timelinePush(
      timeline,
      `session.${event.type || "event"}`,
      compactJson(event.payload || {}),
      event.at,
    );
  });

  return timeline;
}

function renderTimeline(items) {
  DOM.timeline.innerHTML = items
    .map(
      (item) => `
        <li>
          <strong>${escapeHtml(item.title)}</strong>
          <span>${escapeHtml(item.description)}</span>
          <span class="meta">${escapeHtml(item.at)}</span>
        </li>
      `,
    )
    .join("");
}

function timelinePush(timeline, title, description, at) {
  timeline.push({
    title,
    description,
    at: at || new Date().toISOString(),
  });
}

function setRunMessage(message) {
  DOM.runMessage.textContent = message;
}

function setStepStatus(index, status) {
  currentStepState[index].status = status;
  renderStepStrip();
}

function failRunningStep() {
  const current = currentStepState.find((step) => step.status === "running");
  if (current) {
    current.status = "error";
    renderStepStrip();
  }
}

function renderStepStrip() {
  DOM.stepStrip.innerHTML = currentStepState
    .map(
      (step) => `<span class="step-chip ${step.status}">${escapeHtml(step.name)}: ${escapeHtml(step.status)}</span>`,
    )
    .join("");
}

async function runtimeCall(apiBase, payload, token) {
  return apiPost(apiBase, "/v1/runtime/call", payload, token);
}

async function apiGet(apiBase, path, token) {
  return apiRequest(apiBase, path, "GET", null, token);
}

async function apiPost(apiBase, path, payload, token) {
  return apiRequest(apiBase, path, "POST", payload, token);
}

async function apiRequest(apiBase, path, method, payload, token) {
  const headers = { Accept: "application/json" };
  if (payload !== null) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(joinUrl(apiBase, path), {
    method,
    headers,
    body: payload !== null ? JSON.stringify(payload) : null,
  });

  let data;
  try {
    data = await response.json();
  } catch (err) {
    throw new Error(`Non-JSON response (${response.status})`);
  }

  if (!response.ok) {
    throw new Error((data.error && data.error.message) || `HTTP ${response.status}`);
  }

  if (!data.ok) {
    throw new Error((data.error && data.error.message) || "API returned ok=false");
  }

  return data.result;
}

function joinUrl(base, path) {
  const normalizedBase = base.replace(/\/$/, "");
  return `${normalizedBase}${path}`;
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function compactJson(value) {
  return JSON.stringify(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

init();

import { deriveCompareContext } from "./mapCompareAdapter.js";

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

function normalizeMode(mode) {
  if (mode === "split" || mode === "ghost") {
    return mode;
  }
  return "delta";
}

function compareHeadline(state) {
  const baseline = state.compare.baselineBranchId || "baseline";
  const target = state.compare.targetBranchIds?.[0] || "(select target)";
  const mode = normalizeMode(state.compare.visualizationMode);
  return `${baseline} vs ${target} (${mode})`;
}

function compareSummaryPayload(state) {
  const compareContext = deriveCompareContext(state, null);
  const result = state.compare.result;
  if (!result) {
    return {
      compare: compareHeadline(state),
      summary: "Run compare to populate branch deltas and tradeoff summaries.",
    };
  }

  const tradeoffs = (result.summary?.regional_tradeoffs || []).slice(0, 6);
  const topTradeoff = tradeoffs[0] || null;
  return {
    compare: compareHeadline(state),
    hotspot_threshold: compareContext?.threshold ?? null,
    selected_hotspot: compareContext?.selectedHotspot || null,
    hotspot_regions: (compareContext?.hotspots || []).map((item) => item.regionId),
    indicator_deltas: compareContext?.indicatorDeltas || [],
    rankings: result.rankings || [],
    best_composite_score_branch: result.summary?.best_composite_score_branch || null,
    best_equity_branch: result.summary?.best_equity_branch || null,
    top_tradeoff: topTradeoff,
    tradeoff_sample: tradeoffs,
    annotation_summary_keys: Object.keys(result.annotation_summary || {}),
  };
}

function compareLegendRows(state) {
  const result = state.compare.result;
  if (!result || !Array.isArray(result.branches)) {
    return [];
  }

  return result.branches
    .slice()
    .sort((left, right) => String(left.branch_id).localeCompare(String(right.branch_id)))
    .map((branch) => ({
      branchId: branch.branch_id,
      compositeScore: Number(branch.composite_score ?? 0).toFixed(2),
      disparitySpread: Number(branch.equity?.disparity_index?.spread ?? 0).toFixed(4),
      selected:
        branch.branch_id === state.compare.baselineBranchId ||
        state.compare.targetBranchIds?.includes(branch.branch_id),
    }));
}

export function createCompareWorkspace(actions) {
  const root = document.createElement("section");
  root.className = "planning-control-group compare-workspace";
  root.innerHTML = `
    <h3>Compare Room</h3>
    <label>
      Baseline branch
      <select id="compare-baseline-select"></select>
    </label>
    <label>
      Target branch
      <select id="compare-target-select"></select>
    </label>
    <label>
      Visualization mode
      <select id="compare-mode-select">
        <option value="delta">Delta</option>
        <option value="split">Split</option>
        <option value="ghost">Ghost</option>
      </select>
    </label>
    <label>
      Hotspot threshold (gap)
      <input id="compare-hotspot-threshold" type="number" min="0" max="100" step="0.05" value="0.25" />
    </label>
    <div class="planning-button-row">
      <button type="button" id="compare-run">Run compare</button>
      <button type="button" id="compare-provenance-baseline">Baseline provenance</button>
      <button type="button" id="compare-provenance-target">Target provenance</button>
    </div>
    <p class="muted" id="compare-headline">baseline vs (select target)</p>
    <ul class="service-list" id="compare-legend"></ul>
    <p class="muted" id="compare-hotspot-context">Hotspot: none selected.</p>
    <ul class="planning-inline-list compare-hotspot-list" id="compare-hotspots"></ul>
    <pre id="compare-summary" class="planning-result-summary">{}</pre>
  `;

  const elements = {
    baseline: root.querySelector("#compare-baseline-select"),
    target: root.querySelector("#compare-target-select"),
    mode: root.querySelector("#compare-mode-select"),
    run: root.querySelector("#compare-run"),
    threshold: root.querySelector("#compare-hotspot-threshold"),
    provenanceBaseline: root.querySelector("#compare-provenance-baseline"),
    provenanceTarget: root.querySelector("#compare-provenance-target"),
    headline: root.querySelector("#compare-headline"),
    legend: root.querySelector("#compare-legend"),
    hotspotContext: root.querySelector("#compare-hotspot-context"),
    hotspots: root.querySelector("#compare-hotspots"),
    summary: root.querySelector("#compare-summary"),
  };

  elements.baseline.addEventListener("change", () => {
    actions.onSetCompareBaseline?.(elements.baseline.value || null);
  });
  elements.target.addEventListener("change", () => {
    actions.onSetCompareTarget?.(elements.target.value || null);
  });
  elements.mode.addEventListener("change", () => {
    actions.onSetCompareMode?.(normalizeMode(elements.mode.value));
  });
  elements.run.addEventListener("click", () => {
    actions.onRunCompare?.();
  });
  elements.threshold.addEventListener("change", () => {
    actions.onSetCompareThreshold?.(Number(elements.threshold.value));
  });
  elements.provenanceBaseline.addEventListener("click", () => {
    if (!elements.baseline.value) {
      return;
    }
    actions.onInspectProvenance?.("branch", elements.baseline.value, "compare baseline");
  });
  elements.provenanceTarget.addEventListener("click", () => {
    if (!elements.target.value) {
      return;
    }
    actions.onInspectProvenance?.("branch", elements.target.value, "compare target");
  });
  elements.hotspots.addEventListener("click", (event) => {
    const button = event.target.closest("[data-hotspot-region-id][data-hotspot-action]");
    if (!button) {
      return;
    }
    const regionId = button.getAttribute("data-hotspot-region-id");
    const action = button.getAttribute("data-hotspot-action");
    if (!regionId || !action) {
      return;
    }
    if (action === "focus") {
      actions.onSetCompareHotspot?.(regionId);
      return;
    }
    if (action === "provenance") {
      actions.onSetCompareHotspot?.(regionId);
      actions.onInspectProvenanceFromCompareHotspot?.(regionId);
    }
  });

  function render(state) {
    const options = branchOptions(state);
    updateSelectOptions(
      elements.baseline,
      options,
      state.compare.baselineBranchId,
      "(select baseline branch)",
    );

    const selectedBaseline = elements.baseline.value;
    const targetOptions = options.filter((option) => option.value !== selectedBaseline);
    const requestedTarget = state.compare.targetBranchIds?.[0] || null;
    updateSelectOptions(
      elements.target,
      targetOptions,
      requestedTarget,
      "(select target branch)",
    );

    const mode = normalizeMode(state.compare.visualizationMode);
    elements.mode.value = mode;
    elements.threshold.value = String(Number(state.compare.hotspotThreshold ?? 0.25).toFixed(2));
    elements.headline.textContent = compareHeadline(state);

    const compareContext = deriveCompareContext(state, null);

    elements.legend.innerHTML = "";
    const rows = compareLegendRows(state);
    if (!rows.length) {
      const item = document.createElement("li");
      item.textContent = "Legend appears after compare runs.";
      elements.legend.appendChild(item);
    } else {
      for (const row of rows) {
        const item = document.createElement("li");
        item.textContent = `${row.selected ? "*" : "-"} ${row.branchId}: score ${row.compositeScore}, spread ${row.disparitySpread}`;
        elements.legend.appendChild(item);
      }
    }

    elements.hotspots.innerHTML = "";
    if (!compareContext?.hotspots?.length) {
      const item = document.createElement("li");
      item.textContent = "Hotspots appear after compare runs.";
      elements.hotspots.appendChild(item);
      elements.hotspotContext.textContent = "Hotspot: none selected.";
    } else {
      const selectedRegionId = compareContext.selectedHotspotRegionId;
      const selected = compareContext.selectedHotspot;
      elements.hotspotContext.textContent = selected
        ? `Hotspot ${selected.regionId} · gap ${selected.gap.toFixed(4)} · confidence ${selected.confidence}`
        : "Hotspot: none selected.";
      for (const hotspot of compareContext.hotspots) {
        const item = document.createElement("li");
        item.className = "planning-queue-item";
        const selectedFlag = hotspot.regionId === selectedRegionId ? "*" : "-";
        item.innerHTML = `
          <p><strong>${selectedFlag} ${hotspot.regionId}</strong> <span class="muted">[${hotspot.severity}]</span></p>
          <p class="muted">delta ${hotspot.delta.toFixed(4)} · gap ${hotspot.gap.toFixed(4)} · confidence ${hotspot.confidence}</p>
          <div class="planning-button-row">
            <button type="button" data-hotspot-action="focus" data-hotspot-region-id="${hotspot.regionId}">Focus</button>
            <button type="button" data-hotspot-action="provenance" data-hotspot-region-id="${hotspot.regionId}">Provenance</button>
          </div>
        `;
        elements.hotspots.appendChild(item);
      }
    }

    elements.summary.textContent = JSON.stringify(compareSummaryPayload(state), null, 2);
    root.classList.toggle("is-active", state.route === "compare");
  }

  return {
    root,
    render,
  };
}

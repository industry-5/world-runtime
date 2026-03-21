function safeString(value) {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value);
}

function summarizeProvenanceResult(result) {
  if (!result) {
    return {
      summary: "Select a branch/proposal/annotation artifact and inspect provenance.",
    };
  }

  if (result.artifact) {
    const artifact = result.artifact;
    return {
      artifact_type: artifact.artifact_type,
      artifact_id: artifact.artifact_id,
      lineage: artifact.lineage || [],
      metadata: artifact.metadata || {},
      evidence_refs: artifact.evidence_refs || [],
    };
  }

  return {
    count: result.count || 0,
    artifacts: result.artifacts || [],
  };
}

export function createProvenanceDrawer(actions) {
  const root = document.createElement("section");
  root.className = "planning-control-group provenance-drawer";
  root.innerHTML = `
    <h3>Evidence and Provenance</h3>
    <label>
      Artifact type
      <select id="provenance-artifact-type">
        <option value="branch">Branch</option>
        <option value="proposal">Proposal</option>
        <option value="annotation">Annotation</option>
        <option value="scenario">Scenario</option>
      </select>
    </label>
    <label>
      Artifact id
      <input id="provenance-artifact-id" type="text" placeholder="baseline" />
    </label>
    <div class="planning-button-row">
      <button type="button" id="provenance-inspect">Inspect provenance</button>
      <button type="button" id="provenance-selection">From current context</button>
    </div>
    <p class="muted" id="provenance-context">No provenance context selected.</p>
    <pre id="provenance-summary" class="planning-result-summary">{}</pre>
  `;

  const elements = {
    artifactType: root.querySelector("#provenance-artifact-type"),
    artifactId: root.querySelector("#provenance-artifact-id"),
    inspect: root.querySelector("#provenance-inspect"),
    inspectSelection: root.querySelector("#provenance-selection"),
    context: root.querySelector("#provenance-context"),
    summary: root.querySelector("#provenance-summary"),
  };

  elements.inspect.addEventListener("click", () => {
    const artifactType = elements.artifactType.value;
    const artifactId = elements.artifactId.value.trim();
    if (!artifactType || !artifactId) {
      return;
    }
    actions.onInspectProvenance?.(artifactType, artifactId, "manual lookup");
  });

  elements.inspectSelection.addEventListener("click", () => {
    actions.onInspectProvenanceFromContext?.();
  });

  function render(state) {
    const selectedType = state.provenance.artifactType || "branch";
    elements.artifactType.value = selectedType;

    if (document.activeElement !== elements.artifactId) {
      const selectedId = state.provenance.artifactId || state.branch.activeBranchId || "";
      elements.artifactId.value = safeString(selectedId);
    }

    const contextText = state.provenance.contextLabel
      ? `Context: ${state.provenance.contextLabel}`
      : "No provenance context selected.";
    elements.context.textContent = contextText;

    const summaryPayload = summarizeProvenanceResult(state.provenance.result);
    elements.summary.textContent = JSON.stringify(summaryPayload, null, 2);
  }

  return {
    root,
    render,
  };
}

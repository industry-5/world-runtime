function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function numberOrNull(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

function frameAt(state) {
  const frames = Array.isArray(state.replay.frames) ? state.replay.frames : [];
  if (!frames.length) {
    return { frame: null, cursorIndex: 0, frameCount: 0 };
  }
  const cursor = clamp(Number(state.replay.cursorIndex ?? 0), 0, frames.length - 1);
  return {
    frame: frames[cursor],
    cursorIndex: cursor,
    frameCount: frames.length,
  };
}

function branchParentId(state, branchId) {
  if (!branchId) {
    return null;
  }
  return state.branch.branches?.[branchId]?.parent_branch_id || null;
}

function dominantValuesFromFrame(frame, dominantLayerId) {
  const layerId = dominantLayerId || "state.water_security";
  if (layerId === "state.equity_delta" || layerId === "state.equity_outcome") {
    const perRegion = frame?.equity_report?.per_region || [];
    const values = {};
    for (const entry of perRegion) {
      if (!entry?.region_id) {
        continue;
      }
      const raw = layerId === "state.equity_delta" ? entry.delta_vs_baseline : entry.normalized_outcome;
      const numeric = numberOrNull(raw);
      if (numeric !== null) {
        values[entry.region_id] = Number(numeric.toFixed(4));
      }
    }
    return values;
  }

  const stocks = frame?.network_diagnostics?.resource_stocks || [];
  const buckets = {};
  for (const stock of stocks) {
    const regionId = stock?.region_id;
    if (!regionId) {
      continue;
    }
    const current = numberOrNull(stock.current);
    if (current === null) {
      continue;
    }
    const bucket = buckets[regionId] || { total: 0, count: 0 };
    bucket.total += current;
    bucket.count += 1;
    buckets[regionId] = bucket;
  }

  const values = {};
  for (const [regionId, bucket] of Object.entries(buckets)) {
    if (!bucket.count) {
      continue;
    }
    values[regionId] = Number((bucket.total / bucket.count).toFixed(4));
  }
  return values;
}

function frameDeltaMap(previousValues, nextValues) {
  const regionIds = new Set([...Object.keys(previousValues), ...Object.keys(nextValues)]);
  const deltas = {};
  for (const regionId of regionIds) {
    const previous = numberOrNull(previousValues[regionId]) ?? 0;
    const next = numberOrNull(nextValues[regionId]) ?? 0;
    deltas[regionId] = Number((next - previous).toFixed(4));
  }
  return deltas;
}

function topChangedRegions(deltas, limit = 5) {
  return Object.entries(deltas)
    .map(([regionId, delta]) => ({
      regionId,
      delta,
      magnitude: Math.abs(Number(delta || 0)),
    }))
    .filter((item) => Number.isFinite(item.magnitude))
    .sort((left, right) => right.magnitude - left.magnitude || left.regionId.localeCompare(right.regionId))
    .slice(0, limit);
}

function buildReplayMarkers(state, frames) {
  const markers = [];
  const branchId = state.replay.branchId || state.branch.activeBranchId || null;
  const parentBranchId = branchParentId(state, branchId);

  for (let index = 0; index < frames.length; index += 1) {
    const frame = frames[index];
    const turnIndex = Number(frame?.turn_index ?? index);
    const previousFrame = index > 0 ? frames[index - 1] : null;
    const previousValues = dominantValuesFromFrame(previousFrame, state.layers.dominantLayerId);
    const nextValues = dominantValuesFromFrame(frame, state.layers.dominantLayerId);
    const deltas = frameDeltaMap(previousValues, nextValues);
    const changedRegions = topChangedRegions(deltas, 4);
    const maxDelta = changedRegions[0]?.magnitude || 0;
    const hasPolicyAlert = ["warn", "deny", "require_approval"].includes(String(frame?.policy_outcome || ""));
    const hasShock = Boolean(frame?.applied_shock_ids?.length);

    const marker = {
      id: `turn-${turnIndex}`,
      turnIndex,
      kind: "turn",
      label: `Turn ${turnIndex}`,
      checkpoint: index === 0 || hasPolicyAlert || hasShock || maxDelta >= 0.2,
      changedRegions: changedRegions.map((item) => item.regionId),
      maxDelta: Number(maxDelta.toFixed(4)),
      policyOutcome: frame?.policy_outcome || null,
      approvalStatus: frame?.approval_status || null,
      appliedInterventions: frame?.applied_intervention_ids || [],
      appliedShocks: frame?.applied_shock_ids || [],
      branchPoint: index === 0 && Boolean(parentBranchId),
      branchSource: index === 0 ? parentBranchId : null,
    };
    markers.push(marker);
  }

  return markers;
}

function valueRange(valuesMap) {
  const values = Object.values(valuesMap).filter((value) => Number.isFinite(value));
  if (!values.length) {
    return { min: null, max: null };
  }
  return {
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

export function deriveReplayContext(state) {
  if (state.route !== "replay") {
    return null;
  }

  const { frame, cursorIndex, frameCount } = frameAt(state);
  if (!frame) {
    return null;
  }

  const frames = Array.isArray(state.replay.frames) ? state.replay.frames : [];
  const markers = buildReplayMarkers(state, frames);
  const checkpoints = markers.filter((marker) => marker.checkpoint);
  const selectedCheckpointTurn =
    checkpoints.find((checkpoint) => checkpoint.turnIndex === state.replay.selectedCheckpointTurn)?.turnIndex ??
    checkpoints.find((checkpoint) => checkpoint.turnIndex === frame.turn_index)?.turnIndex ??
    checkpoints[0]?.turnIndex ??
    null;
  const selectedCheckpoint = checkpoints.find((checkpoint) => checkpoint.turnIndex === selectedCheckpointTurn) || null;

  const dominantValues = dominantValuesFromFrame(frame, state.layers.dominantLayerId);
  return {
    branchId: state.replay.branchId || state.branch.activeBranchId || null,
    cursorIndex,
    frameCount,
    frame,
    dominantValues,
    dominantScale: valueRange(dominantValues),
    networkSnapshot: frame.network_diagnostics || null,
    equityReport: frame.equity_report || null,
    markers,
    checkpoints,
    selectedCheckpointTurn,
    selectedCheckpoint,
    checkpointRegionIds: selectedCheckpoint?.changedRegions || [],
  };
}

export function deriveReplayRegionMetrics(replayContext, regionId) {
  if (!replayContext || !regionId) {
    return [];
  }

  const metrics = [];
  const stocks = replayContext.networkSnapshot?.resource_stocks || [];
  const stock = stocks.find((item) => item.region_id === regionId);
  if (stock) {
    metrics.push({
      label: `Replay Stock (turn ${replayContext.frame.turn_index ?? replayContext.cursorIndex})`,
      value: `${Number(stock.current).toFixed(2)} (${stock.indicator_id})`,
    });
  }

  const equity = (replayContext.equityReport?.per_region || []).find((item) => item.region_id === regionId);
  if (equity) {
    metrics.push({
      label: "Replay Equity Delta",
      value: Number(equity.delta_vs_baseline).toFixed(4),
    });
    metrics.push({
      label: "Replay Normalized Outcome",
      value: Number(equity.normalized_outcome).toFixed(4),
    });
  }

  return metrics;
}

function normalizeMode(mode) {
  if (mode === "split" || mode === "ghost") {
    return mode;
  }
  return "delta";
}

function hotspotThreshold(state) {
  const numeric = Number(state.compare.hotspotThreshold);
  if (!Number.isFinite(numeric)) {
    return 0.25;
  }
  return Math.max(0, Number(numeric.toFixed(4)));
}

function numberOrNull(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

function branchById(compareResult, branchId) {
  if (!compareResult || !Array.isArray(compareResult.branches) || !branchId) {
    return null;
  }
  return compareResult.branches.find((branch) => branch.branch_id === branchId) || null;
}

function perRegionOutcomeMap(branch) {
  const entries = branch?.equity?.per_region;
  if (!Array.isArray(entries)) {
    return {};
  }
  const map = {};
  for (const item of entries) {
    if (!item?.region_id) {
      continue;
    }
    const value = numberOrNull(item.normalized_outcome);
    if (value !== null) {
      map[item.region_id] = value;
    }
  }
  return map;
}

function perRegionDeltaMap(baselineMap, targetMap) {
  const regionIds = new Set([...Object.keys(baselineMap), ...Object.keys(targetMap)]);
  const deltas = {};
  for (const regionId of regionIds) {
    const baseline = numberOrNull(baselineMap[regionId]) ?? 0;
    const target = numberOrNull(targetMap[regionId]) ?? 0;
    deltas[regionId] = Number((target - baseline).toFixed(4));
  }
  return deltas;
}

function indicatorDeltaSummary(baselineBranch, targetBranch) {
  const baselineScores = baselineBranch?.indicator_scores || {};
  const targetScores = targetBranch?.indicator_scores || {};
  const indicatorIds = new Set([...Object.keys(baselineScores), ...Object.keys(targetScores)]);
  const rows = [];
  for (const indicatorId of indicatorIds) {
    const baseline = numberOrNull(baselineScores[indicatorId]) ?? 0;
    const target = numberOrNull(targetScores[indicatorId]) ?? 0;
    const delta = Number((target - baseline).toFixed(4));
    rows.push({
      indicatorId,
      baseline: Number(baseline.toFixed(4)),
      target: Number(target.toFixed(4)),
      delta,
      magnitude: Math.abs(delta),
    });
  }
  return rows
    .sort((left, right) => right.magnitude - left.magnitude || left.indicatorId.localeCompare(right.indicatorId))
    .slice(0, 6);
}

function hotspotSeverity(gap, threshold) {
  if (gap >= threshold * 2.5) {
    return "critical";
  }
  if (gap >= threshold * 1.5) {
    return "watch";
  }
  return "monitor";
}

function hotspotConfidence(delta, threshold) {
  const absolute = Math.abs(delta);
  if (absolute < threshold * 0.4) {
    return "uncertain";
  }
  if (absolute < threshold * 0.8) {
    return "moderate";
  }
  return "strong";
}

function polygonCentroidX(polygon) {
  if (!Array.isArray(polygon) || !polygon.length) {
    return 0;
  }
  const total = polygon.reduce((sum, point) => sum + Number(point?.[0] || 0), 0);
  return total / polygon.length;
}

function splitValueMap(geometryRegions, baselineMap, targetMap, splitX) {
  const values = {};
  for (const region of geometryRegions || []) {
    const regionId = region.region_id;
    if (!regionId) {
      continue;
    }
    const x = polygonCentroidX(region.polygon);
    const baseline = numberOrNull(baselineMap[regionId]);
    const target = numberOrNull(targetMap[regionId]);
    values[regionId] = x < splitX ? (baseline ?? target ?? 0) : (target ?? baseline ?? 0);
  }
  return values;
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

function selectComparePair(state) {
  const result = state.compare.result;
  if (!result || !Array.isArray(result.branches) || result.branches.length < 2) {
    return null;
  }

  const defaultBaseline = result.branches.find((branch) => branch.branch_id === "baseline")?.branch_id;
  const baselineBranchId =
    state.compare.baselineBranchId ||
    defaultBaseline ||
    result.rankings?.[0] ||
    result.branches[0].branch_id;

  let targetBranchId = state.compare.targetBranchIds?.[0] || null;
  if (!targetBranchId || targetBranchId === baselineBranchId) {
    targetBranchId = result.branches.find((branch) => branch.branch_id !== baselineBranchId)?.branch_id || null;
  }

  if (!baselineBranchId || !targetBranchId || baselineBranchId === targetBranchId) {
    return null;
  }

  return { baselineBranchId, targetBranchId };
}

export function deriveCompareContext(state, geometryPackage) {
  if (state.route !== "compare") {
    return null;
  }
  const pair = selectComparePair(state);
  if (!pair) {
    return null;
  }

  const compareResult = state.compare.result;
  const baselineBranch = branchById(compareResult, pair.baselineBranchId);
  const targetBranch = branchById(compareResult, pair.targetBranchId);
  if (!baselineBranch || !targetBranch) {
    return null;
  }

  const baselineValues = perRegionOutcomeMap(baselineBranch);
  const targetValues = perRegionOutcomeMap(targetBranch);
  const deltaValues = perRegionDeltaMap(baselineValues, targetValues);
  const mode = normalizeMode(state.compare.visualizationMode);
  const threshold = hotspotThreshold(state);

  const viewportWidth = Number(geometryPackage?.projectionMeta?.viewport?.width || 1000);
  const splitX = viewportWidth / 2;
  const regionGeometry = geometryPackage?.regions?.regions || [];

  let dominantValues = deltaValues;
  let colorMode = "diverging";
  if (mode === "split") {
    dominantValues = splitValueMap(regionGeometry, baselineValues, targetValues, splitX);
    colorMode = "sequential";
  } else if (mode === "ghost") {
    dominantValues = targetValues;
    colorMode = "sequential";
  }

  const deltaMagnitude = Object.entries(deltaValues)
    .map(([regionId, value]) => ({ regionId, value: Math.abs(Number(value || 0)) }))
    .filter((item) => Number.isFinite(item.value))
    .sort((left, right) => right.value - left.value);

  const tradeoffMap = {};
  for (const tradeoff of compareResult.summary?.regional_tradeoffs || []) {
    if (tradeoff?.region_id) {
      tradeoffMap[tradeoff.region_id] = tradeoff;
    }
  }

  const hotspotRows = deltaMagnitude.map((row) => {
    const tradeoff = tradeoffMap[row.regionId] || null;
    const baseline = numberOrNull(baselineValues[row.regionId]) ?? 0;
    const target = numberOrNull(targetValues[row.regionId]) ?? 0;
    const delta = numberOrNull(deltaValues[row.regionId]) ?? 0;
    const gap = numberOrNull(tradeoff?.gap) ?? Number(Math.abs(delta).toFixed(4));
    return {
      regionId: row.regionId,
      baseline: Number(baseline.toFixed(4)),
      target: Number(target.toFixed(4)),
      delta: Number(delta.toFixed(4)),
      gap: Number(gap.toFixed(4)),
      severity: hotspotSeverity(gap, Math.max(0.0001, threshold)),
      confidence: hotspotConfidence(delta, Math.max(0.0001, threshold)),
      bestBranchId: tradeoff?.best_branch_id || null,
      worstBranchId: tradeoff?.worst_branch_id || null,
    };
  });

  const thresholdHotspots = hotspotRows.filter((row) => row.gap >= threshold);
  const filteredHotspots = (thresholdHotspots.length ? thresholdHotspots : hotspotRows).slice(0, 8);
  const selectedHotspotRegionId =
    filteredHotspots.find((item) => item.regionId === state.compare.selectedHotspotRegionId)?.regionId ||
    filteredHotspots[0]?.regionId ||
    null;
  const selectedHotspot = filteredHotspots.find((row) => row.regionId === selectedHotspotRegionId) || null;
  const indicatorDeltas = indicatorDeltaSummary(baselineBranch, targetBranch);

  return {
    mode,
    baselineBranchId: pair.baselineBranchId,
    targetBranchId: pair.targetBranchId,
    baselineValues,
    targetValues,
    deltaValues,
    dominantValues,
    dominantScale: valueRange(dominantValues),
    colorMode,
    ghostRegionIds: deltaMagnitude.filter((item) => item.value >= 0.0001).map((item) => item.regionId),
    topDeltaRegionIds: filteredHotspots.map((item) => item.regionId),
    threshold,
    hotspots: filteredHotspots,
    selectedHotspotRegionId,
    selectedHotspot,
    indicatorDeltas,
    topTradeoffs: compareResult.summary?.regional_tradeoffs || [],
  };
}

export function deriveCompareRegionMetrics(compareContext, regionId) {
  if (!compareContext || !regionId) {
    return [];
  }

  const baseline = numberOrNull(compareContext.baselineValues[regionId]);
  const target = numberOrNull(compareContext.targetValues[regionId]);
  const delta = numberOrNull(compareContext.deltaValues[regionId]);

  const metrics = [];
  if (baseline !== null) {
    metrics.push({ label: `Baseline (${compareContext.baselineBranchId})`, value: baseline.toFixed(4) });
  }
  if (target !== null) {
    metrics.push({ label: `Target (${compareContext.targetBranchId})`, value: target.toFixed(4) });
  }
  if (delta !== null) {
    metrics.push({ label: "Delta", value: delta.toFixed(4) });
  }
  return metrics;
}

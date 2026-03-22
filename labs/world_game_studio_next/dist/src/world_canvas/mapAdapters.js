import { deriveCompareContext, deriveCompareRegionMetrics } from "../compare/mapCompareAdapter.js";
import { deriveReplayContext, deriveReplayRegionMetrics } from "../replay/mapReplayAdapter.js";

export const WORLD_CANVAS_LAYER_DEFINITIONS = [
  { id: "base.boundaries", label: "Boundaries", alwaysVisible: true },
  { id: "base.labels", label: "Labels", alwaysVisible: true },
  { id: "flow.resource", label: "Resource Flows", alwaysVisible: false },
  { id: "interaction.selection", label: "Selection Overlay", alwaysVisible: true },
  { id: "interaction.proposal_preview", label: "Proposal Preview", alwaysVisible: true },
  { id: "analysis.compare_highlights", label: "Compare Highlights", alwaysVisible: false },
  { id: "analysis.replay_checkpoints", label: "Replay Checkpoints", alwaysVisible: false },
  { id: "evidence.annotation_badges", label: "Annotation Badges", alwaysVisible: false },
];

export const DOMINANT_REGION_LAYER_OPTIONS = [
  { id: "state.water_security", label: "Water Security (stock current)" },
  { id: "state.equity_delta", label: "Equity Delta vs Baseline" },
  { id: "state.equity_outcome", label: "Equity Normalized Outcome" },
];

export function createDefaultLayerState() {
  return {
    visibleLayerIds: [
      "base.boundaries",
      "base.labels",
      "interaction.selection",
      "interaction.proposal_preview",
    ],
    dominantLayerId: "state.water_security",
    manifest: {
      availableLayerIds: [
        ...WORLD_CANVAS_LAYER_DEFINITIONS.map((layer) => layer.id),
        ...DOMINANT_REGION_LAYER_OPTIONS.map((layer) => layer.id),
      ],
      defaultDominantLayerId: "state.water_security",
    },
  };
}

function indexNodesById(networkSnapshot) {
  const map = {};
  const nodes = networkSnapshot?.dependency_graph?.nodes || [];
  for (const node of nodes) {
    map[node.node_id] = node;
  }
  return map;
}

function collectWaterStockValues(networkSnapshot) {
  const valuesByRegionId = {};
  const stocks = networkSnapshot?.resource_stocks || [];
  for (const stock of stocks) {
    const regionId = stock.region_id;
    if (!regionId) {
      continue;
    }
    const current = Number(stock.current);
    if (!Number.isFinite(current)) {
      continue;
    }
    const entry = valuesByRegionId[regionId] || { total: 0, count: 0 };
    entry.total += current;
    entry.count += 1;
    valuesByRegionId[regionId] = entry;
  }

  return Object.fromEntries(
    Object.entries(valuesByRegionId).map(([regionId, entry]) => [regionId, Number((entry.total / entry.count).toFixed(4))]),
  );
}

function collectEquityValuesFromReport(equityReport, mode) {
  const perRegion = equityReport?.per_region;
  if (!Array.isArray(perRegion)) {
    return {};
  }
  const values = {};
  for (const item of perRegion) {
    if (!item?.region_id) {
      continue;
    }
    const raw = mode === "state.equity_delta" ? item.delta_vs_baseline : item.normalized_outcome;
    const numeric = Number(raw);
    if (Number.isFinite(numeric)) {
      values[item.region_id] = Number(numeric.toFixed(4));
    }
  }
  return values;
}

function dominantLayerValuesFromPlanning(state, networkSnapshot) {
  const layerId = state.layers.dominantLayerId || "state.water_security";
  if (layerId === "state.equity_delta" || layerId === "state.equity_outcome") {
    const latestEquity = state.planning.lastTurnResult?.turn_result?.equity_report || null;
    return collectEquityValuesFromReport(latestEquity, layerId);
  }
  return collectWaterStockValues(networkSnapshot);
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

function indexFlowAnchors(geometry) {
  const byEdgeId = {};
  const byRegionPair = {};
  const flows = geometry?.flowAnchors?.flows || [];
  for (const flow of flows) {
    if (flow.edge_id) {
      byEdgeId[flow.edge_id] = flow;
    }
    if (flow.from_region_id && flow.to_region_id) {
      byRegionPair[`${flow.from_region_id}::${flow.to_region_id}`] = flow;
    }
  }
  return { byEdgeId, byRegionPair };
}

function resolveFlowAnchor(flow, nodesById, anchorIndex) {
  if (flow.edge_id && anchorIndex.byEdgeId[flow.edge_id]) {
    return anchorIndex.byEdgeId[flow.edge_id];
  }
  const fromRegionId = nodesById[flow.from_node_id]?.region_id;
  const toRegionId = nodesById[flow.to_node_id]?.region_id;
  if (!fromRegionId || !toRegionId) {
    return null;
  }
  return anchorIndex.byRegionPair[`${fromRegionId}::${toRegionId}`] || null;
}

function collectFlowLines(networkSnapshot, geometry) {
  const flowRecords = networkSnapshot?.resource_flows || [];
  if (!flowRecords.length) {
    return [];
  }

  const nodesById = indexNodesById(networkSnapshot);
  const anchorIndex = indexFlowAnchors(geometry);

  const lines = [];
  for (const flow of flowRecords) {
    const anchor = resolveFlowAnchor(flow, nodesById, anchorIndex);
    if (!anchor || !Array.isArray(anchor.path)) {
      continue;
    }
    const transfer = Number(flow.last_delivered || flow.last_transfer || 0);
    const capacity = Number(flow.capacity || 0);
    lines.push({
      flowId: flow.flow_id,
      edgeId: flow.edge_id,
      path: anchor.path,
      fromRegionId: anchor.from_region_id,
      toRegionId: anchor.to_region_id,
      transfer: Number.isFinite(transfer) ? transfer : 0,
      capacity: Number.isFinite(capacity) ? capacity : 0,
    });
  }
  return lines;
}

function collectAnnotationCounts(annotations) {
  const counts = {};
  for (const annotation of annotations || []) {
    if (annotation.target_type !== "region") {
      continue;
    }
    const regionId = annotation.target_id;
    if (!regionId) {
      continue;
    }
    counts[regionId] = (counts[regionId] || 0) + 1;
  }
  return counts;
}

function dominantSurface(state, geometryPackage, compareContext, replayContext, networkSnapshot) {
  if (replayContext) {
    return {
      dominantValues: replayContext.dominantValues,
      dominantScale: replayContext.dominantScale,
      dominantColorMode: state.layers.dominantLayerId === "state.equity_delta" ? "diverging" : "sequential",
    };
  }

  if (compareContext) {
    return {
      dominantValues: compareContext.dominantValues,
      dominantScale: compareContext.dominantScale,
      dominantColorMode: compareContext.colorMode,
    };
  }

  const dominantValues = dominantLayerValuesFromPlanning(state, networkSnapshot);
  return {
    dominantValues,
    dominantScale: valueRange(dominantValues),
    dominantColorMode: "sequential",
  };
}

export function deriveCanvasModel(state, geometryPackage) {
  const replayContext = deriveReplayContext(state);
  const compareContext = deriveCompareContext(state, geometryPackage);

  const activeNetworkSnapshot = replayContext?.networkSnapshot || state.planning.networkSnapshot;
  const dominant = dominantSurface(state, geometryPackage, compareContext, replayContext, activeNetworkSnapshot);

  return {
    geometry: {
      projectionMeta: geometryPackage.projectionMeta,
      faces: geometryPackage.faces.faces || [],
      landPolygons: geometryPackage.land.land_polygons || [],
      regions: geometryPackage.regions.regions || [],
      labels: geometryPackage.labels.labels || [],
    },
    flowLines: collectFlowLines(activeNetworkSnapshot, geometryPackage),
    dominantValues: dominant.dominantValues,
    dominantLayerId: state.layers.dominantLayerId,
    dominantScale: dominant.dominantScale,
    dominantColorMode: dominant.dominantColorMode,
    visibleLayerIds: state.layers.visibleLayerIds || [],
    selectedRegionId: state.selection.regionId,
    hoveredRegionId: state.selection.hoverRegionId,
    proposalRegionIds: state.selection.proposalRegionIds || [],
    annotationCounts: collectAnnotationCounts(state.planning.annotations),
    viewport: state.canvas.viewport,
    compareOverlay: compareContext,
    replayOverlay: replayContext,
    spotlightRegionId: state.facilitation?.spotlightRegionId || null,
    presentationMode: Boolean(state.facilitation?.presentationMode),
    route: state.route,
  };
}

export function deriveRegionInspector(state, regionId) {
  if (!regionId) {
    return [];
  }

  const metrics = [];
  const replayContext = deriveReplayContext(state);
  if (replayContext) {
    metrics.push(...deriveReplayRegionMetrics(replayContext, regionId));
  }

  const compareContext = deriveCompareContext(state, null);
  if (compareContext) {
    metrics.push(...deriveCompareRegionMetrics(compareContext, regionId));
    const hotspot = (compareContext.hotspots || []).find((item) => item.regionId === regionId);
    if (hotspot) {
      metrics.push({
        label: "Compare Hotspot Gap",
        value: hotspot.gap.toFixed(4),
      });
      metrics.push({
        label: "Hotspot Confidence",
        value: hotspot.confidence,
      });
    }
  }

  if (!replayContext && !compareContext) {
    const stock = (state.planning.networkSnapshot?.resource_stocks || []).find((item) => item.region_id === regionId);
    if (stock) {
      metrics.push({
        label: "Water Stock",
        value: `${Number(stock.current).toFixed(2)} (${stock.indicator_id})`,
      });
    }

    const equity = (state.planning.lastTurnResult?.turn_result?.equity_report?.per_region || []).find(
      (item) => item.region_id === regionId,
    );
    if (equity) {
      metrics.push({
        label: "Equity Delta",
        value: Number(equity.delta_vs_baseline).toFixed(4),
      });
      metrics.push({
        label: "Normalized Outcome",
        value: Number(equity.normalized_outcome).toFixed(4),
      });
    }
  }

  const annotationCount = (state.planning.annotations || []).filter(
    (item) => item.target_type === "region" && item.target_id === regionId,
  ).length;
  metrics.push({
    label: "Annotations",
    value: String(annotationCount),
  });

  return metrics;
}

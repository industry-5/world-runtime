export type StudioMode = "plan" | "simulate" | "compare" | "replay" | "facilitate";

export type RuntimeMethodName =
  | "world_game.scenario.list"
  | "world_game.scenario.load"
  | "world_game.turn.run"
  | "world_game.branch.compare"
  | "world_game.replay.run"
  | "world_game.network.inspect"
  | "world_game.equity.report"
  | "world_game.annotation.list"
  | "world_game.provenance.inspect";

export type LayerId = string;
export type RegionId = string;
export type BranchId = string;

export type CanvasViewport = {
  zoom: number;
  x: number;
  y: number;
};

export type CanvasRenderState = {
  scenarioId: string;
  branchId: BranchId;
  compareBranchId?: BranchId;
  turnIndex?: number;
  replayCursor?: number;
  mode: StudioMode;
  selectedRegionId?: RegionId;
  selectedProposalId?: string;
  visibleLayers: LayerId[];
  viewport: CanvasViewport;
};

export type LayerFamily =
  | "base"
  | "state"
  | "flow"
  | "intervention"
  | "analysis"
  | "evidence";

export type LayerGeometryKind =
  | "region-fill"
  | "region-outline"
  | "point"
  | "line"
  | "arc"
  | "label"
  | "badge"
  | "raster"
  | "composite";

export type LayerTimeMode = "static" | "turn-indexed" | "time-series" | "event-driven";

export type LayerCompareMode =
  | "not-supported"
  | "branch-delta"
  | "baseline-delta"
  | "multi-branch"
  | "before-after";

export type LayerDataSourceDefinition = {
  sourceType:
    | "scenario-static"
    | "scenario-derived"
    | "runtime-state"
    | "runtime-derived"
    | "proposal-preview"
    | "annotation-store"
    | "provenance-store";
  entityType: "region" | "edge" | "event" | "proposal" | "annotation" | "hybrid";
  valueSchema: unknown;
  unit?: string;
  aggregationMethod?: "none" | "sum" | "mean" | "weighted-mean" | "index" | "score";
  missingValueBehavior: "hide" | "show-unknown" | "fallback-zero" | "interpolate";
};

export type LayerRenderSpec = {
  zIndexGroup: "background" | "base" | "state" | "flow" | "analysis" | "annotations" | "interaction";
  opacityRange?: [number, number];
  blendMode?: "normal" | "multiply" | "screen" | "overlay";
  colorRole?: string;
  strokeRole?: string;
  symbolRole?: string;
  labelStrategy?: "always" | "zoom-sensitive" | "selection-only" | "decluttered";
  animationStrategy?: "none" | "pulse" | "flow" | "step-transition" | "scrub-linked";
};

export type LayerDefinition = {
  id: LayerId;
  family: LayerFamily;
  title: string;
  shortTitle?: string;
  description: string;
  geometryKind: LayerGeometryKind;
  timeMode: LayerTimeMode;
  compareMode: LayerCompareMode;
  defaultVisibility: boolean;
  defaultOpacity: number;
  legendKind: "categorical" | "sequential" | "diverging" | "binary" | "none";
  inspectorEnabled: boolean;
  filterSchema?: unknown;
  supportsRegionSelection: boolean;
  supportsBranchComparison: boolean;
  supportsReplay: boolean;
  supportsProposalPreview: boolean;
  dataSource: LayerDataSourceDefinition;
  renderSpec: LayerRenderSpec;
};

export type ScenarioLayerManifest = {
  defaultDominantLayerId?: LayerId;
  availableLayerIds: LayerId[];
  hiddenByDefaultLayerIds?: LayerId[];
  compareRecommendedLayerIds?: LayerId[];
  replayRecommendedLayerIds?: LayerId[];
  layerPresets?: Array<{
    id: string;
    title: string;
    layerIds: LayerId[];
    dominantLayerId?: LayerId;
  }>;
};

export type LayerProvenance = {
  sourceRefs: string[];
  sourceKind: "scenario-input" | "simulation-output" | "user-proposal" | "annotation" | "external-import";
  generatedAt?: string;
  branchId?: string;
  turnIndex?: number;
  confidence?: number | null;
};

export type RegionLayerDatum = {
  regionId: RegionId;
  value?: number | string | boolean | null;
  normalizedValue?: number | null;
  category?: string | null;
  confidence?: number | null;
  turnIndex?: number;
  branchId?: BranchId;
  baselineValue?: number | null;
  deltaValue?: number | null;
  sourceRefs?: string[];
  noteCount?: number;
  statusFlags?: string[];
  provenance?: LayerProvenance;
};

export type EdgeLayerDatum = {
  edgeId: string;
  fromRegionId: RegionId;
  toRegionId: RegionId;
  value: number;
  normalizedValue?: number | null;
  category?: string | null;
  confidence?: number | null;
  turnIndex?: number;
  branchId?: BranchId;
  deltaValue?: number | null;
  directionality?: "one-way" | "two-way";
  routeHint?: string;
  sourceRefs?: string[];
  statusFlags?: string[];
  provenance?: LayerProvenance;
};

export type AnnotationLayerDatum = {
  id: string;
  anchorType: "region" | "edge" | "canvas";
  regionId?: RegionId;
  edgeId?: string;
  turnIndex?: number;
  branchId?: BranchId;
  category: "annotation" | "evidence" | "assumption" | "warning" | "decision" | "scenario-event";
  title: string;
  summary?: string;
  provenanceRefIds?: string[];
  authorActorId?: string;
  severity?: "info" | "warn" | "critical";
  resolved?: boolean;
};

export type TopologyRegionKind = "land" | "ocean" | "polar" | "hybrid";

export type TopologyRegionDefinition = {
  regionId: RegionId;
  label: string;
  macroRegionId: string;
  kind: TopologyRegionKind;
  status: "active" | "deprecated" | "draft";
  centroid?: { lon: number; lat: number };
  labelAnchor?: { lon: number; lat: number };
};

export type TopologyAdjacencyType = "land" | "maritime" | "polar" | "dymaxion_seam" | "hybrid";

export type TopologyAdjacency = {
  fromRegionId: RegionId;
  toRegionId: RegionId;
  type: TopologyAdjacencyType;
  weight?: number;
  bidirectional: boolean;
  notes?: string;
};

export type GeometryPackageRef = {
  packageId: string;
  version: string;
  basePath: string;
  files: {
    faces: string;
    land: string;
    regions: string;
    regionLabels: string;
    flowAnchors: string;
    projectionMeta: string;
  };
};

export type TopologyBinding = {
  topologyId: string;
  topologyVersion: string;
  scenarioId: string;
  regions: TopologyRegionDefinition[];
  adjacency: TopologyAdjacency[];
};

export type WorldGameScenarioLoadResponse = {
  session_id: string;
  scenario_id: string;
  label: string;
  description: string;
  regions: RegionId[];
  intervention_ids: string[];
  shock_ids: string[];
  branch: {
    branch_id: BranchId;
    parent_branch_id?: BranchId | null;
    turn: number;
    composite_score: number;
    equity_trend_vs_baseline: number;
    disparity_spread: number;
    event_count: number;
  };
  network_summary?: Record<string, unknown>;
  equity_summary?: Record<string, unknown>;
};

export type WorldGameTurnRunResponse = {
  session_id: string;
  scenario_id: string;
  branch_id: BranchId;
  turn_result: {
    turn_index: number;
    policy_outcome: string;
    approval_status: string;
    applied_intervention_ids: string[];
    applied_shock_ids: string[];
    scorecard: Record<string, unknown>;
    network_diagnostics: Record<string, unknown>;
    equity_report: Record<string, unknown>;
    committed: boolean;
  };
  policy_report?: Record<string, unknown> | null;
  branch: Record<string, unknown>;
  timeline_event: Record<string, unknown>;
};

export type WorldGameBranchCompareResponse = {
  comparison_id: string;
  scenario_id: string;
  branches: Array<Record<string, unknown>>;
  rankings: string[];
  summary: Record<string, unknown>;
  annotation_summary?: Record<string, Array<Record<string, unknown>>>;
};

export type WorldGameReplayRunResponse = {
  session_id: string;
  scenario_id: string;
  branch_id: BranchId;
  replay_turn_count: number;
  live_composite_score: number;
  replay_composite_score: number;
  replay_matches_live: boolean;
};

export type WorldGameNetworkInspectResponse = {
  scenario_id: string;
  branch_id: BranchId;
  turn: number;
  dependency_graph: Record<string, unknown>;
  resource_stocks: Array<Record<string, unknown>>;
  resource_flows: Array<Record<string, unknown>>;
  spillover_rules: Array<Record<string, unknown>>;
  latest_turn_diagnostics: Record<string, unknown>;
};

export type WorldGameEquityReportResponse =
  | {
      session_id: string;
      scenario_id: string;
      branch_id: BranchId;
      turn: number;
      equity_report: Record<string, unknown>;
    }
  | {
      session_id: string;
      scenario_id: string;
      reports: Array<{
        branch_id: BranchId;
        turn: number;
        equity_report: Record<string, unknown>;
      }>;
      count: number;
    };

export type WorldGameAnnotationListResponse = {
  session_id: string;
  annotations: Array<Record<string, unknown>>;
  count: number;
};

export type WorldGameProvenanceInspectResponse = {
  session_id: string;
  artifact?: Record<string, unknown>;
  artifacts?: Array<Record<string, unknown>>;
  count?: number;
};

export type ScenarioRenderSeed = {
  scenarioId: string;
  availableBranchIds: BranchId[];
  topologyBinding: TopologyBinding;
  geometry: GeometryPackageRef;
  defaultLayerManifest: ScenarioLayerManifest;
};

export type BranchLayerData = {
  branchId: BranchId;
  turnIndex: number;
  regionData: RegionLayerDatum[];
  flowData: EdgeLayerDatum[];
  replayEvents: AnnotationLayerDatum[];
};

export type CompareLayerData = {
  baseBranchId: BranchId;
  compareBranchId: BranchId;
  deltaRegionData: RegionLayerDatum[];
  deltaFlowData?: EdgeLayerDatum[];
};

export interface MapGeometryAdapter {
  loadGeometry(topologyId: string, version: string): Promise<GeometryPackageRef>;
  resolveRegionPath(regionId: RegionId): string;
}

export interface MapScenarioAdapter {
  fromScenarioLoad(payload: WorldGameScenarioLoadResponse): ScenarioRenderSeed;
  resolveLayerManifest(scenarioId: string): ScenarioLayerManifest;
}

export interface MapBranchAdapter {
  fromTurnRun(payload: WorldGameTurnRunResponse): BranchLayerData;
  fromNetworkInspect(payload: WorldGameNetworkInspectResponse): BranchLayerData;
  fromEquityReport(payload: WorldGameEquityReportResponse): BranchLayerData;
}

export interface MapCompareAdapter {
  fromBranchCompare(payload: WorldGameBranchCompareResponse): CompareLayerData;
}

export interface MapReplayAdapter {
  fromReplayRun(payload: WorldGameReplayRunResponse): {
    replayTurnCount: number;
    replayMatchesLive: boolean;
  };
}

export interface MapAnnotationAdapter {
  fromAnnotationList(payload: WorldGameAnnotationListResponse): AnnotationLayerDatum[];
  fromProvenance(payload: WorldGameProvenanceInspectResponse): AnnotationLayerDatum[];
}

export type MapAdapterRegistry = {
  mapGeometryAdapter: MapGeometryAdapter;
  mapScenarioAdapter: MapScenarioAdapter;
  mapBranchAdapter: MapBranchAdapter;
  mapCompareAdapter: MapCompareAdapter;
  mapReplayAdapter: MapReplayAdapter;
  mapAnnotationAdapter: MapAnnotationAdapter;
};

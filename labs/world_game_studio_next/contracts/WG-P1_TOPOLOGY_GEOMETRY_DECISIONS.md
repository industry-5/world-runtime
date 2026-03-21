# WG-P1 Topology And Geometry Decisions

Status: Accepted for WG-P1 (contract freeze)

## Repo-Truth First Notes

- `adapters/world_game` currently treats `scenario.regions[].region_id` as the authoritative region identifier.
- There is no runtime method yet for a global semantic topology catalog.
- Mirrored scratch docs recommend dot-scoped region IDs and a 64-region MVP; current repo scenarios use scenario-local snake_case IDs.
- WG-P1 locks contracts around current repo truth and records additive follow-ons instead of inventing unsupported runtime behavior.

## Decision 1: Semantic Topology Asset Placement

Canonical placement:

- `adapters/world_game/topology/`

Why:

- Keeps semantic region identity close to the domain source of truth.
- Prevents studio-only copies of semantic IDs, adjacency, and macro grouping.
- Supports future runtime delivery of topology metadata without relocating assets.

## Decision 2: Dymaxion Geometry Package Shape

Canonical placement:

- `labs/world_game_studio_next/assets/world_game_map/<version>/`

WG-P1 package shape (file names locked, data can evolve):

- `dymaxion_faces.json`
- `dymaxion_land.json`
- `dymaxion_regions.json`
- `dymaxion_region_labels.json`
- `dymaxion_flow_anchors.json`
- `dymaxion_projection_meta.json`

Why:

- Geometry and semantic topology are split by concern.
- Studio owns render geometry and hit polygons.
- Domain owns semantic region identity and adjacency contracts.

## Decision 3: Canonical Region Identity For WG-P1

WG-P1 canonical rule:

- The canonical region key consumed by the studio is `scenario.regions[].region_id`.
- Semantic topology binding files in `adapters/world_game/topology/scenario_bindings/` map scenario IDs to macro regions, kinds, and adjacency metadata.

Implication:

- Studio can proceed without waiting for global region-ID migration.
- Future global region namespace migration is additive and must include mapping compatibility.

## Decision 4: Adjacency Strategy

WG-P1 adjacency contract:

- Adjacency is explicit data, not inferred from frontend polygons.
- `bidirectional: true` is the default for planning adjacency in seed bindings.
- `type` values are constrained to:
  - `land`
  - `maritime`
  - `polar`
  - `dymaxion_seam`
  - `hybrid`

## Decision 5: Layer And Adapter Boundary Contract

WG-P1 contract file:

- `labs/world_game_studio_next/contracts/map_contracts.ts`

Contains:

- `CanvasRenderState`
- `LayerDefinition`
- `ScenarioLayerManifest`
- layer datum types for region, flow, annotation, provenance
- adapter seams:
  - `mapGeometryAdapter`
  - `mapScenarioAdapter`
  - `mapBranchAdapter`
  - `mapCompareAdapter`
  - `mapReplayAdapter`
  - `mapAnnotationAdapter`

## Required Additive Runtime/Domain Follow-Ons (Explicit)

1. Add a topology delivery surface (`world_game.topology.*` or scenario-load topology references) so the studio does not read topology files directly forever.
2. Extend replay runtime data for visual replay (`world_game.replay.run` currently returns parity summary, not render frames).
3. Add richer compare payloads for per-region/per-indicator deltas when non-equity state-layer compare is required.
4. Optionally expose per-turn network diagnostics history in a runtime call (today `world_game.network.inspect` is latest-turn oriented).

## Legacy Studio Posture

- `labs/world_game_studio` is intentionally untouched in WG-P1.
- WG-P1 artifacts are contract-only and live in `world_game_studio_next` plus additive domain topology docs.

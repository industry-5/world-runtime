# WG-P1 Topology And Layer Contract Checklist

Status: WG-P1 completion checklist

## Topology Contract Invariants

- [x] semantic topology placement is `adapters/world_game/topology/`
- [x] geometry package placement is `labs/world_game_studio_next/assets/world_game_map/<version>/`
- [x] scenario-facing canonical region key is `scenario.regions[].region_id`
- [x] adjacency entries are explicit and typed (`land`, `maritime`, `polar`, `dymaxion_seam`, `hybrid`)
- [x] topology bindings and geometry package references include explicit version IDs

## Layer Contract Invariants

- [x] `CanvasRenderState` is defined
- [x] `LayerDefinition` and supporting source/render specs are typed
- [x] `ScenarioLayerManifest` is typed
- [x] adapter boundaries are defined (`mapGeometryAdapter`, `mapScenarioAdapter`, `mapBranchAdapter`, `mapCompareAdapter`, `mapReplayAdapter`, `mapAnnotationAdapter`)

## Runtime Mapping Coverage

- [x] scenario mapping defined (`world_game.scenario.load`)
- [x] branch/turn mapping defined (`world_game.turn.run`)
- [x] compare mapping defined (`world_game.branch.compare`)
- [x] replay mapping defined (`world_game.replay.run`)
- [x] network mapping defined (`world_game.network.inspect`)
- [x] equity mapping defined (`world_game.equity.report`)
- [x] annotation mapping defined (`world_game.annotation.list`)
- [x] provenance mapping defined (`world_game.provenance.inspect`)

## Explicit Follow-Ons

- [x] topology transport runtime surface follow-on captured
- [x] replay frame payload follow-on captured
- [x] richer compare delta payload follow-on captured

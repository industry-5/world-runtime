# World Game Map Geometry Package v1

Status: WG-P1 package shape lock (contract only)

This directory is reserved for Dymaxion render geometry artifacts consumed by `world_game_studio_next`.

WG-P1 locks file names and package location only.

Expected files:

- `dymaxion_faces.json`
- `dymaxion_land.json`
- `dymaxion_regions.json`
- `dymaxion_region_labels.json`
- `dymaxion_flow_anchors.json`
- `dymaxion_projection_meta.json`

Rules:

- semantic region identity remains in `adapters/world_game/topology/`
- geometry files can evolve without changing semantic IDs
- version bumps are required when geometry file schema changes

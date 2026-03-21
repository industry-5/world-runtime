# World Game Topology Contracts

Status: WG-P1 semantic topology contract seed

This directory is the semantic topology source-of-truth location for World Game.

## Purpose

- define semantic region identity independent of frontend geometry
- define adjacency metadata used by studio layer adapters
- bind scenario region IDs to semantic topology metadata

## WG-P1 Scope

WG-P1 adds contract artifacts only:

- `topology.contract.v1.json`
- `scenario_bindings/world-game-multi-region.binding.v1.json`

No runtime behavior is changed in WG-P1.

## Contract Split

- semantic topology: `adapters/world_game/topology/`
- Dymaxion render geometry: `labs/world_game_studio_next/assets/world_game_map/`

## Follow-On

Additive runtime transport of topology metadata is deferred to a later milestone.

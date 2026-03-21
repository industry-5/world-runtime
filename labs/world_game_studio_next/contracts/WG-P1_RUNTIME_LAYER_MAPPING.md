# WG-P1 Runtime To Layer Mapping

Status: Accepted for WG-P1

This document locks how runtime payloads map into the `map_*Adapter` boundaries defined in `map_contracts.ts`.

## Mapping Table

| Runtime method | Primary payload fields | Studio adapter | Layer family outputs |
| --- | --- | --- | --- |
| `world_game.scenario.load` | `scenario_id`, `regions`, `branch`, `network_summary`, `equity_summary` | `mapScenarioAdapter` | base topology context, initial state-layer seed, default manifest selection |
| `world_game.turn.run` | `turn_result.scorecard`, `turn_result.network_diagnostics`, `turn_result.equity_report`, `timeline_event` | `mapBranchAdapter` | state, flow, analysis, replay event markers |
| `world_game.branch.compare` | `branches[]`, `rankings`, `summary.regional_tradeoffs` | `mapCompareAdapter` | compare delta layers and compare inspector summaries |
| `world_game.replay.run` | `replay_turn_count`, `replay_matches_live`, scores | `mapReplayAdapter` | replay control state only (not full replay frame rendering yet) |
| `world_game.network.inspect` | `dependency_graph`, `resource_flows`, `resource_stocks`, `latest_turn_diagnostics` | `mapBranchAdapter` | flow layers, edge diagnostics overlays, network inspector details |
| `world_game.equity.report` | `equity_report` or `reports[]` | `mapBranchAdapter` | equity/disparity state and analysis layers |
| `world_game.annotation.list` | `annotations[]` | `mapAnnotationAdapter` | annotation and evidence overlays |
| `world_game.provenance.inspect` | `artifact` or `artifacts[]` | `mapAnnotationAdapter` | provenance markers and inspector lineage cards |

## Contract Rules

1. Studio adapters are shape-normalizers only; no simulation, scoring, policy, or branch semantics in frontend code.
2. Runtime payload IDs pass through unchanged (`region_id`, `branch_id`, `proposal_id`, `annotation_id`).
3. Layer derivation must be deterministic for identical input payloads.
4. Compare and replay modes may hide unsupported layer combinations rather than inventing client-only approximations.

## Known Contract Gaps (Follow-Ons)

1. Full replay frame binding is blocked by limited `world_game.replay.run` payload details.
2. General indicator compare deltas by region are not fully represented in `world_game.branch.compare` today.
3. Topology catalog transport is file-based contract in WG-P1; runtime transport surface remains follow-on work.

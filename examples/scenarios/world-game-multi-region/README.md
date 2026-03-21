# world-game-multi-region

- Premise: three-region planning scenario with shared power/logistics dependency and non-local spillovers.
- Regions: coastal_import_hub, upstream_water_basin, manufacturing_belt.
- Indicators: electricity_access, water_security, food_resilience, emissions_intensity, equity_score, logistics_reliability.
- Phase 2 network model: DAG dependency graph + shared water stocks/flows + explicit spillover coefficients + equity dimensions.
- Policy pack: `adapters/world_game/policies/world_game_policy_pack.json`.
- Strategic tension: centralized gains can create upstream water and equity harms; branch comparison is required to evaluate tradeoffs.

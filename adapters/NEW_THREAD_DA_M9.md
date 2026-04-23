# DA-M9 - Promotion hardening and public-export readiness

## Objective

Run the final public adapter audit across package docs, root rollups, `docs/what-you-can-build.*`, validation surfaces, and public-export wording so the public portfolio is ready for downstream promotion.

## In Scope

- package-local hardening passes where docs, scenario artifacts, playbooks, or validation coverage still need promotion-ready polish
- root/docs rollup updates required to describe the now-implemented full public portfolio truthfully and concisely
- public-export wording alignment so the export rewrite text matches the on-repo public story

## Out Of Scope

- new stable App Server, HTTP API, or SDK surfaces
- new public adapter domains beyond the completed in-scope portfolio
- turning `digital_twin` into a standalone showcase world or widening internal tracks into the public series

## Acceptance Highlights

- package docs, series docs, root rollups, `docs/what-you-can-build.*`, and public-export rewrite text agree on the public portfolio posture
- validation surfaces remain green across the completed public tracks, including the host-bound digital-twin overlay
- the repo is easier to promote downstream without reopening the completed implementation milestones

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_air_traffic_domain.py tests/test_supply_network_domain.py tests/test_semantic_system_domain.py tests/test_power_grid_domain.py tests/test_city_ops_domain.py tests/test_lab_science_domain.py tests/test_market_micro_domain.py tests/test_multiplayer_game_domain.py tests/test_autonomous_vehicle_domain.py tests/test_multi_agent_ai_domain.py tests/test_open_agent_world_domain.py tests/test_digital_twin_domain.py tests/test_operator_workflows.py`

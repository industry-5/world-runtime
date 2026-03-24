# Playbook: City Ops Adapter

## Goal

Run a cross-agency city-ops incident workflow without changing kernel internals.

## Steps

1. Load city-ops fixtures from `examples/scenarios/city-ops-mini`.
2. If you are checking overlay host behavior, confirm this scenario is referenced second in `examples/scenarios/digital-twin-mini/host_bindings.json`.
3. Validate domain types with `adapters/city_ops/schemas` and adapter checks (`make adapters`).
4. Evaluate `proposal.json` and `coordination_options.json` against `adapters/city_ops/policies/default_policy.json`.
5. Confirm explicit coordination outcomes:
   - plans without unified command or hospital access are `deny`
   - long transit detours emit `warn`
   - large resident-impact plans become `require_approval`
6. Run the city-ops quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-city-ops`
7. Validate package coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_city_ops_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

# Playbook: Power Grid Adapter

## Goal

Run a public power-grid contingency workflow without changing kernel internals.

## Steps

1. Load power-grid fixtures from `examples/scenarios/power-grid-mini`.
2. If you are checking overlay host behavior, confirm this scenario is referenced first in `examples/scenarios/digital-twin-mini/host_bindings.json`.
3. Validate domain types with `adapters/power_grid/schemas` and adapter checks (`make adapters`).
4. Evaluate `proposal.json` and `contingency_options.json` against `adapters/power_grid/policies/default_policy.json`.
5. Confirm explicit contingency outcomes:
   - no-simulation or unsafe-frequency plans are `deny`
   - low reserve margin emits `warn`
   - large interruption plans become `require_approval`
6. Run the power-grid quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-power-grid`
7. Validate package coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_power_grid_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

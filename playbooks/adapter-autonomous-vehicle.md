# Playbook: Autonomous Vehicle Adapter

## Goal

Run a public autonomous-vehicle intervention workflow without changing kernel internals.

## Steps

1. Load autonomous-vehicle fixtures from `examples/scenarios/autonomous-vehicle-mini`.
2. Validate domain types with `adapters/autonomous_vehicle/schemas` and adapter checks (`make adapters`).
3. Evaluate `proposal.json` and `maneuver_options.json` against `adapters/autonomous_vehicle/policies/default_policy.json`.
4. Confirm explicit motion-safety outcomes:
   - maneuvers without remote supervision or below the clearance floor are `deny`
   - elevated occluded-crosswalk probability emits `warn`
   - creep plans above the low-speed envelope become `require_approval`
5. Run the autonomous-vehicle quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-autonomous-vehicle`
6. Validate package coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_autonomous_vehicle_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

# Playbook: Air Traffic Adapter

## Goal

Run a safety-constrained air-traffic workflow without changing kernel internals.

## Steps

1. Load air-traffic fixtures from `examples/scenarios/air-traffic-mini`.
2. Validate domain types with `adapters/air_traffic/schemas` and adapter checks (`make adapters`).
3. Evaluate `proposal.json` and `conflicting_proposals.json` against `adapters/air_traffic/policies/default_policy.json`.
4. Confirm explicit constrained outcomes:
   - unsafe clearance proposal is `deny`
   - low fuel margin proposal emits `warn`
   - closed-runway or no-simulation proposals become `require_approval`
5. Run the air-traffic quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-air-traffic`
6. Validate domain safety coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_air_traffic_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

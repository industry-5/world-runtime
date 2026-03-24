# Playbook: Lab Science Adapter

## Goal

Run a public lab-science release workflow without changing kernel internals.

## Steps

1. Load lab-science fixtures from `examples/scenarios/lab-science-mini`.
2. Validate domain types with `adapters/lab_science/schemas` and adapter checks (`make adapters`).
3. Evaluate `proposal.json` and `release_options.json` against `adapters/lab_science/policies/default_policy.json`.
4. Confirm explicit regulated-workflow outcomes:
   - incomplete evidence or low integrity plans are `deny`
   - elevated control drift emits `warn`
   - open-deviation releases become `require_approval`
5. Run the lab-science quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-lab-science`
6. Validate package coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_lab_science_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

# Playbook: Open Agent World Adapter

## Goal

Run a public open-agent-world governance workflow without changing kernel internals.

## Steps

1. Load open-agent-world fixtures from `examples/scenarios/open-agent-world-mini`.
2. Validate domain types with `adapters/open_agent_world/schemas` and adapter checks (`make adapters`).
3. Evaluate `proposal.json` and `intervention_options.json` against `adapters/open_agent_world/policies/default_policy.json`.
4. Confirm explicit shared-world governance outcomes:
   - interventions without an online governance beacon or above the replication ceiling are `deny`
   - dense cross-cohort conflicts emit `warn`
   - interventions that span more than two regions become `require_approval`
5. Run the open-agent-world quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-open-agent-world`
6. Validate package coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_open_agent_world_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

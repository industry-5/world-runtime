# Playbook: Multi-Agent AI Adapter

## Goal

Run a public multi-agent coordination workflow without changing kernel internals.

## Steps

1. Load multi-agent AI fixtures from `examples/scenarios/multi-agent-ai-mini`.
2. Validate domain types with `adapters/multi_agent_ai/schemas` and adapter checks (`make adapters`).
3. Evaluate `proposal.json` and `branch_options.json` against `adapters/multi_agent_ai/policies/default_policy.json`.
4. Confirm explicit agent-governance outcomes:
   - delegation plans that widen write scope or launch privileged tools without review are `deny`
   - plans that carry multiple conflicting objectives emit `warn`
   - plans with more than three delegated agents become `require_approval`
5. Run the multi-agent AI quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-multi-agent-ai`
6. Validate package coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_multi_agent_ai_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

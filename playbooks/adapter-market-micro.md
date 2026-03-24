# Playbook: Market Micro Adapter

## Goal

Run a public market-micro risk workflow without changing kernel internals.

## Steps

1. Load market-micro fixtures from `examples/scenarios/market-micro-mini`.
2. Validate domain types with `adapters/market_micro/schemas` and adapter checks (`make adapters`).
3. Evaluate `proposal.json` and `risk_options.json` against `adapters/market_micro/policies/default_policy.json`.
4. Confirm explicit market-risk outcomes:
   - disarmed kill-switch or hard-limit breach plans are `deny`
   - elevated maker imbalance emits `warn`
   - thin limit headroom becomes `require_approval`
5. Run the market-micro quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-market-micro`
6. Validate package coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_market_micro_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

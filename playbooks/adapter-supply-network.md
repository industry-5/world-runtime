# Playbook: Supply Network Adapter

## Goal

Run supply-network workflows without changing core kernel components.

## Steps

1. Load supply scenario fixtures from `examples/scenarios/supply-network-mini`.
2. Validate `entity_type` and `event_type` values using `adapters/supply_network/schemas`.
3. Evaluate `proposal.json` and `reroute_options.json` with `adapters/supply_network/policies/default_policy.json`.
4. Confirm the selected reroute remains the simulation-backed recommendation while alternate options preserve visible cost/loss tradeoffs.
5. Use replay + simulation engines for state rebuild and what-if analysis.
6. Validate supply-network coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_supply_network_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

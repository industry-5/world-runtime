# Playbook: Supply Network Adapter

## Goal

Run supply-network workflows without changing core kernel components.

## Steps

1. Load supply scenario fixtures from `examples/scenarios/supply-network-mini`.
2. Validate `entity_type` and `event_type` values using `adapters/supply_network/schemas`.
3. Evaluate proposals with `adapters/supply_network/policies/default_policy.json`.
4. Use replay + simulation engines for state rebuild and what-if analysis.
5. Run `make test` and `make evals` before merge.

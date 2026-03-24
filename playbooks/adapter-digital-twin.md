# Playbook: Digital Twin Adapter

## Goal

Run the public digital-twin overlay workflow as a host-bound advisory layer without changing kernel internals or writing directly into host runtimes.

## Steps

1. Load digital-twin fixtures from `examples/scenarios/digital-twin-mini`.
2. Confirm the host overlay attachments in `host_bindings.json` point first to `power-grid-mini` and then to `city-ops-mini`.
3. Validate domain types with `adapters/digital_twin/schemas` and adapter checks (`make adapters`).
4. Evaluate `proposal.json` and `overlay_options.json` against `adapters/digital_twin/policies/default_policy.json`.
5. Confirm explicit overlay outcomes:
   - hostless or direct-writeback plans are `deny`
   - stale cross-host guidance emits `warn`
   - overlays spanning both hosts become `require_approval`
6. Run the digital-twin quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-digital-twin`
7. Validate package coverage before merge:
   - `python3 scripts/check_adapters.py`
   - `python3 scripts/check_examples.py`
   - `python3 -m pytest -q tests/test_digital_twin_domain.py`
   - `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`
   - `make evals`

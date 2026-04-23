# SN-M3 - Replay, Simulation, Playbook, And Docs Completion

## Objective

Align replay/simulation artifacts, contributor/operator guidance, and package-local docs around the implemented public supply-network slice.

## Acceptance Highlights

- replay/simulation artifacts stay aligned with the selected reroute and alternate tradeoffs
- `playbooks/adapter-supply-network.md` reflects the implemented validation path
- package docs advance to local `SN-M3` parity without widening root docs beyond rollup truth

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_supply_network_domain.py tests/test_operator_workflows.py`

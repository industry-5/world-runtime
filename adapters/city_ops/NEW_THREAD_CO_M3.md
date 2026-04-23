# CO-M3 - Replay, Simulation, Playbook, And Docs Completion

## Objective

Align replay/simulation artifacts, contributor/operator guidance, and package-local docs around the implemented public city-ops slice.

## Acceptance Highlights

- replay/simulation artifacts stay aligned with the coordinated civic decision path
- `playbooks/adapter-city-ops.md` reflects the implemented validation path
- package docs advance to local `CO-M3` parity without widening root docs beyond rollup truth

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_city_ops_domain.py tests/test_operator_workflows.py`

# DT-M3 - City-Ops Overlay Expansion And Docs Completion

## Objective

Extend the host-bound overlay path from `power_grid` into `city_ops` and align replay/simulation/package-doc parity around the implemented public digital-twin slice.

## Acceptance Highlights

- replay/simulation artifacts stay aligned with the power-grid-first then city-ops extension path
- `playbooks/adapter-digital-twin.md` reflects the implemented validation path
- package docs advance to local `DT-M3` parity without widening root docs beyond rollup truth

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_digital_twin_domain.py tests/test_operator_workflows.py`

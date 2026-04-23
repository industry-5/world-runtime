# DT-M2 - Power-Grid Overlay Proof

## Objective

Document and validate the first public host-bound overlay proof for `adapter-digital-twin` against `power_grid`.

## Acceptance Highlights

- `host_bindings.json` records `adapter-power-grid` as the first overlay host proof
- `overlay_options.json` is treated as the package-local overlay alternative proof beside the shared runtime artifact set
- targeted digital-twin tests validate deny/allow/require-approval behavior around the power-grid-first path

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_digital_twin_domain.py`

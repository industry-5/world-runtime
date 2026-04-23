# PG-M2 - Domain Tension And Policy Proof

## Objective

Document and validate the least-bad contingency path for the public power-grid package so simulation evidence, interruption approval pressure, and contingency alternatives are explicit package-local proof surfaces.

## Acceptance Highlights

- `contingency_options.json` is treated as the package-local contingency proof beside the shared bundle baseline
- default/scenario policy behavior is validated through targeted power-grid tests
- package docs describe the contingency-response path truthfully without implying later replay/promotion work is complete

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_power_grid_domain.py`

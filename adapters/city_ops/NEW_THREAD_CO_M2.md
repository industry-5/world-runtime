# CO-M2 - Domain Tension And Policy Proof

## Objective

Document and validate the cross-agency coordination path for the public city-ops package so unified command, resident-impact approval pressure, and civic alternatives are explicit package-local proof surfaces.

## Acceptance Highlights

- `coordination_options.json` is treated as the package-local civic-coordination proof beside the shared bundle baseline
- default/scenario policy behavior is validated through targeted city-ops tests
- package docs describe the coordinated-response path truthfully without implying later replay/promotion work is complete

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_city_ops_domain.py`

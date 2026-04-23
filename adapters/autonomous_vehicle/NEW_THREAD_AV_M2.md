# AV-M2 - Domain Tension And Policy Proof

## Objective

Document and validate the motion-safety path for the public autonomous-vehicle package so occlusion pressure, intervention choices, and safer maneuver alternatives are explicit package-local proof surfaces.

## Acceptance Highlights

- `maneuver_options.json` is treated as the package-local motion-safety proof beside the shared bundle baseline
- default/scenario policy behavior is validated through targeted autonomous-vehicle tests
- package docs describe the supervised intervention path truthfully without implying later replay/promotion work is complete

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_autonomous_vehicle_domain.py`

# AT-M2 - Domain Tension And Policy Proof

## Objective

Document and validate the constrained alternative-review path for the public air-traffic package so approval pressure and hard safety rules are explicit package-local proof surfaces.

## Acceptance Highlights

- `conflicting_proposals.json` is treated as the package-local constrained-review proof beside the shared bundle baseline
- default/scenario policy behavior is validated through targeted air-traffic tests
- package docs describe the safety-tension path truthfully without implying later replay/promotion work is complete

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_air_traffic_domain.py`

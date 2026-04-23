# SN-M2 - Domain Tension And Policy Proof

## Objective

Document and validate the tradeoff-review path for the public supply-network package so reroute cost, output loss, and alternate options are explicit package-local proof surfaces.

## Acceptance Highlights

- alternate reroute options are preserved package-locally beside the shared bundle baseline
- default/scenario policy behavior is validated through targeted supply-network tests
- package docs describe the tradeoff path truthfully without implying later replay/promotion work is complete

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_supply_network_domain.py`

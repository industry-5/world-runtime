# MM-M2 - Domain Tension And Policy Proof

## Objective

Document and validate the risk-control path for the public market-micro package so exposure pressure, multi-actor conflict, and safer inventory alternatives are explicit package-local proof surfaces.

## Acceptance Highlights

- `risk_options.json` is treated as the package-local market-risk proof beside the shared bundle baseline
- default/scenario policy behavior is validated through targeted market-micro tests
- package docs describe the supervised de-risking path truthfully without implying later replay/promotion work is complete

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_market_micro_domain.py`

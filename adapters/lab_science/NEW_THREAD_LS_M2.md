# LS-M2 - Domain Tension And Policy Proof

## Objective

Document and validate the regulated release path for the public lab-science package so evidence integrity, deviation review, and safer release alternatives are explicit package-local proof surfaces.

## Acceptance Highlights

- `release_options.json` is treated as the package-local regulated-release proof beside the shared bundle baseline
- default/scenario policy behavior is validated through targeted lab-science tests
- package docs describe the regulated review path truthfully without implying later replay/promotion work is complete

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_lab_science_domain.py`

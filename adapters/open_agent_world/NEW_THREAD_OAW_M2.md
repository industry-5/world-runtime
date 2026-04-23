# OAW-M2 - Domain Tension And Policy Proof

## Objective

Document and validate the governed intervention path for the public open-agent-world package so commons conflict, stewardship, and bounded alternatives are explicit package-local proof surfaces.

## Acceptance Highlights

- `intervention_options.json` is treated as the package-local bounded-governance proof beside the shared bundle baseline
- default/scenario policy behavior is validated through targeted open-agent-world tests
- package docs describe the shared-world governance path truthfully without implying later replay/promotion work is complete

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_open_agent_world_domain.py`

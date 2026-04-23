# SN-M1 - Adapter Contract, Schemas, Minimal Scenario, Registry Wiring

## Objective

Backfill and verify the existing supply-network adapter implementation as a package-local `M1` slice with truthful docs, aligned validation, and clear boundaries.

## In Scope

- package-local normalization of the existing adapter contract and docs
- schemas, policy, and minimal scenario alignment
- registry/example/test expectations for the current supply-network slice

## Out Of Scope

- deeper replay/simulation hardening beyond the minimal `M1` slice
- promotion wording that implies later milestones are complete
- repo-wide API surface changes

## Acceptance Highlights

- package-local docs match the current adapter assets on disk
- the package clearly states what is already implemented and what remains for later milestones
- current validation targets for the package are explicit and runnable

## Validation Targets

- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_operator_workflows.py`

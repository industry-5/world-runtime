# Playbook: Semantic System Adapter

## Goal

Run a governed semantic-change workflow without changing kernel internals.

## Steps

1. Load semantic-system fixtures from `examples/scenarios/semantic-system-mini`.
2. Validate domain types with `adapters/semantic_system/schemas` and adapter checks (`make adapters`).
3. Evaluate `proposal.json` and `conflicting_proposals.json` against `adapters/semantic_system/policies/default_policy.json`.
4. Confirm explicit semantic-governance outcomes:
   - missing provenance is `deny`
   - high-conflict changes emit `warn`
   - breaking meaning changes become `require_approval`
5. Run the semantic-system quickstart path:
   - `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-semantic-system`
6. Validate semantic coverage before merge:
   - `python3 -m pytest -q tests/test_semantic_system_domain.py`
   - `make evals`

# Supply Network Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-supply-network`
- Milestone status: **SN-M0 through SN-M4 complete**
- Current milestone: **No active package milestone (SN-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_SN_M4.md` retained for history

## Current Snapshot

- `SN-M1` normalized the existing adapter contract, schemas, policy, and public scenario bundle as package-local truth
- `SN-M2` now makes reroute tradeoffs explicit through `reroute_options.json`, enriched decision/simulation artifacts, and `tests/test_supply_network_domain.py`
- `SN-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public supply-network slice
- `SN-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_supply_network_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `SN-M4` validation baseline:

1. Package bootstrap:
- `find adapters/supply_network -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "SN-M[0-4]" adapters/supply_network/ROADMAP.md adapters/supply_network/STATUS.md adapters/supply_network/README.md adapters/supply_network/NEW_THREAD_KICKOFF_PROMPT.md adapters/supply_network/NEW_THREAD_SN_M0.md adapters/supply_network/NEW_THREAD_SN_M1.md adapters/supply_network/NEW_THREAD_SN_M2.md adapters/supply_network/NEW_THREAD_SN_M3.md adapters/supply_network/NEW_THREAD_SN_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_supply_network_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-supply-network.md` and `examples/scenarios/supply-network-mini/README.md` still describe the same reroute-tradeoff path

## Completed SN-M4 Outcome

- the completed `SN-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- promotion hardening should build on the completed `SN-M3` slice instead of reopening foundational normalization work
- the supply-network track should remain distinct from `adapter-supply-ops`

## Handoff Checklist For New Thread

1. Re-read `adapters/supply_network/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/supply_network/NEW_THREAD_SN_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `SN-M0` through `SN-M4` scope unless a correctness fix requires it.

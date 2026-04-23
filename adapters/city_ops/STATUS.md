# City Ops Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-city-ops`
- Milestone status: **CO-M0 through CO-M4 complete**
- Current milestone: **No active package milestone (CO-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_CO_M4.md` retained for history

## Current Snapshot

- `CO-M1` established the first runtime-authoritative city-ops adapter slice, schemas, policy, and minimal public scenario bundle
- `CO-M2` now treats civic coordination alternatives, resident-impact approval pressure, and cross-agency safety constraints as explicit package-local proof through `coordination_options.json` and `tests/test_city_ops_domain.py`
- `CO-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public city-ops slice
- `CO-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_city_ops_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `CO-M4` validation baseline:

1. Package bootstrap:
- `find adapters/city_ops -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "CO-M[0-4]" adapters/city_ops/ROADMAP.md adapters/city_ops/STATUS.md adapters/city_ops/README.md adapters/city_ops/NEW_THREAD_KICKOFF_PROMPT.md adapters/city_ops/NEW_THREAD_CO_M0.md adapters/city_ops/NEW_THREAD_CO_M1.md adapters/city_ops/NEW_THREAD_CO_M2.md adapters/city_ops/NEW_THREAD_CO_M3.md adapters/city_ops/NEW_THREAD_CO_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_city_ops_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-city-ops.md` and `examples/scenarios/city-ops-mini/README.md` still describe the same coordinated-response path

## Completed CO-M4 Outcome

- the completed `CO-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `CO-M4` slice instead of reopening foundational implementation work
- the city-ops track should remain focused on cross-agency incident coordination rather than broad municipal platform scope

## Handoff Checklist For New Thread

1. Re-read `adapters/city_ops/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/city_ops/NEW_THREAD_CO_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `CO-M0` through `CO-M4` scope unless a correctness fix requires it.

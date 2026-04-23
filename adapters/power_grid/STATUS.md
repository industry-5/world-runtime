# Power Grid Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-power-grid`
- Milestone status: **PG-M0 through PG-M4 complete**
- Current milestone: **No active package milestone (PG-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_PG_M4.md` retained for history

## Current Snapshot

- `PG-M1` established the first runtime-authoritative power-grid adapter slice, schemas, policy, and minimal public scenario bundle
- `PG-M2` now treats contingency alternatives, least-bad load shed, and approval-required interruptions as explicit package-local proof through `contingency_options.json` and `tests/test_power_grid_domain.py`
- `PG-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public power-grid slice
- `PG-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_power_grid_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `PG-M4` validation baseline:

1. Package bootstrap:
- `find adapters/power_grid -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "PG-M[0-4]" adapters/power_grid/ROADMAP.md adapters/power_grid/STATUS.md adapters/power_grid/README.md adapters/power_grid/NEW_THREAD_KICKOFF_PROMPT.md adapters/power_grid/NEW_THREAD_PG_M0.md adapters/power_grid/NEW_THREAD_PG_M1.md adapters/power_grid/NEW_THREAD_PG_M2.md adapters/power_grid/NEW_THREAD_PG_M3.md adapters/power_grid/NEW_THREAD_PG_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_power_grid_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-power-grid.md` and `examples/scenarios/power-grid-mini/README.md` still describe the same contingency path

## Completed PG-M4 Outcome

- the completed `PG-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `PG-M4` slice instead of reopening foundational implementation work
- the power-grid track should remain focused on balancing, contingencies, and least-bad infrastructure response rather than broad market operations

## Handoff Checklist For New Thread

1. Re-read `adapters/power_grid/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/power_grid/NEW_THREAD_PG_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `PG-M0` through `PG-M4` scope unless a correctness fix requires it.

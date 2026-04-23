# Digital Twin Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-digital-twin`
- Milestone status: **DT-M0 through DT-M4 complete**
- Current milestone: **No active package milestone (DT-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_DT_M4.md` retained for history

## Current Snapshot

- `DT-M1` established the first runtime-authoritative digital-twin overlay slice, schemas, default policy, and the host-bound overlay bundle shape
- `DT-M2` now treats the `power_grid` host-binding proof as explicit package-local evidence through `host_bindings.json`, `overlay_options.json`, and `tests/test_digital_twin_domain.py`
- `DT-M3` extends the overlay path into `city_ops` and aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public overlay slice
- `DT-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_digital_twin_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `DT-M4` validation baseline:

1. Package bootstrap:
- `find adapters/digital_twin -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "DT-M[0-4]" adapters/digital_twin/ROADMAP.md adapters/digital_twin/STATUS.md adapters/digital_twin/README.md adapters/digital_twin/NEW_THREAD_KICKOFF_PROMPT.md adapters/digital_twin/NEW_THREAD_DT_M0.md adapters/digital_twin/NEW_THREAD_DT_M1.md adapters/digital_twin/NEW_THREAD_DT_M2.md adapters/digital_twin/NEW_THREAD_DT_M3.md adapters/digital_twin/NEW_THREAD_DT_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_digital_twin_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-digital-twin.md` and `examples/scenarios/digital-twin-mini/README.md` still describe the same host-bound overlay path

## Completed DT-M4 Outcome

- the completed `DT-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `DT-M4` slice instead of reopening foundational implementation work
- the digital-twin track should stay host-bound to `power_grid` and `city_ops` rather than becoming a standalone showcase world

## Handoff Checklist For New Thread

1. Re-read `adapters/digital_twin/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/digital_twin/NEW_THREAD_DT_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `DT-M0` through `DT-M4` scope unless a correctness fix requires it.

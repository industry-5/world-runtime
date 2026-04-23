# Autonomous Vehicle Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-autonomous-vehicle`
- Milestone status: **AV-M0 through AV-M4 complete**
- Current milestone: **No active package milestone (AV-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_AV_M4.md` retained for history

## Current Snapshot

- `AV-M1` established the first runtime-authoritative autonomous-vehicle adapter slice, schemas, policy, and minimal public scenario bundle
- `AV-M2` now treats motion-safety alternatives, occlusion pressure, and approval-required creep interventions as explicit package-local proof through `maneuver_options.json` and `tests/test_autonomous_vehicle_domain.py`
- `AV-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public autonomous-vehicle slice
- `AV-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_autonomous_vehicle_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `AV-M4` validation baseline:

1. Package bootstrap:
- `find adapters/autonomous_vehicle -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "AV-M[0-4]" adapters/autonomous_vehicle/ROADMAP.md adapters/autonomous_vehicle/STATUS.md adapters/autonomous_vehicle/README.md adapters/autonomous_vehicle/NEW_THREAD_KICKOFF_PROMPT.md adapters/autonomous_vehicle/NEW_THREAD_AV_M0.md adapters/autonomous_vehicle/NEW_THREAD_AV_M1.md adapters/autonomous_vehicle/NEW_THREAD_AV_M2.md adapters/autonomous_vehicle/NEW_THREAD_AV_M3.md adapters/autonomous_vehicle/NEW_THREAD_AV_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_autonomous_vehicle_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-autonomous-vehicle.md` and `examples/scenarios/autonomous-vehicle-mini/README.md` still describe the same supervised intervention path

## Completed AV-M4 Outcome

- the completed `AV-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `AV-M4` slice instead of reopening foundational implementation work
- the autonomous-vehicle track should stay focused on motion planning, teleassist intervention, and safety-limited fallback choices rather than broad autonomy platform coverage

## Handoff Checklist For New Thread

1. Re-read `adapters/autonomous_vehicle/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/autonomous_vehicle/NEW_THREAD_AV_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `AV-M0` through `AV-M4` scope unless a correctness fix requires it.

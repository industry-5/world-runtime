# Air Traffic Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-air-traffic`
- Milestone status: **AT-M0 through AT-M4 complete**
- Current milestone: **No active package milestone (AT-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_AT_M4.md` retained for history

## Current Snapshot

- `AT-M1` normalized the existing adapter contract, schemas, policy, and public scenario bundle as package-local truth
- `AT-M2` now treats constrained alternatives and approval pressure as explicit package-local proof through `conflicting_proposals.json` and `tests/test_air_traffic_domain.py`
- `AT-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public air-traffic slice
- `AT-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_air_traffic_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `AT-M4` validation baseline:

1. Package bootstrap:
- `find adapters/air_traffic -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "AT-M[0-4]" adapters/air_traffic/ROADMAP.md adapters/air_traffic/STATUS.md adapters/air_traffic/README.md adapters/air_traffic/NEW_THREAD_KICKOFF_PROMPT.md adapters/air_traffic/NEW_THREAD_AT_M0.md adapters/air_traffic/NEW_THREAD_AT_M1.md adapters/air_traffic/NEW_THREAD_AT_M2.md adapters/air_traffic/NEW_THREAD_AT_M3.md adapters/air_traffic/NEW_THREAD_AT_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_air_traffic_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-air-traffic.md` and `examples/scenarios/air-traffic-mini/README.md` still describe the same constrained-review path

## Completed AT-M4 Outcome

- the completed `AT-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `AT-M4` slice instead of reopening foundational implementation work
- the air-traffic track should remain the high-constraint safety proof path inside the public portfolio

## Handoff Checklist For New Thread

1. Re-read `adapters/air_traffic/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/air_traffic/NEW_THREAD_AT_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `AT-M0` through `AT-M4` scope unless a correctness fix requires it.

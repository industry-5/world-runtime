# Lab Science Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-lab-science`
- Milestone status: **LS-M0 through LS-M4 complete**
- Current milestone: **No active package milestone (LS-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_LS_M4.md` retained for history

## Current Snapshot

- `LS-M1` established the first runtime-authoritative lab-science adapter slice, schemas, policy, and minimal public scenario bundle
- `LS-M2` now treats regulated release alternatives, evidence integrity, and approval-required deviation handling as explicit package-local proof through `release_options.json` and `tests/test_lab_science_domain.py`
- `LS-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public lab-science slice
- `LS-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_lab_science_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `LS-M4` validation baseline:

1. Package bootstrap:
- `find adapters/lab_science -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "LS-M[0-4]" adapters/lab_science/ROADMAP.md adapters/lab_science/STATUS.md adapters/lab_science/README.md adapters/lab_science/NEW_THREAD_KICKOFF_PROMPT.md adapters/lab_science/NEW_THREAD_LS_M0.md adapters/lab_science/NEW_THREAD_LS_M1.md adapters/lab_science/NEW_THREAD_LS_M2.md adapters/lab_science/NEW_THREAD_LS_M3.md adapters/lab_science/NEW_THREAD_LS_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_lab_science_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-lab-science.md` and `examples/scenarios/lab-science-mini/README.md` still describe the same regulated-release path

## Completed LS-M4 Outcome

- the completed `LS-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `LS-M4` slice instead of reopening foundational implementation work
- the lab-science track should remain focused on regulated release, evidence integrity, and deviation governance rather than general lab operations breadth

## Handoff Checklist For New Thread

1. Re-read `adapters/lab_science/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/lab_science/NEW_THREAD_LS_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `LS-M0` through `LS-M4` scope unless a correctness fix requires it.

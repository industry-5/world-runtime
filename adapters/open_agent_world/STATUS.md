# Open Agent World Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-open-agent-world`
- Milestone status: **OAW-M0 through OAW-M4 complete**
- Current milestone: **No active package milestone (OAW-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_OAW_M4.md` retained for history

## Current Snapshot

- `OAW-M1` established the first runtime-authoritative open-agent-world adapter slice, schemas, policy, and minimal public scenario bundle
- `OAW-M2` now treats bounded intervention alternatives, commons-conflict pressure, and approval-required governance as explicit package-local proof through `intervention_options.json` and `tests/test_open_agent_world_domain.py`
- `OAW-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public open-agent-world slice
- `OAW-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_open_agent_world_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `OAW-M4` validation baseline:

1. Package bootstrap:
- `find adapters/open_agent_world -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "OAW-M[0-4]" adapters/open_agent_world/ROADMAP.md adapters/open_agent_world/STATUS.md adapters/open_agent_world/README.md adapters/open_agent_world/NEW_THREAD_KICKOFF_PROMPT.md adapters/open_agent_world/NEW_THREAD_OAW_M0.md adapters/open_agent_world/NEW_THREAD_OAW_M1.md adapters/open_agent_world/NEW_THREAD_OAW_M2.md adapters/open_agent_world/NEW_THREAD_OAW_M3.md adapters/open_agent_world/NEW_THREAD_OAW_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_open_agent_world_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-open-agent-world.md` and `examples/scenarios/open-agent-world-mini/README.md` still describe the same governed intervention path

## Completed OAW-M4 Outcome

- the completed `OAW-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `OAW-M4` slice instead of reopening foundational implementation work
- the open-agent-world track should stay focused on shared-world governance, intervention, and conflict management rather than broad sandbox-platform scope

## Handoff Checklist For New Thread

1. Re-read `adapters/open_agent_world/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/open_agent_world/NEW_THREAD_OAW_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `OAW-M0` through `OAW-M4` scope unless a correctness fix requires it.

# Multi-Agent AI Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-multi-agent-ai`
- Milestone status: **MA-M0 through MA-M4 complete**
- Current milestone: **No active package milestone (MA-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_MA_M4.md` retained for history

## Current Snapshot

- `MA-M1` established the first runtime-authoritative multi-agent AI adapter slice, schemas, policy, and minimal public scenario bundle
- `MA-M2` now treats reviewed branch alternatives, delegated agent-count pressure, and approval-required coordination as explicit package-local proof through `branch_options.json` and `tests/test_multi_agent_ai_domain.py`
- `MA-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public multi-agent AI slice
- `MA-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_multi_agent_ai_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `MA-M4` validation baseline:

1. Package bootstrap:
- `find adapters/multi_agent_ai -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "MA-M[0-4]" adapters/multi_agent_ai/ROADMAP.md adapters/multi_agent_ai/STATUS.md adapters/multi_agent_ai/README.md adapters/multi_agent_ai/NEW_THREAD_KICKOFF_PROMPT.md adapters/multi_agent_ai/NEW_THREAD_MA_M0.md adapters/multi_agent_ai/NEW_THREAD_MA_M1.md adapters/multi_agent_ai/NEW_THREAD_MA_M2.md adapters/multi_agent_ai/NEW_THREAD_MA_M3.md adapters/multi_agent_ai/NEW_THREAD_MA_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_multi_agent_ai_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-multi-agent-ai.md` and `examples/scenarios/multi-agent-ai-mini/README.md` still describe the same reviewed coordination path

## Completed MA-M4 Outcome

- the completed `MA-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `MA-M4` slice instead of reopening foundational implementation work
- the multi-agent AI track should stay focused on delegated coordination, branch review, and explicit governance rather than broad agent-platform scope

## Handoff Checklist For New Thread

1. Re-read `adapters/multi_agent_ai/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/multi_agent_ai/NEW_THREAD_MA_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `MA-M0` through `MA-M4` scope unless a correctness fix requires it.

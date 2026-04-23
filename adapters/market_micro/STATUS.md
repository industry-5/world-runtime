# Market Micro Public Adapter Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Domain package: `adapter-market-micro`
- Milestone status: **MM-M0 through MM-M4 complete**
- Current milestone: **No active package milestone (MM-M4 complete)**
- Next recommended milestone: **Post-promotion maintenance or downstream export follow-through (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_MM_M4.md` retained for history

## Current Snapshot

- `MM-M1` established the first runtime-authoritative market-micro adapter slice, schemas, policy, and minimal public scenario bundle
- `MM-M2` now treats market-risk alternatives, exposure pressure, and approval-required inventory interventions as explicit package-local proof through `risk_options.json` and `tests/test_market_micro_domain.py`
- `MM-M3` aligns replay/simulation artifacts, playbook guidance, and package docs around the implemented public market-micro slice
- `MM-M4` completed the downstream-promotion audit across package docs, scenario README/playbook guidance, and validation posture without changing the package's public proof identity
- current repo-level validation covers the package through `scripts/check_adapters.py`, `scripts/check_examples.py`, `tests/test_adapters.py`, `tests/test_scenario_bundles.py`, `tests/test_market_micro_domain.py`, and `tests/test_operator_workflows.py`
- no stable App Server, HTTP API, or SDK surface changed while advancing the package to local `M4`

## Validation Baseline

Completed `MM-M4` validation baseline:

1. Package bootstrap:
- `find adapters/market_micro -maxdepth 1 -type f | sort`

2. Milestone consistency:
- `rg -n "MM-M[0-4]" adapters/market_micro/ROADMAP.md adapters/market_micro/STATUS.md adapters/market_micro/README.md adapters/market_micro/NEW_THREAD_KICKOFF_PROMPT.md adapters/market_micro/NEW_THREAD_MM_M0.md adapters/market_micro/NEW_THREAD_MM_M1.md adapters/market_micro/NEW_THREAD_MM_M2.md adapters/market_micro/NEW_THREAD_MM_M3.md adapters/market_micro/NEW_THREAD_MM_M4.md`

3. Current adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_market_micro_domain.py tests/test_operator_workflows.py`

4. Package-local docs/playbook consistency:
- verify `playbooks/adapter-market-micro.md` and `examples/scenarios/market-micro-mini/README.md` still describe the same supervised de-risking path

## Completed MM-M4 Outcome

- the completed `MM-M4` pass hardened the package docs, scenario README/playbook wording, and validation posture for downstream public promotion without widening stable runtime/public surfaces

## Known Constraints

- this package is part of the public adapter program
- root docs should remain rollup-only
- any follow-up should build on the completed `MM-M4` slice instead of reopening foundational implementation work
- the market-micro track should remain focused on exposure limits, inventory pressure, and desk-risk controls rather than broad exchange or brokerage operations

## Handoff Checklist For New Thread

1. Re-read `adapters/market_micro/STATUS.md`, `ROADMAP.md`, and `README.md`.
2. Re-read `adapters/market_micro/NEW_THREAD_MM_M4.md` as historical context if the follow-up touches promotion/export posture.
3. Re-read touched root rollups only if repo-wide posture matters.
4. Keep any follow-up narrowly scoped and do not reopen completed `MM-M0` through `MM-M4` scope unless a correctness fix requires it.

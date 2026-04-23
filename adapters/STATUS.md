# Public Domain Adapter Program Status

_Last updated: 2026-03-23 (America/Chicago)_

## Current Phase

- Program: public domain adapter scenario program
- Milestone status: **DA-M1 through DA-M9 complete**
- Current milestone: **No active series milestone (DA-M9 complete)**
- Next recommended milestone: **Downstream promotion/export handoff or post-promotion maintenance (not yet scoped)**
- Next thread entrypoint: `NEW_THREAD_KICKOFF_PROMPT.md`
- Active milestone brief: none; `NEW_THREAD_DA_M9.md` retained for history

## Current Snapshot

- `DA-M1` established the series-level governance docs in `adapters/`
- `DA-M2` established shared public-track metadata, package checklist validation, and the generic non-overlay scenario-bundle contract
- package-local governance docs now exist for every in-scope public track and are validated through the shared checklist
- `air_traffic` and `supply_network` now describe their implemented public slices through local `M3` instead of remaining legacy `M1` carryovers
- `semantic_system` is now the third implemented public proof path with package-local `SS-M1` through `SS-M3` landed
- `power_grid` is now the fourth implemented public proof path with package-local `PG-M1` through `PG-M3` landed
- `city_ops` is now the fifth implemented public proof path with package-local `CO-M1` through `CO-M3` landed
- `lab_science` is now the sixth implemented public proof path with package-local `LS-M1` through `LS-M3` landed
- `market_micro` is now the seventh implemented public proof path with package-local `MM-M1` through `MM-M3` landed
- `multiplayer_game` is now the eighth implemented public proof path with package-local `MPG-M1` through `MPG-M3` landed
- `autonomous_vehicle` is now the ninth implemented public proof path with package-local `AV-M1` through `AV-M3` landed
- `multi_agent_ai` is now the tenth implemented public proof path with package-local `MA-M1` through `MA-M3` landed
- `open_agent_world` is now the eleventh implemented public proof path with package-local `OAW-M1` through `OAW-M3` landed
- `digital_twin` is now the first implemented public overlay track, with package-local `DT-M1` through `DT-M3` landed first on `power_grid` and then extended to `city_ops`
- package-local `M4` promotion-hardening closeout now lands across every in-scope public track, including the host-bound `digital_twin` overlay path
- touched root/docs rollups and `docs/what-you-can-build.*` now describe the same eleven standalone proof paths plus the host-bound digital-twin overlay
- public-export rewrite text now matches the on-repo public adapter story and no longer lags older portfolio states
- `supply_ops` and `world_game` remain in-repo internal tracks and are explicitly out-of-program for this series
- no stable App Server, HTTP API, or SDK surface changed as part of `DA-M1` through `DA-M9`

## Validation Baseline

Completed `DA-M9` baseline:

1. Series/bootstrap structure:
- `find adapters -maxdepth 2 -type f | sort`

2. Milestone naming consistency:
- `rg -n "DA-M[1-9]|(SN|AT|SS|PG|CO|LS|MM|MPG|AV|MA|OAW|DT)-M[0-4]" adapters`

3. Shared adapter/example safety:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_adapters.py tests/test_scenario_bundles.py tests/test_air_traffic_domain.py tests/test_supply_network_domain.py tests/test_semantic_system_domain.py tests/test_power_grid_domain.py tests/test_city_ops_domain.py tests/test_lab_science_domain.py tests/test_market_micro_domain.py tests/test_multiplayer_game_domain.py tests/test_autonomous_vehicle_domain.py tests/test_multi_agent_ai_domain.py tests/test_open_agent_world_domain.py tests/test_digital_twin_domain.py tests/test_operator_workflows.py`

4. Public-doc sync:
- verify touched root/docs rollups stay rollup-only
- verify `docs/what-you-can-build.md`, the matching HTML portfolio narrative, and export rewrite text stay aligned

5. Public-export smoke:
- run the curated public-export build smoke used for downstream promotion readiness

## Completed DA-M9 Outcome

- the final public adapter audit now closes across package docs, root rollups, `docs/what-you-can-build.*`, validation surfaces, and public-export wording so the portfolio is ready for downstream promotion

## Immediate Next Opportunities

- stage or review the curated downstream export with the public-export build smoke used for promotion readiness
- treat future public-adapter changes as post-series maintenance or a newly declared milestone rather than reopening the completed `DA-M1` through `DA-M9` arc
- keep the digital-twin overlay explicitly host-bound during downstream promotion and public maintenance

## Known Constraints

- `supply_ops` and `world_game` are out-of-program for this series
- root docs should stay concise and should not absorb package-local milestone detail
- `digital_twin` is overlay-first and should not be treated as a standalone world-showcase track
- future adapter implementation milestones should not widen stable public API surfaces by default
- `DA-M2` shared standards should remain the baseline rather than being re-specialized around any one implemented public adapter
- the completed eleven standalone implemented public tracks and the host-bound overlay track should stay stable during downstream promotion follow-through

## Handoff Checklist For New Thread

1. Re-read `adapters/STATUS.md` and `adapters/ROADMAP.md` from disk.
2. Re-read `adapters/README.md`, `adapters/CHANGELOG.md`, and `NEW_THREAD_DA_M9.md` as historical context if a follow-up touches public-export posture.
3. Re-read touched root rollups: `README.md`, `STATUS.md`, `ROADMAP.md`, `docs/README.md`, `docs/what-you-can-build.md`, and the matching HTML portfolio narrative.
4. Confirm `git status` and avoid reverting unrelated work.
5. Keep series docs authoritative for program-level detail, package docs authoritative for track-level detail, and do not reopen completed `DA-M1` through `DA-M9` scope unless a correctness fix requires it.

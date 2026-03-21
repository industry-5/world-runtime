# World Game Studio Next Status

_Last updated: 2026-03-14 (America/Chicago)_

## Current Phase

- Studio package: `world_game_studio_next`
- Milestone status: **WG-P0 through WG-P10 complete**
- Current milestone: **WG-P10 complete (Release-grade stabilization, browser E2E, and promotion follow-through)**

## Planned Milestones

- WG-P0: Program bootstrap and hygiene
- WG-P1: Topology, geometry, and layer contracts
- WG-P2: Studio platform foundation
- WG-P3: Dymaxion canvas and core planning loop
- WG-P4: Compare, replay, and evidence surfaces
- WG-P5: Collaboration, facilitation, and persistence
- WG-P6: Hardening, cutover, and legacy containment
- WG-P7: Experience realization and shell redesign
- WG-P8: Analytical overlays, compare depth, and narrative explanation
- WG-P9: Facilitation, shared-attention, and session-role maturity
- WG-P10: Release-grade stabilization, browser E2E, and promotion follow-through

## Validation Baseline

WG-P10 validation groups completed:

1. Studio baseline:
- `python3 labs/world_game_studio_next/scripts/build_static.py` -> passed
- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py` -> passed (`14 passed`)
- `find labs/world_game_studio_next -maxdepth 2 \( -type f -o -type d \) | sort` -> passed

2. Milestone-specific validation:
- `python3 -m pytest -q tests/labs/test_world_game_studio_next_browser_e2e.py` -> passed/skip-by-environment (Safari WebDriver required)
- `rg -n "RESPONSIVENESS_BUDGETS_MS|__WG_STUDIO_NEXT_DIAGNOSTICS|planning-performance-summary|test_world_game_studio_next_browser_e2e|map_redraw_p95|replay_scrub_p95|overlay_toggle_p95" labs/world_game_studio_next/src tests/labs/test_world_game_studio_next.py tests/labs/test_world_game_studio_next_browser_e2e.py labs/world_game_studio_next/README.md playbooks/world-game-studio-next-demo.md` -> passed
- profiling evidence captured from workspace diagnostics:
  - `window.__WG_STUDIO_NEXT_DIAGNOSTICS.map_redraw`
  - `window.__WG_STUDIO_NEXT_DIAGNOSTICS.replay_scrub`
  - `window.__WG_STUDIO_NEXT_DIAGNOSTICS.overlay_toggle`
  - p95 budgets: redraw `120ms`, replay scrub `180ms`, overlay toggle `150ms`

3. Domain/runtime regression checks:
- `python3 scripts/check_adapters.py` -> passed
- `python3 scripts/check_examples.py` -> passed
- targeted runtime/domain pytest coverage used:
  - `tests/test_world_game_smoke.py`
  - `tests/test_world_game_examples.py`

## Completed Milestones

- WG-P0: Program bootstrap and hygiene (completed 2026-03-13)
- WG-P1: Topology, geometry, and layer contracts (completed 2026-03-13)
- WG-P2: Studio platform foundation (completed 2026-03-13)
- WG-P3: Dymaxion canvas and core planning loop (completed 2026-03-14)
- WG-P4: Compare, replay, and evidence surfaces (completed 2026-03-14)
- WG-P5: Collaboration, facilitation, and persistence (completed 2026-03-14)
- WG-P6: Hardening, cutover, and legacy containment (completed 2026-03-14)
- WG-P7: Experience realization and shell redesign (completed 2026-03-14)
- WG-P8: Analytical overlays, compare depth, and narrative explanation (completed 2026-03-14)
- WG-P9: Facilitation, shared-attention, and session-role maturity (completed 2026-03-14)
- WG-P10: Release-grade stabilization, browser E2E, and promotion follow-through (completed 2026-03-14)

## WG-P10 Completion Evidence

- Added browser E2E harness for route-level user journeys:
  - Safari WebDriver suite in `tests/labs/test_world_game_studio_next_browser_e2e.py`
  - onboarding route, keyboard shortcut routing (`Alt+1..6`), reduced-motion toggle path
  - map interaction in Plan plus compare/replay/facilitate route workflow checks
- Added profiling diagnostics and explicit responsiveness budgets:
  - diagnostics tracker in `src/world_canvas/planningWorkspace.js`
  - global diagnostics export `window.__WG_STUDIO_NEXT_DIAGNOSTICS`
  - visible profiling summary panel `planning-performance-summary`
  - p95 budgets set and reported for map redraw (`120ms`), replay scrub (`180ms`), and overlay toggle (`150ms`)
- Updated WG-P10 tests and docs:
  - `tests/labs/test_world_game_studio_next_browser_e2e.py`
  - `tests/labs/test_world_game_studio_next.py`
  - `labs/world_game_studio_next/README.md`
  - `labs/world_game_studio_next/CHANGELOG.md`
  - `labs/world_game_studio_next/ROADMAP.md`
  - `labs/world_game_studio_next/studio_manifest.json`
  - `playbooks/world-game-studio-next-demo.md`
- Legacy studio retirement follow-through is now complete:
  - `labs/world_game_studio` has been removed from the active repo surface after Studio Next stabilization.

## Next Milestone Candidate

- Post-WG-P10 stabilization follow-ups (targeted hardening only; no new product pillars)

## Notes

- `labs/world_game_studio_next` is now the primary World Game studio surface for demos/workshops/new UX work.
- `labs/world_game_studio` has been retired after stabilization and removed from the active repo surface.
- `adapters/world_game` remains the domain and runtime source of truth.
- Mirrored scratch docs still describe a React/Vite-oriented modernization path; repo truth remains the implemented vanilla JS studio-next surface tracked in this status file.

## Risks / Deferred Follow-Ups

- Risk: topology transport remains file-driven in studio-next; no runtime `world_game.topology.*` surface exists yet.
- Risk: replay checkpoint cues are derived from current frame payload heuristics; explicit runtime-authored checkpoint metadata is still absent.
- Risk: compare hotspot severity/confidence remains client-derived from current equity deltas and tradeoff gaps rather than runtime-authored explanation metadata.
- Risk: collaboration durability now supports export/import bundles, but automatic persisted storage/indexing is still deferred.
- Risk: browser E2E harness currently targets Safari WebDriver; cross-browser matrix coverage is still absent.
- Risk: shared-attention presenter and spotlight cues are explicitly local-only; no runtime synchronized spotlight/presence metadata exists yet.
- Risk: session continuity is now discoverable for active session refresh and bundle import/export, but runtime session list/resume workflows remain unavailable on `world_game.session.*`.
- Risk: density mode preference remains session-local UI state and is not persisted per user profile.
- Risk: reduced-motion preference is session-local UI state and is not yet persisted per user profile.
- Risk: canvas render fingerprint optimization and diagnostics sampling remain JSON/JS object based; larger geometry/overlay workloads may still require deeper profiling strategy.
- Risk: `jsonschema.RefResolver` deprecation warning remains in domain authoring validation path.
- Deferred: add runtime topology delivery method(s) or scenario-load topology references to remove long-term file-only geometry binding.
- Deferred: enrich compare payload surfaces for multi-indicator and flow-level delta legends.
- Deferred: add replay playback transport enhancements (auto-play, explicit jump-to-branch-point timeline controls, runtime-authored checkpoint tags).
- Deferred: add shared multi-client spotlight/presence synchronization semantics beyond local studio presentation cues.
- Deferred: evaluate whether role presets should bind to runtime actor roles for optional synchronization (without breaking thin-client posture).
- Deferred: expand browser E2E coverage to include density/role permutation matrix and cross-browser compatibility.
- Deferred: clean any remaining historical references to the retired legacy studio when milestone-history edits are worth the churn.

## Handoff Checklist For New Thread

1. Re-read `labs/world_game_studio_next/STATUS.md` and `labs/world_game_studio_next/ROADMAP.md` from disk.
2. Re-read `adapters/world_game/STATUS.md` and `adapters/world_game/ROADMAP.md` before assuming runtime capabilities.
3. Confirm `git status` and avoid reverting unrelated changes.
4. Keep milestone boundary tight; list adjacent improvements as follow-ups rather than widening scope.
5. Do not reintroduce dependencies on the retired `labs/world_game_studio` surface.
6. End milestone threads by updating this file with validation evidence, completion state, and next recommended milestone.

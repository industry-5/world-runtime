# Playbook: World Game Studio Next Demo Flow

## Goal

Run the canonical World Game showcase walkthrough in `labs/world_game_studio_next` using runtime-backed World Game methods only.

## Preconditions

1. Start API server:
   - `python3 -m api.http_server --host 127.0.0.1 --port 8080`
2. Start studio-next server:
   - `python3 labs/world_game_studio_next/server.py --host 127.0.0.1 --port 8093 --upstream http://127.0.0.1:8080`
3. Open:
   - `http://127.0.0.1:8093`

## Guided flow

1. Open the `Onboard` route (`Alt+1`) and run `Start quickstart`.
2. In `Plan` (`Alt+2`), select a region and create then submit a proposal.
3. Adopt the proposal to create a branch, then run one turn in `simulation` stage.
4. Open `Compare` (`Alt+4`) and run branch comparison.
   - set a hotspot threshold and focus one highlighted region from the hotspot list
   - open hotspot provenance to narrate why that region diverges
5. Open `Replay` (`Alt+5`) and load timeline frames.
   - focus at least one replay checkpoint and verify checkpoint region highlights on the map
   - open checkpoint provenance to tie replay moment to branch lineage
6. Open `Facilitate` (`Alt+6`) to verify stage controls, roster, queue triage, and continuity actions.
   - choose a presenter and toggle `Follow presenter focus` to confirm shared-attention cues
   - set spotlight from selection and verify attention status remains explicitly local-only
   - run `Refresh room state` and confirm continuity timeline entries render
   - verify session export/import controls remain available for durable handoff
7. Inspect provenance from compare/replay/facilitation context.
8. Use the top-bar `Workspace role` and `Density` selectors:
   - verify facilitator/analyst/delegate/observer presets alter control emphasis without changing runtime APIs
   - verify `presentation` density improves projection readability and keeps map as center of gravity

## Accessibility and hardening checks

- use `Reduced motion` toggle in the top controls (or `Alt+M`)
- verify focus-visible outlines for controls and region boundaries
- verify region navigation via the planning pane `Region navigator`
- verify skip-link behavior to jump directly to workspace content

## Browser E2E and responsiveness checks (WG-P10)

- run browser suite:
  - `python3 -m pytest -q tests/labs/test_world_game_studio_next_browser_e2e.py`
- verify diagnostics in workspace snapshot (`planning-performance-summary`) or from browser console:
  - `window.__WG_STUDIO_NEXT_DIAGNOSTICS`
- responsiveness budgets:
  - map redraw p95 <= `120ms`
  - replay scrub p95 <= `180ms`
  - overlay toggle p95 <= `150ms`

## Notes

- `labs/world_game_studio_next` is the primary showcase surface for demos, workshops, and new UX work.
- `labs/world_game_studio` has been retired and is no longer part of the active demo path.
- `adapters/world_game` remains the runtime/domain source of truth.

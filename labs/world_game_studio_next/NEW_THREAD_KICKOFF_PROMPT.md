# World Game Studio Next New Thread Kickoff Prompt

Copy and paste this at the start of a new Codex thread for `world_game_studio_next`. Fill in bracketed fields before sending.

```text
Project: world-runtime (World Game Studio Next)
Repo root: <repo-root>
Studio package: labs/world_game_studio_next
Domain package dependency: adapters/world_game

You are working inside the world-runtime repository on the active World Game studio build at `labs/world_game_studio_next`.

Before making assumptions, re-read current repository state from disk.

Read these files in this order:
1. labs/world_game_studio_next/STATUS.md
2. labs/world_game_studio_next/ROADMAP.md
3. adapters/world_game/STATUS.md
4. adapters/world_game/ROADMAP.md
5. current files under labs/world_game_studio_next/
6. relevant mirrored design docs under scratch/world-game-design-docs/

Working assumptions:
- Trust repository state on disk over thread memory.
- Do not depend on the retired `labs/world_game_studio` surface.
- Keep business logic in runtime methods rather than recreating simulation or policy behavior in the frontend.
- Treat `adapters/world_game` as the domain and runtime source of truth.
- Do not widen scope beyond the selected `WG-P*` milestone unless a narrow supporting fix is required for correctness.
- If the mirrored scratch docs conflict with repo truth, note the mismatch and proceed from current repo state.

Scope for this thread:
- WG program milestone: [WG-P0 / WG-P1 / WG-P2 / WG-P3 / WG-P4 / WG-P5 / WG-P6]
- Objective: [one concise sentence]
- In scope:
  - [bullet]
  - [bullet]
- Out of scope:
  - [bullet]
  - [bullet]

Before coding:
1. Restate the milestone acceptance criteria in your own words.
2. Identify the files and subsystems expected to change.
3. Identify dependencies on prior `WG-P*` milestones and on current `adapters/world_game` capabilities.
4. State any required runtime/domain follow-ons explicitly before implementing them.
5. Call out whether any historical legacy-studio references were updated in this milestone.

Execution requirements:
1. Implement end-to-end changes within the selected milestone boundary.
2. Do not reintroduce or depend on the retired `labs/world_game_studio` surface.
3. Keep the studio thin relative to runtime logic.
4. If changing a runtime or contract surface, update the related docs/tests in the same thread.
5. Update docs, examples, and playbooks when the supported workflow changes.
6. Do not widen scope with opportunistic cleanup unless required for milestone safety.
7. Prefer small, reviewable edits across the right files.
8. Update `labs/world_game_studio_next/STATUS.md` when the milestone is complete or partially handed off.

Definition of done:
- Milestone objective implemented within scope.
- Acceptance criteria satisfied.
- Relevant validation passes.
- `labs/world_game_studio_next/STATUS.md` updated with completion evidence and the next recommended milestone.
- Deferred follow-ups and unresolved risks listed explicitly.

Validation requirements (run and report in groups):

1. Studio baseline:
- [add studio-local build/test commands for this milestone]
- `find labs/world_game_studio_next -maxdepth 2 \( -type f -o -type d \) | sort`

2. Milestone-specific validation:
- [add milestone-specific commands]

3. Domain/runtime regression checks when shared surfaces changed:
- `python3 scripts/check_adapters.py`
- `python3 scripts/check_examples.py`
- [add targeted pytest or compatibility commands for changed runtime/domain surfaces]

Reporting format:
- Summary of what changed
- Files changed
- Acceptance criteria status
- Validation results
- `labs/world_game_studio_next/STATUS.md` update made
- Unresolved risks
- Deferred follow-ups
- Suggested next milestone

Thread discipline:
- If adjacent improvements are out of scope, list them as follow-ups instead of implementing them.
- If context gets crowded, finish a coherent unit and update `labs/world_game_studio_next/STATUS.md` before handoff.
- Do not mark a milestone complete unless code, validation, and milestone-relevant docs are all in place.
- Keep the active studio track explicit: `labs/world_game_studio_next` is the active showcase surface, the legacy studio is retired, and `adapters/world_game` remains the domain truth.
```

## Optional Add-on: Strict Milestone Gate

```text
Strict milestone gate:
- Do not implement beyond this `WG-P*` milestone boundary in this thread.
- If adjacent improvements are discovered, list them as follow-ups.
- Do not mark the milestone complete unless acceptance criteria and validation requirements pass.
```

## Optional Add-on: Handoff-First Mode

```text
Handoff-first mode:
- Start by checking `labs/world_game_studio_next/STATUS.md` for partial progress on this milestone.
- Reconcile prior handoff with current repo state before coding.
- Prefer completing or stabilizing partial work before starting a parallel path.
- If prior work is inconsistent, document what was kept, changed, and why.
```

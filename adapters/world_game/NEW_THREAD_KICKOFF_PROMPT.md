# World Game New Thread Kickoff Prompt

Copy and paste this at the start of a new Codex thread for `adapter-world-game`. Fill in bracketed fields before sending.

```text
Project: world-runtime (world_game domain package)
Repo root: <repo-root>
Domain package: adapters/world_game

You are working inside the world-runtime repository on the world_game domain package.

Before making assumptions, re-read current repository state from disk.

Read these files in this order:
1. adapters/world_game/STATUS.md
2. adapters/world_game/ROADMAP.md
3. adapters/world_game/README.md
4. adapters/world_game/runtime/engine.py
5. core/app_server.py (world_game.* methods)
6. examples/scenarios/world-game-mini/events.json
7. examples/scenarios/world-game-multi-region/scenario.json

Working assumptions:
- Trust repository state on disk over thread memory.
- If assumptions conflict with repo state, note the mismatch and proceed from current state.
- Treat adapters/world_game/ROADMAP.md as WG strategy, adapters/world_game/STATUS.md as WG execution ledger.

Scope for this thread:
- WG milestone: [WG-M5 / WG-M6 / WG-M7 / ...]
- Objective: [one concise sentence]
- In scope:
  - [bullet]
  - [bullet]
- Out of scope:
  - [bullet]
  - [bullet]

Before coding:
1. Restate milestone acceptance criteria in your own words.
2. Identify files/subsystems expected to change.
3. Call out dependencies on prior WG milestones.
4. Keep work inside the milestone boundary unless a narrow supporting fix is required for correctness.

Execution requirements:
1. Implement end-to-end changes (code/tests/docs/playbooks/examples/schemas when relevant).
2. Do not revert unrelated working-tree changes.
3. Preserve backward compatibility unless this milestone explicitly changes a supported contract.
4. If changing schema or runtime/public surface, update compatibility checks/docs in the same thread.
5. Do not widen scope with opportunistic cleanup unless required for milestone safety.
6. Prefer small reviewable edits across the right files.
7. Keep `adapter-world-game` as the only public world-game showcase surface.

Definition of done:
- Milestone objective implemented within scope.
- Acceptance criteria satisfied.
- Relevant WG validation passes.
- adapters/world_game/STATUS.md updated with completion evidence + next recommended WG milestone.
- Risks/deferred follow-ups listed explicitly.

Validation requirements (run and report in groups):

1. Baseline WG safety:
- python3 scripts/check_adapters.py
- python3 scripts/check_examples.py

2. Milestone-specific validation:
- [add WG milestone-specific commands]

3. WG regression + compatibility:
- python3 -m pytest -q tests/test_world_game_smoke.py tests/test_world_game_examples.py
- python3 -m pytest -q tests/test_world_game_domain.py tests/test_world_game_branches.py tests/test_world_game_replay.py tests/test_world_game_compare.py tests/test_world_game_policies.py
- make protocol-compat
- make public-api-compat

Reporting format:
- Summary of what changed
- File list
- Acceptance criteria status
- Validation results
- adapters/world_game/STATUS.md update made
- Unresolved risks
- Deferred follow-ups
- Suggested next WG milestone

Thread discipline:
- If adjacent improvements are out of scope, list as follow-ups instead of implementing.
- If context gets crowded, finish a coherent unit and update adapters/world_game/STATUS.md before handoff.
- Do not mark milestone complete unless code + validation + docs are all in place.
```

## Optional Add-on: Strict Milestone Gate

```text
Strict milestone gate:
- Do not implement beyond this WG milestone boundary in this thread.
- If adjacent improvements are discovered, list as follow-ups.
- Do not mark milestone complete unless acceptance criteria and validation requirements pass.
```

## Optional Add-on: Handoff-First Mode

```text
Handoff-first mode:
- Start by checking adapters/world_game/STATUS.md for partial progress on this milestone.
- Reconcile prior handoff with current repo state before coding.
- Prefer completing/stabilizing partial work before starting fresh parallel work.
- If prior work is inconsistent, document what was kept, changed, and why.
```

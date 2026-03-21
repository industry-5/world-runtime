# New Thread Kickoff Prompt

Copy and paste this at the start of a new Codex thread. Fill in the bracketed fields before sending.

```
Project: world-runtime
Repo root: <repo-root>

You are working inside the world-runtime repository.

Before making assumptions, re-read the current repository state from disk.

Read these files in this order:
1. STATUS.md
2. ROADMAP.md
3. README.md
4. ARCHITECTURE.md

Working assumptions:
- Trust the current repository state over prior thread memory or earlier assumptions.
- If the repo state conflicts with prior assumptions, note the mismatch explicitly and proceed from the repo as it exists now.
- Treat ROADMAP.md as the strategic source, STATUS.md as the current execution ledger, README.md as the operator-facing entry point, and ARCHITECTURE.md as the system shape reference.

Scope for this thread:
- Milestone: [M18 / M19 / ...]
- Objective: [one concise sentence]
- In scope:
  - [bullet]
  - [bullet]
- Out of scope:
  - [bullet]
  - [bullet]

Before coding:
1. Restate the milestone acceptance criteria in your own words.
2. Identify the files and subsystems you expect to touch.
3. Call out any obvious dependency on prior milestones.
4. Keep the work inside this milestone boundary unless a narrowly-scoped supporting change is required for correctness.

Execution requirements:
1. Implement end-to-end changes, not code-only changes.
   This includes code, tests, docs, playbooks, examples, and schemas or contracts when relevant.
2. Do not revert unrelated working-tree changes.
3. Preserve backward compatibility unless this thread explicitly changes a supported contract.
4. If you change a schema, protocol, public interface, or extension contract, update compatibility checks and docs in the same thread.
5. Do not widen scope through opportunistic cleanup or refactors unless they are required to complete the milestone safely.
6. Prefer small, reviewable edits across the correct files rather than large speculative rewrites.

Definition of done for this thread:
- The milestone objective is implemented within scope.
- Acceptance criteria are satisfied.
- Relevant tests and validation pass.
- Docs, examples, and playbooks are updated where needed.
- STATUS.md is updated with completion evidence, validation results, and the next recommended milestone.
- Any unresolved risks or deferred items are listed explicitly.

Validation requirements:
Run and report validation in three groups.

1. Baseline validation:
- [example: make test]
- [example: make validate]

2. Milestone-specific validation:
- [add milestone-specific commands here]

3. Broader regression validation (run if touched surfaces justify it):
- [example: make evals]
- [example: make examples]
- [example: make adapters]
- [example: make protocol-compat]
- [example: make release-dry-run]

Reporting format at the end:
- Summary of what changed
- File list
- Acceptance criteria status
- Validation results
- STATUS.md update made
- Unresolved risks
- Deferred follow-ups
- Suggested next milestone

Thread discipline:
- If you discover adjacent improvements outside scope, list them as follow-ups instead of implementing them.
- If context becomes crowded, finish the smallest coherent unit of work, update STATUS.md, and prepare a clean handoff summary.
- Do not mark the milestone complete unless code, validation, and documentation changes are all in place.

```

<a id="optional-add-on-strict-milestone-gate"></a>

## Optional Add-on: Strict Milestone Gate

Use this when you want especially tight milestone discipline.

```
Strict milestone gate:
- Do not implement beyond this milestone boundary in this thread.
- If you encounter adjacent improvements, list them as follow-ups instead of implementing them.
- Do not mark the milestone complete unless all stated acceptance criteria and validation requirements pass.

```

<a id="optional-add-on-handoff-first-mode"></a>

## Optional Add-on: Handoff-First Mode

Use this when continuing partially completed work from an earlier thread.

```
Handoff-first mode:
- Start by checking whether STATUS.md already records partial progress for this milestone.
- Reconcile the prior handoff with current repo state before making changes.
- Prefer completing or stabilizing partially finished work over starting fresh parallel work.
- If prior work is incomplete or inconsistent, document what you kept, what you changed, and why.

```

<a id="suggested-usage-notes"></a>

## Suggested usage notes

- Keep the milestone field specific. Avoid vague entries like "cleanup" or "improve runtime."
- Use the out-of-scope section aggressively. It helps prevent drift.
- Add milestone-specific validation every time. Do not rely only on broad repo commands.
- Keep STATUS.md current so the next thread can start from a reliable ledger.

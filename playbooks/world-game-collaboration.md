# Playbook: World Game Collaboration

## Goal

Run `adapter-world-game` as a facilitated, proposal-first planning workflow with actor roles, stage progression, annotations, and provenance inspection.

Use this playbook for the runtime/domain workflow. For the primary showcase UI path, start with [playbooks/world-game-studio-next-demo.md](world-game-studio-next-demo.md).

## When to enable collaboration

Enable the collaboration flow when you want:

- multiple participants with explicit roles
- proposal review before branch mutation
- facilitated workshop stages
- attributable annotations on planning artifacts
- provenance from scenario inputs to branch outcomes

Keep using the direct single-user flow when you only need quick scenario loading, branch creation, and turn execution.

## Roles and capabilities

Default roles include:

- `facilitator` for session management and stage control
- `analyst` for proposal creation, branch work, and simulation
- `observer` for read-oriented participation
- `approver` for adoption/rejection and stage advancement support

Role capabilities are enforced through runtime methods when collaboration mode is enabled.

## Canonical workflow

1. Create a collaboration session with `world_game.session.create`.
2. Add actors with `world_game.session.actor.add`.
3. Load a scenario with `world_game.scenario.load`.
4. Move to `proposal_intake` with `world_game.session.stage.set` or `world_game.session.stage.advance`.
5. Create and submit a proposal with `world_game.proposal.create` and `world_game.proposal.submit`.
6. Advance to `selection`.
7. Adopt the proposal into a branch with `world_game.proposal.adopt`.
8. Advance to `simulation`.
9. Run a turn with `world_game.turn.run`.
10. Add interpretation with `world_game.annotation.create`.
11. Inspect lineage with `world_game.provenance.inspect`.

## Stage progression

Default stages are:

- `setup`
- `proposal_intake`
- `deliberation`
- `selection`
- `simulation`
- `review`
- `closed`

Stage gating is additive. Existing scenario and branch APIs still exist, but collaborative sessions use the stage machine to keep workshop flow explicit.

## Proposal lifecycle

Default proposal states include:

- `draft`
- `submitted`
- `adopted`
- `rejected`
- `archived`

Proposal adoption is the preferred collaborative path into branch mutation because it preserves actor attribution and provenance linkage.

## Annotation target model

Annotations use a simple target reference contract:

- `target_type`
- `target_id`

Typical collaboration targets are:

- branches
- proposals
- sessions

Use annotations to capture risk, opportunity, assumptions, disagreement, evidence gaps, and facilitator notes around simulation outcomes.

## Provenance inspection

Use `world_game.provenance.inspect` to inspect lineage for:

- scenarios
- proposals
- annotations
- branches

In the current implementation, provenance records are additive metadata blocks connected through references. Collaboration durability is still active-session scoped rather than persisted across restarts.

## Minimal validation

- `python3 scripts/check_examples.py`
- `python3 -m pytest -q tests/test_world_game_collaboration.py`
- `python3 -m pytest -q tests/labs/test_world_game_studio_next.py`

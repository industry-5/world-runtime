# World Game Domain Package

`adapter-world-game` is the World Game domain package and runtime source of truth for the primary showcase stack in `world-runtime`.

## Purpose

- provide a runtime-native, branch-first world-game domain
- support deterministic turn execution, replay, and branch comparison
- support proposal-first collaborative planning, facilitation, annotations, and provenance inspection
- power the World Game showcase surfaces, especially `labs/world_game_studio_next`, without moving domain authority into frontend code
- keep domain governance and execution hygiene local to this package

## Boundaries

- domain-specific contracts, fixtures, and policy packs live under `adapters/world_game/`
- runtime and reporting logic live under `adapters/world_game/runtime/` and `adapters/world_game/reporting/`
- authoring workflows live under `adapters/world_game/authoring/`
- collaboration workflows live under `adapters/world_game/collaboration/`
- showcase UI and demo experience live in `labs/world_game_studio_next`
- runtime method surface integration lives in `core/app_server.py`, which delegates to `adapters/world_game/service.py`
- root-level docs keep only rollup pointers; detailed WG tracking is domain-local

## Package Map

- `adapter.py` - adapter contract implementation (`adapter-world-game`)
- `schemas/` - domain schemas (`scenario`, `intervention`, `shock`, `comparison_report`, etc.)
- `schemas/` - domain + authoring schemas (`scenario_template`, `template_bundle`, `indicator_registry`, libraries)
- `collaboration/` - actor/session/proposal/facilitation/annotation/provenance helpers
- `topology/` - semantic topology contract seeds and scenario-binding metadata for studio map integration
- `policies/` - default and packaged policy rules
- `fixtures/` - scenario/intervention/shock fixture catalogs
- `ROADMAP.md` - WG milestone roadmap
- `STATUS.md` - WG execution ledger and validation evidence
- `NEW_THREAD_KICKOFF_PROMPT.md` - domain-specific kickoff template for new implementation threads

## Runtime Methods

World-game runtime methods are callable via runtime-call and handled in `core/app_server.py`:

- Scenario and simulation:
  - `world_game.scenario.list`
  - `world_game.scenario.load`
  - `world_game.turn.run`
  - `world_game.branch.create`
  - `world_game.branch.compare`
  - `world_game.replay.run`
  - `world_game.network.inspect`
  - `world_game.equity.report`
- Collaboration sessions:
  - `world_game.session.create`
  - `world_game.session.get`
  - `world_game.session.actor.add`
  - `world_game.session.actor.remove`
  - `world_game.session.actor.list`
  - `world_game.session.stage.get`
  - `world_game.session.stage.set`
  - `world_game.session.stage.advance`
  - `world_game.session.export`
  - `world_game.session.import`
- Proposal workflow:
  - `world_game.proposal.create`
  - `world_game.proposal.update`
  - `world_game.proposal.get`
  - `world_game.proposal.list`
  - `world_game.proposal.submit`
  - `world_game.proposal.adopt`
  - `world_game.proposal.reject`
- Interpretation and traceability:
  - `world_game.annotation.create`
  - `world_game.annotation.list`
  - `world_game.annotation.update`
  - `world_game.annotation.archive`
  - `world_game.provenance.inspect`
- Authoring:
  - `world_game.authoring.template.list`
  - `world_game.authoring.draft.create`
  - `world_game.authoring.draft.validate`
  - `world_game.authoring.bundle.publish`
  - `world_game.authoring.bundle.instantiate`

Replay payload note:

- `world_game.replay.run` returns summary parity fields and additive `replay_frames` data (`turn_index`, score/equity/network diagnostics) for scrub-linked studio replay views without client-side simulation logic.

## WG-M11 to WG-M15 Collaboration Arc

Phase 4 and 5 runtime additions keep the existing simulation/authoring path intact while adding:

- actor-aware World Game sessions and timeline-safe collaborative state
- proposal-first planning before branch mutation
- facilitation stage gating for workshop progression
- structured annotations on proposals, branches, and related artifacts
- provenance inspection for scenarios, proposals, annotations, and branches

Collaboration state remains service-managed and session-scoped for this arc. When collaboration is enabled, stage transitions and actor capabilities are enforced through runtime methods rather than frontend logic.

## How Collaboration Works

The canonical collaborative workflow is:

1. Create a World Game collaboration session with `world_game.session.create`.
2. Add actors and roles with `world_game.session.actor.add`.
3. Move the workshop into the right stage with `world_game.session.stage.set` or `world_game.session.stage.advance`.
4. Create and submit a proposal before mutating branches with `world_game.proposal.create` and `world_game.proposal.submit`.
5. Adopt the proposal into a branch with `world_game.proposal.adopt`.
6. Run the simulated turn on that branch with `world_game.turn.run`.
7. Capture interpretation with `world_game.annotation.create`.
8. Inspect lineage with `world_game.provenance.inspect`.

This layer is additive. Existing single-user flows still work:

- direct `world_game.scenario.load` -> `world_game.turn.run` remains valid
- direct `world_game.branch.create` still exists
- stage gating applies only when collaboration mode is enabled
- collaboration state can now be exported/imported with `world_game.session.export` / `world_game.session.import` for durability beyond a single runtime process

If you want a guided evaluator walkthrough for the collaborative flow, use [playbooks/world-game-collaboration.md](../../playbooks/world-game-collaboration.md).

Core domain behaviors used by these methods are implemented inside this package and exposed through `adapters/world_game/service.py`.

Phase 2 scenarios can optionally include:

- `dependency_graph` (DAG nodes/edges)
- `resource_stocks` and `resource_flows`
- `spillover_rules`
- `equity_dimensions`

When present, `world_game.turn.run` includes deterministic network diagnostics and equity reporting while remaining backward-compatible with direct-effects-only scenarios.

WG-P1 studio-contract placement for topology is now explicit:

- semantic topology contracts: `adapters/world_game/topology/`
- Dymaxion geometry package shape/docs: `labs/world_game_studio_next/assets/world_game_map/`

## Scenarios

Primary scenario assets:

- `examples/scenarios/world-game-mini/`
- `examples/scenarios/world-game-multi-region/`

Authoring template bundle example:

- `examples/world-game-authoring/template_bundle.multi-region.v1.json`

WG-M10 reusable template packs:

- `examples/world-game-authoring/template_bundle.multi-region-stress.v1.json`
- `examples/world-game-authoring/template_bundle.resilience-first-regional-planning.v1.json`

## WG-M9 Authoring Workflows

WG-M8/WG-M9 authoring primitives and workflows include:

- schema validation helper: `validate_world_game_template_bundle`
- deterministic bundle loader: `load_world_game_template_bundle`
- deterministic scenario materializer: `instantiate_world_game_template_bundle`
- workflow validation helper (schema + semantics): `validate_world_game_template_bundle_workflow`
- draft scaffold helper: `create_world_game_template_bundle_draft`
- publish helper: `publish_world_game_template_bundle`
- template discovery helper: `list_world_game_template_bundles`

These helpers live in `adapters/world_game/authoring/` and produce concrete scenario payloads that remain compatible with `world_game.scenario.load` / `world_game.turn.run`.

CLI entrypoint:

- `python3 scripts/world_game_authoring.py template-list`
- `python3 scripts/world_game_authoring.py scaffold --source-bundle examples/world-game-authoring/template_bundle.multi-region.v1.json --output-path /tmp/wg.draft.json`
- `python3 scripts/world_game_authoring.py validate --bundle-path /tmp/wg.draft.json`
- `python3 scripts/world_game_authoring.py publish --bundle-path /tmp/wg.draft.json --output-path /tmp/wg.published.json`
- `python3 scripts/world_game_authoring.py instantiate --bundle-path /tmp/wg.published.json --template-id template.wg.multi-region.core.v1 --param region_count=2 --param scenario_suffix=sample --scenario-output-path /tmp/wg.scenario.json`

## WG-M10 Playbooks

- `adapters/world_game/playbooks/template-authoring-rules.md`
- `adapters/world_game/playbooks/library-authoring-rules.md`
- `adapters/world_game/playbooks/publish-instantiate-workflow.md`

## Validation Bundle

Use this bundle for WG-focused verification:

```bash
python3 scripts/check_adapters.py
python3 scripts/check_examples.py
python3 -m pytest -q tests/test_world_game_smoke.py tests/test_world_game_examples.py
```

Common deeper WG checks:

```bash
python3 -m pytest -q tests/adapters/world_game/test_domain.py tests/adapters/world_game/test_branches.py tests/adapters/world_game/test_replay.py tests/adapters/world_game/test_compare.py tests/adapters/world_game/test_policies.py
```

Collaboration-focused checks:

```bash
python3 -m pytest -q tests/test_world_game_collaboration.py tests/labs/test_world_game_studio_next.py
```

## Showcase Positioning

`adapter-world-game` is the only public world-game adapter surface in this repository. Lightweight scenario variants should be added as scenario packs under `world_game`, not as separate compatibility adapters.

`labs/world_game_studio_next` is the primary showcase surface for demos, workshops, and new UX work. This package remains authoritative for the World Game domain behavior, runtime methods, scenarios, authoring workflows, and provenance/collaboration contracts behind that experience.

The root `world-runtime` docs remain the source for repo-wide support posture and stable-surface commitments. `labs/world_game_studio` has been retired after stabilization and remains relevant only in historical milestone records.

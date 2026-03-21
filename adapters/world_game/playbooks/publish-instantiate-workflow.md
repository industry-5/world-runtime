# World Game Publish and Instantiate Workflow

WG authoring uses a deterministic draft-to-runtime flow.

## 1. Discover Template Packs

```bash
python3 scripts/world_game_authoring.py template-list
```

Use this to select a source pack/template before editing.

## 2. Create Draft Bundle

```bash
python3 scripts/world_game_authoring.py scaffold \
  --source-bundle examples/world-game-authoring/template_bundle.multi-region-stress.v1.json \
  --output-path /tmp/wg.draft.json \
  --bundle-id wg.authoring.bundle.operator-team.v1
```

## 3. Validate Draft (Schema + Semantics)

```bash
python3 scripts/world_game_authoring.py validate --bundle-path /tmp/wg.draft.json
```

Validation must pass before publishing.

## 4. Publish Deterministically

```bash
python3 scripts/world_game_authoring.py publish \
  --bundle-path /tmp/wg.draft.json \
  --output-path /tmp/wg.published.json
```

Publish output returns stable `published_bundle_id` for identical inputs.

## 5. Instantiate Scenario

```bash
python3 scripts/world_game_authoring.py instantiate \
  --bundle-path /tmp/wg.published.json \
  --template-id template.wg.multi-region.dependency-stress.v1 \
  --param region_count=3 \
  --param scenario_suffix=ops-smoke \
  --scenario-output-path /tmp/wg.scenario.json
```

## 6. Execute Runtime Smoke Path

```bash
python3 -m pytest -q tests/test_world_game_smoke.py tests/labs/test_world_game_studio_next.py
```

The generated scenario must remain replay-safe and branch-compare compatible.

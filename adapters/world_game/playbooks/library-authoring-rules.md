# World Game Library Authoring Rules

This playbook covers indicator, intervention, and shock libraries inside WG template bundles.

## Indicator Registries

- Define indicators with stable IDs, bounds, directionality, and default weights.
- Keep a full registry and optionally a compact registry when operator workflows need lighter configs.
- Ensure every baseline indicator seed in `region_pool` can render for each supported registry.

## Intervention Libraries

- Keep IDs unique and deterministic (`intervention.*`).
- Ensure `applicable_regions` use IDs from template `region_pool`.
- Keep `direct_effects` and `tradeoffs` indicator references aligned with bundle registries.
- Only include prerequisites that exist in the same library.

## Shock Libraries

- Keep IDs unique and deterministic (`shock.*`).
- Ensure shock `effects` reference valid regions and indicators.
- Keep shock schedules compatible with `time_horizon.turn_count`.

## Reusability Rules

- Design libraries to survive template filtering:
  - region filtering via `region_count`
  - indicator filtering via alternate `indicator_registry_ref`
- Prefer additive changes when evolving libraries; avoid mutating historical IDs in-place.

## Quality Gate

Use workflow validation before publishing:

```bash
python3 scripts/world_game_authoring.py validate --bundle-path <bundle.json>
python3 scripts/world_game_authoring.py publish --bundle-path <bundle.json>
```

Validation must return path-specific issues; unresolved errors should block publish.

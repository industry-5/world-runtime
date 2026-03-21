# World Game Template Authoring Rules

This playbook defines the minimum authoring contract for `scenario_templates` in WG template bundles.

## Required Contract

- Every template must include: `template_id`, `label`, `description`, `parameter_model`, `scenario_id_template`, `baseline_version_template`, `time_horizon`, `region_pool`, and library/policy reference templates.
- `parameter_model.parameters` must use stable names and explicit type constraints (`string`, `integer`, `number`, `boolean`).
- `scenario_id_template` and `baseline_version_template` must remain deterministic for identical parameter values.

## Parameter Design

- Prefer reusable parameters: `region_count`, `scenario_suffix`, `start_year`, registry/library refs, and `policy_pack_ref`.
- For values operators are expected to switch, provide `default` and `enum` when possible.
- Reserve parameters for author-facing controls only; avoid leaking runtime internal state.

## Region and Indicator Reuse

- `region_pool` should include complete baseline indicator seeds so templates can be instantiated without manual patching.
- Keep indicator references aligned with one or more indicator registries in the same bundle.
- Keep `region_count` bounded by `region_pool` size to avoid invalid instantiations.

## Optional Networked Fields

For dependency-aware templates, include any of:

- `dependency_graph_template`
- `resource_stocks_template`
- `resource_flows_template`
- `spillover_rules_template`
- `equity_dimensions_template`

These fields must remain valid after region filtering (`region_count`) and indicator filtering (`indicator_registry_ref`).

## Validation Gate

Before publish, always run both:

```bash
python3 scripts/world_game_authoring.py validate --bundle-path <bundle.json>
python3 scripts/world_game_authoring.py instantiate --bundle-path <bundle.json> --template-id <template_id> --param scenario_suffix=smoke-check
```

If either command fails, fix template contracts before publishing.

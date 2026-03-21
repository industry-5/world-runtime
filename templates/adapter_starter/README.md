# __ADAPTER_NAME__ Adapter Starter

This starter package provides a minimal World Runtime domain adapter scaffold.

## Generated identity

- `adapter_id`: `__ADAPTER_ID__`
- Python package slug: `__ADAPTER_SLUG__`

## Integration steps

1. Move this directory under `adapters/__ADAPTER_SLUG__/`.
2. Register `__ADAPTER_NAME__Adapter` in `adapters/registry.py`.
3. Point your scenario path to `examples/scenarios/__ADAPTER_SLUG__-mini/`.
4. Add policy and schema files to your onboarding/release checklist.
5. Run `make adapters` and `make extension-contracts`.

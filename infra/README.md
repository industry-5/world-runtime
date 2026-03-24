# Reference Deployments

Milestone 10 adds reproducible reference deployment assets.

## Profiles

- `infra/profiles/local.profile.json`: local-first profile that runs out of the box.
- `infra/profiles/dev.profile.json`: shared development profile with reference backend/provider settings.

## Configs

- `infra/config/persistence.local.json`
- `infra/config/persistence.dev.json`
- `infra/config/llm.local.json`
- `infra/config/llm.dev.json`

## Adapter Deployment Examples

- `infra/deployments/supply-network.local.json`

## Integration Reference Stacks (M15)

- `infra/integration_stacks/supply-network.erp-sync.local.json`

## Smoke Commands

```bash
make migrate-local
make migrate-dev
make deploy-local
make deploy-dev
make integration-stacks
```

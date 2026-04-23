# Reference Deployments

This directory holds reproducible reference deployment assets.

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

## Integration Reference Stacks

- `infra/integration_stacks/supply-network.erp-sync.local.json`

## Managed Service Manifests

- `infra/service_manifests/reference-http.json`: minimal managed helper service used for runtime-host supervision smoke validation.
- `infra/service_manifests/world-runtime.local.json`: supported `python -m world_runtime serve` local runtime example managed through the runtime supervisor substrate.

## Provider Registry And Task Profiles

- `infra/provider_bindings/`: provider inventory manifests that bind generic capabilities to managed service dependencies, quality/cost/latency tiers, and routing scope tags.
- `infra/task_profiles/`: task intent manifests that define required capabilities, output expectations, bounded fallback behavior, and approval sensitivity without hard-coding provider families.

## Smoke Commands

```bash
make migrate-local
make migrate-dev
make deploy-local
make deploy-dev
make integration-stacks
make service-host-smoke
make provider-inventory
make task-routing
```

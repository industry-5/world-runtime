# World Runtime Public API v1

This is the supported external HTTP surface for World Runtime.

## Versioning and compatibility

- Public API version: `v1`
- Backing App Server protocol: `1.0`
- Compatibility policy: major-compatible (`v1.x` clients remain supported across `v1` server minors)

## Endpoints

- `GET /health` - unauthenticated liveness
- `GET /v1/meta` - API/protocol compatibility metadata
- `POST /v1/runtime/call` - generic method bridge for advanced users
- `POST /v1/sessions` - create runtime session
- `GET /v1/runtime/inventory` - runtime inventory summary
- `GET /v1/runtime/services` - managed runtime service inventory
- `GET /v1/runtime/services/{service_id}` - inspect one managed runtime service
- `POST /v1/runtime/services/reconcile` - bounded reconcile for managed services
- `GET /v1/runtime/providers` - provider inventory summary
- `GET /v1/runtime/providers/{provider_id}` - inspect one provider entry
- `POST /v1/runtime/tasks/resolve` - resolve a task profile against eligible providers
- `POST /v1/proposals/submit` - submit proposal + policy evaluation
- `POST /v1/simulations/run` - create/run simulation with hypothetical events
- `POST /v1/approvals/respond` - approve/reject/escalate/override an approval request
- `POST /v1/connectors/inbound/run` - run inbound connector flow
- `POST /v1/connectors/outbound/run` - run outbound connector flow
- `GET /v1/observability/telemetry/summary` - observability summary surface

For a first local API run:

```bash
python -m world_runtime serve --profile local
make sdk-example
```

The runtime-call bridge may expose adapter-specific methods in some repo builds, but those domain-specific runtime methods are not part of the baseline public `/v1` contract unless they are documented here.

## Authentication and configuration

- Local profile: run without bearer auth for local-only development.
- Dev profile: set `WORLD_RUNTIME_API_TOKEN` and send `Authorization: Bearer <token>`.
- API base URL default for local examples: `http://127.0.0.1:8080`.

## Deprecation notes

- `core.app_server.WorldRuntimeAppServer.handle_request` remains supported for internal/in-process usage.
- External clients should prefer Public API `v1` or the SDK surface.
- Breaking public changes require a new API major (`v2`).

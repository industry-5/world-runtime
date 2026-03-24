# Compatibility Matrix

This matrix defines supported compatibility expectations for M24 onboarding.

| Surface | Current contract | Compatibility policy | Validation command |
| --- | --- | --- | --- |
| Runtime/App Server wire protocol | `APP_SERVER_PROTOCOL.md` + `schemas/app_server.*.schema.json` | Major-version compatible | `make protocol-compat` |
| Public API | `api/PUBLIC_API_V1.md` (`/v1`) | Additive changes in v1, breaking changes require new major API version | `make public-api-compat` |
| Python SDK | `sdk/python_client.py` + `sdk/README.md` | Mirrors supported Public API v1 endpoints | `make public-api-compat` |
| Persistence migrations | `infra/migrations/persistence/` | Forward-only ordered migrations; no in-place rewrite of applied migration files | `make recovery-check` |
| Connector plugin contract | `core.connector_transports.TransportPlugin` | `provider` + `send(payload, attempt, auth, options)` contract stability | `make extension-contracts` |
| Adapter contract | `adapters.base.DomainAdapter` | Required abstract members stable; additive methods allowed | `make extension-contracts` |
| Policy packs | `schemas/policy.schema.json` | Schema-governed with additive fields preferred | `make schemas` |
| Simulation records | `schemas/simulation.schema.json` | Schema-governed with additive optional fields | `make schemas` |

## Version notes

- Runtime protocol version source: `core/app_protocol.py`.
- Public API major version source: `api/runtime_api.py` and `api/PUBLIC_API_V1.md`.
- Release artifacts include this matrix to support partner handoff.

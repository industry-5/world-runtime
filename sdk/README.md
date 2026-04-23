# World Runtime SDK Starter (Python)

## Scope

The starter SDK wraps the public HTTP API `v1` and avoids importing internal runtime modules.

For the fastest local smoke path:

```bash
python -m world_runtime serve --profile local
make sdk-example
```

## Client

- Class: `world_runtime.sdk.WorldRuntimeSDKClient`
- Default API version: `v1`
- Default usage:

```python
from world_runtime.sdk import WorldRuntimeSDKClient

client = WorldRuntimeSDKClient(base_url="http://127.0.0.1:8080")
session = client.create_session()
```

Supported downstream import boundary:

- use `world_runtime.sdk` from an installed package
- do not treat `sdk.python_client` as the supported downstream import path
- use the additive runtime-admin helpers from the SDK for runtime inventory, provider inspection, task resolution, and bounded reconcile instead of importing `core.runtime_host` or routing internals directly
- the M30 local AI reference stack is bootstrapped through these same runtime-admin helpers; the local stack manifests and reference extraction engine remain operator-facing reference assets rather than a new stable SDK contract

## Supported starter methods

- `create_session`
- `runtime_inventory`
- `list_runtime_services`
- `get_runtime_service`
- `reconcile_runtime_services`
- `list_runtime_providers`
- `get_runtime_provider`
- `resolve_runtime_task`
- `submit_proposal`
- `run_simulation`
- `respond_approval`
- `run_connector_inbound`
- `run_connector_outbound`
- `telemetry_summary`
- `call_runtime`

## Auth configuration

- Local: omit `api_token`.
- Dev: pass `api_token` and configure `WORLD_RUNTIME_API_TOKEN` on the server.

`reconcile_runtime_services` is the only baseline v1.1 mutating runtime-admin helper. Pass an actor payload that includes the `runtime.service.reconcile` capability, and optionally pass a `session_id` if you want the reconcile action to appear in the existing audit-export flow.

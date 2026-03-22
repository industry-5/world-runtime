# World Runtime SDK Starter (Python)

## Scope

The starter SDK wraps the public HTTP API `v1` and avoids importing internal runtime modules.

For the fastest local smoke path:

```bash
make api-server
make sdk-example
```

## Client

- Class: `sdk.python_client.WorldRuntimeSDKClient`
- Default API version: `v1`
- Default usage:

```python
from sdk.python_client import WorldRuntimeSDKClient

client = WorldRuntimeSDKClient(base_url="http://127.0.0.1:8080")
session = client.create_session()
```

## Supported starter methods

- `create_session`
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

# Consumer Integration Guide

This guide defines the supported downstream-consumer boundary for installing and running `world-runtime` as a pinned dependency.

`world-runtime` is now released as `v1.1.0` GA. The supported package-consumption path sits on top of the existing compatibility commitments for the App Server protocol, Public API `/v1`, Python SDK starter, persistence migrations, and extension contracts.

## Supported Consumption Modes

### Tier A: Supported external client usage

This is the default recommendation for downstream products.

- run the supported local server entrypoint:
  - `python -m world_runtime serve --profile local`
  - `world-runtime serve --profile local`
- integrate through:
  - Public API `/v1`
  - `world_runtime.sdk`
  - App Server protocol via the supported server surface
  - additive runtime-admin inventory, provider inspection, task resolution, and bounded reconcile through those supported surfaces

### Tier B: Supported package-hosted local runtime

Use this when a downstream repo wants to supervise a local `world-runtime` process as a pinned dependency.

- pin an exact package version such as `world-runtime==1.1.0` in your package source of record
- install the package into the downstream environment rather than importing repo-local files
- start the runtime through the supported module or console entrypoint
- call the runtime through the supported HTTP API or SDK

Example:

```bash
python -m pip install world-runtime==1.1.0
world-runtime serve --profile local --host 127.0.0.1 --port 8080
```

Python client example:

```python
from world_runtime.sdk import WorldRuntimeSDKClient

client = WorldRuntimeSDKClient(base_url="http://127.0.0.1:8080")
session = client.create_session()
```

Managed-service supervision and provider/task routing can supervise and resolve the supported serve path internally, but the stable downstream contract remains the installed serve entrypoints plus the supported HTTP/API/SDK surfaces.
The released runtime-admin read surfaces plus bounded reconcile build on that existing App Server, `/v1`, and SDK contract instead of widening direct-import support for the host/router internals.
The local AI structured-extraction reference stack can be started and inspected through those supported runtime-admin surfaces, while the stack manifest, managed extraction service, and routing inventory remain best-effort/operator-facing assets rather than a new stable embedding API.

### Tier C: Internal runtime embedding

This is not a supported downstream contract in the current release.

- do not treat direct imports from runtime internals as a stable downstream embedding API
- `core.app_server.WorldRuntimeAppServer.handle_request` remains supported for internal and in-process repo usage, but it is not the preferred or supported downstream integration contract
- if a stable embedding facade is needed later, it should land as an explicit future release or declared public contract instead of growing accidentally out of convenience imports

## Supported Downstream Boundary

Supported for downstream repos:

- pinned package installation of `world-runtime`
- `python -m world_runtime serve`
- `world-runtime serve`
- Public API `/v1` documented in [api/PUBLIC_API_V1.md](../api/PUBLIC_API_V1.md)
- Python SDK starter via `world_runtime.sdk`

Not supported for downstream repos:

- direct imports from `core/*`
- direct imports from `core.runtime_host` or other service-host internals as a stable embedding API
- direct imports from `core.task_router`, `core.provider_registry`, `core.task_profiles`, or other routing internals as a stable embedding API
- direct imports from `api/*`
- direct imports from `sdk/*`
- file-path loading of runtime internals from another checkout
- assumptions about repo-root `make` commands
- assumptions about repository folder layout or vendored source placement
- experimental surfaces unless they are explicitly promoted in project docs

## Serve Entrypoint Notes

Supported serve entrypoint options:

- `--profile`
- `--host`
- `--port`
- `--api-token` or `WORLD_RUNTIME_API_TOKEN`

Profile guidance:

- `local`: local-only development; bearer auth is optional
- `dev`: bearer auth is required

Repo contributors may still use `make api-server`, but that target is a repository convenience wrapper around the supported package entrypoint, not the primary downstream contract.

## Consumer Smoke Path

The repository validates the supported consumer boundary with:

- `examples/consumers/python_package_smoke.py`
- `scripts/check_consumer_smoke.py`
- `make consumer-smoke`
- `make m26-validate`

The smoke path proves:

- isolated package installation
- supported serve startup without repo-root assumptions
- `GET /health`
- `GET /v1/meta`
- one supported SDK call

## Compatibility Notes

- The App Server protocol remains major-version compatible.
- Public API `/v1` remains additive.
- The Python SDK starter continues to track the supported `/v1` API surface.
- Runtime-admin methods/endpoints stay additive and do not make `core.runtime_host`, `core.provider_registry`, `core.task_profiles`, or `core.task_router` into supported downstream imports.
- Persistence migrations and extension contracts remain under their existing compatibility rules.

This guide does not widen the stable contract to arbitrary internal Python modules.

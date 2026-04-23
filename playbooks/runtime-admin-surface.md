# Runtime-Admin Surface

Use the M29 runtime-admin surface when you need to inspect managed runtime state through supported interfaces instead of direct imports from `core.runtime_host`, `core.provider_registry`, `core.task_profiles`, or `core.task_router`.

## What It Covers

- runtime inventory summary
- managed-service inventory
- provider inventory
- task-resolution inspection
- bounded reconcile through supported surfaces

Read surfaces stay distinct from mutate surfaces. `runtime.service.reconcile` is the only baseline v1.1 mutating runtime-admin action.

## Supported Entry Points

App Server methods:

- `runtime.inventory.summary`
- `runtime.service.list`
- `runtime.service.get`
- `runtime.service.reconcile`
- `runtime.provider.list`
- `runtime.provider.get`
- `runtime.task.resolve`

Public API `/v1` endpoints:

- `GET /v1/runtime/inventory`
- `GET /v1/runtime/services`
- `GET /v1/runtime/services/{service_id}`
- `POST /v1/runtime/services/reconcile`
- `GET /v1/runtime/providers`
- `GET /v1/runtime/providers/{provider_id}`
- `POST /v1/runtime/tasks/resolve`

SDK starter helpers:

- `runtime_inventory`
- `list_runtime_services`
- `get_runtime_service`
- `reconcile_runtime_services`
- `list_runtime_providers`
- `get_runtime_provider`
- `resolve_runtime_task`

## Reconcile Guardrails

- Reconcile requires an actor payload with the `runtime.service.reconcile` capability.
- Pass `session_id` when you want reconcile activity to appear in the existing audit-export flow.
- Keep reconcile bounded by explicitly naming `service_ids` unless you intentionally want all registered service manifests reconciled.
- Do not treat reconcile as a generic `start` / `stop` / `restart` API. Those mutators remain out of scope for the M29 baseline.

## Typical Flow

1. Inspect `GET /v1/runtime/inventory` or `runtime.inventory.summary`.
2. Inspect one or more services/providers.
3. Run `runtime.task.resolve` or `POST /v1/runtime/tasks/resolve` to see the current routing decision and trace.
4. Reconcile the specific managed service dependency you need.
5. Re-run task resolution and confirm the selected provider and dependency state.

The M30 local AI reference stack follows this exact flow:

1. reconcile `reference-local-ai-extraction`
2. inspect `reference-local-structured-extraction-high` and `reference-local-structured-extraction-balanced`
3. resolve `structured-extraction.local-reference`
4. inspect the route trace and then run the extraction fixture against the managed service endpoint

## Validation

Run the milestone smoke and aggregate validation:

```bash
make runtime-admin-smoke
make m29-validate
```

The smoke path writes:

- `tmp/diagnostics/m29_runtime_admin.latest.json`

It verifies:

- App Server runtime-admin methods
- matching Public API `/v1` endpoints
- SDK starter runtime-admin helpers
- reconcile observability
- session-bound audit capture for reconcile

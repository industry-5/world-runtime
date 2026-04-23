# Runtime Service Host

Use the M27 managed runtime host when you need `world-runtime` to start, inspect, and reconcile local runtime-adjacent processes from declarative manifests.

## What It Covers

- service manifest authoring
- desired-state reconcile flow
- readiness and health probe semantics
- deterministic restart behavior
- lifecycle telemetry and diagnostics capture

This playbook is intentionally operator-facing. `M29` now exposes supported runtime-admin read/reconcile surfaces over this substrate; use [runtime-admin-surface.md](runtime-admin-surface.md) for the supported App Server, `/v1`, and SDK entry points.

## Reference Assets

- Schema: `schemas/service_manifest.schema.json`
- Reference helper manifest: `infra/service_manifests/reference-http.json`
- Local runtime manifest: `infra/service_manifests/world-runtime.local.json`
- Local AI extraction manifest: `infra/service_manifests/reference-local-ai-extraction.json`
- Diagnostics script: `scripts/check_service_host.py`
- Reference helper process: `scripts/reference_managed_service.py`
- Reference local AI process: `scripts/reference_local_ai_extraction_service.py`

## Manifest Shape

Each service manifest stays descriptive rather than policy-bearing.

Required sections:

- `service_id`
- `process`
- `restart_policy`
- `log_capture`

Optional but expected for operable services:

- `readiness_probe`
- `health_probe`
- `dependencies`
- `outputs`

Portable manifests should use environment placeholders such as `${REPO_ROOT}`, `${PYTHON}`, or runtime-selected ports instead of hard-coding machine-specific paths.

## Start and Reconcile Flow

1. Load one or more manifests.
2. Resolve dependency order.
3. Start missing services in dependency order.
4. Wait for readiness before treating a dependency as usable.
5. Reconcile running services against the desired manifest set.
6. Stop services that are no longer desired.

The current host implementation is a desired-state reconciler. It can be called directly from scripts or periodic supervisory loops without introducing a second policy system.

## Readiness and Health

- Readiness means the service can accept work.
- Health means the service is still operating within its expected envelope.
- A process can be alive but not ready.
- A process can be running but unhealthy and therefore restartable.

Available probe types:

- `http`
- `command`
- `tcp`

## Restart Semantics

Restart behavior is controlled only by `restart_policy`:

- `condition`: `never`, `on_failure`, or `always`
- `max_attempts`: bounded retry count
- `backoff_seconds`: deterministic delay between retries

Failures that count for restart purposes include:

- process exit before or after readiness
- readiness timeout
- health-probe failure

## Failure States

Common failure modes surfaced in state and diagnostics:

- `process exited with code N before readiness`
- `readiness timeout after ...`
- `health probe failed: ...`
- `dependencies not ready: ...`

Service state snapshots record:

- lifecycle state
- pid
- restart count
- readiness and health state
- last failure reason
- last exit code
- probe results
- log capture paths

## Diagnostics Capture

Run the milestone smoke path:

```bash
make service-host-smoke
```

The smoke script writes:

- `tmp/diagnostics/m27_service_host.latest.json`

It validates:

- manifest-to-readiness supervision
- controlled exit and deterministic restart
- health failure detection and restart
- failed-start diagnostics
- lifecycle telemetry emission

## Operational Notes

- Keep manifests domain-neutral. They should describe process supervision, not routing policy.
- When a routed provider depends on a managed service, reference the manifest `service_id` from the provider binding instead of embedding routing choices into the service manifest itself.
- Prefer supported serve entrypoints such as `python -m world_runtime serve` inside manifests when supervising the runtime itself.
- The M30 reference local AI stack uses this same substrate for `reference-local-ai-extraction`; inspect and reconcile it through the supported runtime-admin surfaces rather than building a second supervision path.
- Treat direct imports from `core.runtime_host` as repo/operator tooling, not as a widened stable downstream package API.

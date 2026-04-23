# Reference Local AI Structured Extraction

Use this playbook when you want to bootstrap the M30 reference local AI stack that is tuned for schema-constrained structured extraction instead of open-ended chat behavior.

## What It Proves

- managed local service hosting through the M27 runtime host
- extraction-specific provider/task routing through the M28 router
- supported runtime-admin inspection and reconcile through the M29 App Server, Public API `/v1`, and SDK helpers
- schema-valid structured extraction outputs with deterministic structure checks and diagnostics

## Reference Assets

- Integration stack manifest: `infra/integration_stacks/local_ai_structured_extraction.json`
- Managed service manifest: `infra/service_manifests/reference-local-ai-extraction.json`
- Provider bindings:
  - `infra/provider_bindings/reference-local-structured-extraction-high.json`
  - `infra/provider_bindings/reference-local-structured-extraction-balanced.json`
- Task profile: `infra/task_profiles/structured-extraction.local-reference.json`
- Eval fixtures: `examples/evals/structured_extraction/`
- Smoke script: `scripts/check_structured_extraction_stack.py`
- Diagnostics artifact: `tmp/diagnostics/m30_local_ai_structured_extraction.latest.json`

## Bootstrap

1. Install dependencies: `make install`
2. Run the supported runtime baseline first when needed: `make validate`
3. Start and validate the local AI stack through the milestone smoke path:

```bash
make structured-extraction-smoke
```

The smoke path reconciles the managed local extraction service through the runtime-admin surface, resolves the extraction task profile, runs the structured extraction fixtures, validates schema compliance, and writes the M30 diagnostics artifact.

## Supported Inspection Flow

The stack should be inspected through the additive runtime-admin surfaces, not by importing host or router internals in downstream code.

- App Server methods:
  - `runtime.service.reconcile`
  - `runtime.service.get`
  - `runtime.task.resolve`
- Public API `/v1`:
  - `GET /v1/runtime/services/{service_id}`
  - `POST /v1/runtime/tasks/resolve`
- SDK helpers:
  - `get_runtime_service`
  - `reconcile_runtime_services`
  - `resolve_runtime_task`

The smoke path exercises all three supported entry paths before calling the managed extraction endpoint.

## Hardware Envelope

- The bundled reference extraction engine is intentionally lightweight and CPU-friendly.
- It is designed to prove the managed-service, routing, runtime-admin, and diagnostics workflow on a normal developer laptop.
- Downstream adopters can swap the managed service manifest and provider bindings for a real local model engine later without changing the stable App Server, Public API `/v1`, or SDK contracts.

## First-Run Validation

Run the milestone gate:

```bash
make m30-validate
```

This bundles:

- `make integration-stacks`
- `make evals`
- `make observability`
- `make structured-extraction-smoke`

## Failure Recovery

Common failure modes to inspect:

- managed service fails before readiness:
  - inspect `tmp/service_logs/reference-local-ai-extraction.stdout.log`
  - inspect `tmp/service_logs/reference-local-ai-extraction.stderr.log`
- routing resolves `no_route`:
  - confirm `reference-local-ai-extraction` is `ready`
  - confirm the task profile and provider bindings still share `extraction_reference_stack`, `local_only`, and `sensitive_data_approved`
- schema validation fails:
  - inspect the M30 diagnostics artifact for `schema_errors`, `missing_required_fields`, and `field_completeness`
  - inspect the service `/state` output captured in the diagnostics payload

## Evaluation Path

The structured extraction fixture suite lives under `examples/evals/structured_extraction/` and currently covers:

- a complete record with full field coverage
- an ambiguous record that must still return schema-valid JSON with explicit ambiguity notes and null handling

The smoke path calls each fixture twice to confirm deterministic structure adherence.

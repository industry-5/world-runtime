# Provider And Task Routing

Use the M28 routing substrate when you need `world-runtime` to resolve an abstract task profile to an eligible provider binding without hard-coding one provider family into the runtime core.

## What It Covers

- provider binding authoring
- task profile authoring
- deterministic candidate filtering and ranking
- bounded fallback behavior
- routing trace inspection

This playbook is intentionally operator-facing. `M29` now exposes supported App Server, Public API `/v1`, and SDK inspection surfaces for provider inventory and task resolution; use [runtime-admin-surface.md](runtime-admin-surface.md) for the supported integration path.

## Reference Assets

- Provider schema: `schemas/provider_binding.schema.json`
- Task profile schema: `schemas/task_profile.schema.json`
- Provider manifests: `infra/provider_bindings/`
- Task profile manifests: `infra/task_profiles/`
- M30 local extraction bindings:
  - `infra/provider_bindings/reference-local-structured-extraction-high.json`
  - `infra/provider_bindings/reference-local-structured-extraction-balanced.json`
- M30 local extraction profile:
  - `infra/task_profiles/structured-extraction.local-reference.json`
- Registry loader: `core/provider_registry.py`
- Task profile loader: `core/task_profiles.py`
- Router and trace model: `core/task_router.py`, `core/routing_trace.py`
- Diagnostics scripts: `scripts/check_provider_inventory.py`, `scripts/check_task_routing.py`

## Authoring Model

Keep task intent separate from provider inventory.

A provider binding should describe:

- what capabilities the provider exposes
- which managed service dependencies must be ready
- what quality, latency, cost, and determinism tier it sits in
- which routing scope tags apply

A task profile should describe:

- what kind of work is being attempted
- which capabilities and policy scope tags are required
- what output contract is expected
- which quality floor and fallback rule are acceptable
- how sensitive the task is from an approval posture standpoint

Neither manifest should contain secrets or environment-specific credentials.

## Service Dependency Linkage

Provider bindings may reference one or more managed services through `service_dependency_ids`.

Those ids should match the `service_id` values from `infra/service_manifests/`. This keeps process supervision in the M27 manifest layer and routing intent in the M28 provider layer.

If a managed dependency is not `ready`, the router should reject that provider and record the dependency state in the routing trace.

## Routing Flow

1. Load provider bindings from `infra/provider_bindings/`.
2. Load task profiles from `infra/task_profiles/`.
3. Gather current managed-service state from the runtime host when available.
4. Filter providers by required capabilities, scope tags, determinism floor, and service readiness.
5. Reject providers below the task profile's minimum quality floor.
6. Rank remaining providers deterministically using bounded fallback and explicit tie-breaks.
7. Emit a routing trace that records the selected provider, rejected candidates, and fallback behavior.

The router is intentionally rule-driven and inspectable. It is not a planner.

## Fallback Semantics

Fallback is bounded by the task profile.

- `preferred_quality_tier` defines the first-choice tier.
- `minimum_quality_tier` defines the lowest acceptable tier.
- `fallback_policy.max_quality_tier_downgrade` bounds how far the router may drop below the preferred tier.

If no preferred-tier provider survives the earlier filters, the router may select a lower-tier candidate only if that downgrade stays within the declared bound. The trace must record when this happens.

## Validation And Diagnostics

Run the M28 inventory and routing checks:

```bash
make provider-inventory
make task-routing
make m28-validate
```

The routing smoke script writes:

- `tmp/diagnostics/m28_task_routing.latest.json`

It validates:

- manifest loading for provider and task definitions
- cross-reference integrity between provider bindings and managed service ids
- deterministic resolution of reference task profiles
- explicit rejection reasons for ineligible candidates
- bounded fallback behavior and dependency-aware no-route outcomes

## Operational Notes

- Keep provider and task manifests generic; do not turn them into a second policy language.
- Prefer capability tags and scope tags that describe stable routing facts rather than vendor-specific branding.
- The M30 local AI reference stack uses the `extraction_reference_stack` capability tag to isolate the reference extraction providers from the earlier generic routing inventory while preserving the same router semantics.
- Treat `core.provider_registry`, `core.task_profiles`, and `core.task_router` as repo/operator tooling in `M28`, not as a newly supported downstream embedding API.

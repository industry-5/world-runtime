# Support Policy

This policy applies to the v1.1.0 GA release and subsequent v1.x releases unless superseded.

## Public Posture

- Public repository posture: Issues open, PRs welcome
- Maintainer response posture: best-effort
- Maintainers may close, defer, or decline issues and pull requests that do not fit roadmap, support capacity, release posture, or project direction
- Security and conduct reports should use the dedicated email channels in `SECURITY.md` and `CODE_OF_CONDUCT.md`

## Compatibility Commitments

- App Server protocol (`core/app_protocol.py`, `APP_SERVER_PROTOCOL.md`): major-version compatible.
- Public API (`api/PUBLIC_API_V1.md`): additive changes within `/v1`; breaking changes require a new major API version.
- Installed package consumer boundary (`python -m world_runtime serve`, `world-runtime serve`, `world_runtime.sdk`): stable within `v1.x` for downstream usage.
- Python SDK (`world_runtime.sdk`, `sdk/python_client.py`): tracks supported `/v1` Public API surface.
- Persistence migrations (`infra/migrations/persistence/`): forward-only ordered migrations; previously released migration files are immutable.
- Extension seams (`adapters.base.DomainAdapter`, `core.connector_transports.TransportPlugin`): contract checks enforced by `make extension-contracts`.

## Stable Surfaces

- App Server protocol
- Public API `/v1`
- Additive runtime-admin methods/endpoints exposed through the App Server protocol, Public API `/v1`, and Python SDK starter
- Supported package serve entrypoints
- Python SDK starter
- Persistence migration chain
- Extension contracts documented in the compatibility matrix

Managed-service manifests plus the provider/task routing manifests and internals are intentionally not listed here as stable public/downstream-consumer surfaces. The released runtime-admin inventory and bounded-reconcile surfaces build on those substrates without promoting the manifest or routing internals themselves to stable embedding APIs.

## Experimental Or Best-Effort Surfaces

- `labs/`
- private shared lab infrastructure unless explicitly promoted
- showcase/storytelling assets under `docs/`
- starter templates and exploratory examples unless explicitly promoted to a supported surface
- managed local service manifests, runtime-host internals, and repo/operator smoke tooling
- provider bindings, task profiles, deterministic routing internals, and repo/operator routing diagnostics tooling
- the local AI reference stack manifest, reference extraction service, fixture suite, and playbook assets
- release-gate and diagnostics workflows that may continue to evolve

## Unsupported Downstream Import Patterns

The following may exist in the repository or installed distribution for implementation reasons, but they are not part of the supported downstream-consumer contract:

- direct imports from `core/*`
- direct imports from `api/*`
- direct imports from `sdk/*`
- repo-path loading of source files from another checkout
- assumptions about repo-root `make` commands or checkout layout

## Support Windows

- v1.x stable releases: patch support for critical/high defects and compatibility regressions.

## Escalation and Governance

- Security/trust-boundary findings must be recorded in `docs/SECURITY_TRUST_BOUNDARY_REVIEW.md`.
- Open high-severity findings require explicit waiver disposition before release.
- Release readiness claims require a passing release-gate artifact: `tmp/diagnostics/m25_release_candidate_gate.latest.json`.

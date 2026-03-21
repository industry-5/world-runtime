# Support Policy

This policy applies to v1.0 release candidates and v1.x releases unless superseded.

## Public Maintainer Posture

- Public repository posture: Issues open, PRs welcome
- Maintainer response posture: best-effort
- Maintainers may close, defer, or decline issues and pull requests that do not fit roadmap, support capacity, release posture, or project direction
- Security and conduct reports should use the dedicated email channels in `SECURITY.md` and `CODE_OF_CONDUCT.md`

## Compatibility Commitments

- App Server protocol (`core/app_protocol.py`, `APP_SERVER_PROTOCOL.md`): major-version compatible.
- Public API (`api/PUBLIC_API_V1.md`): additive changes within `/v1`; breaking changes require a new major API version.
- Python SDK (`sdk/python_client.py`): tracks supported `/v1` Public API surface.
- Persistence migrations (`infra/migrations/persistence/`): forward-only ordered migrations; previously released migration files are immutable.
- Extension seams (`adapters.base.DomainAdapter`, `core.connector_transports.TransportPlugin`): contract checks enforced by `make extension-contracts`.

## Stable vs Experimental Surfaces

- Stable/support-committed surfaces:
  - App Server protocol
  - Public API `/v1`
  - Python SDK starter
  - Persistence migration chain
  - Extension contracts documented in the compatibility matrix
- Experimental or best-effort surfaces:
  - `labs/`
  - showcase/storytelling assets under `docs/`
  - starter templates and exploratory examples unless explicitly promoted to a supported surface
  - release-candidate-only workflows that may be refined before GA

## Support Windows

- v1.0 release candidates: best-effort support focused on blocker fixes and release validation.
- v1.x stable releases: patch support for critical/high defects and compatibility regressions.

## Escalation and Governance

- Security/trust-boundary findings must be recorded in `docs/SECURITY_TRUST_BOUNDARY_REVIEW.md`.
- Open high-severity findings require explicit waiver disposition before release.
- Release readiness claims require a passing M25 gate artifact: `tmp/diagnostics/m25_release_candidate_gate.latest.json`.

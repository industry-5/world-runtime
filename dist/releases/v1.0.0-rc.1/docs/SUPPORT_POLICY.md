# Support Policy

This policy applies to v1.0 release candidates and v1.x releases unless superseded.

## Compatibility Commitments

- App Server protocol (`core/app_protocol.py`, `APP_SERVER_PROTOCOL.md`): major-version compatible.
- Public API (`api/PUBLIC_API_V1.md`): additive changes within `/v1`; breaking changes require a new major API version.
- Python SDK (`sdk/python_client.py`): tracks supported `/v1` Public API surface.
- Persistence migrations (`infra/migrations/persistence/`): forward-only ordered migrations; previously released migration files are immutable.
- Extension seams (`adapters.base.DomainAdapter`, `core.connector_transports.TransportPlugin`): contract checks enforced by `make extension-contracts`.

## Support Windows

- v1.0 release candidates: best-effort support focused on blocker fixes and release validation.
- v1.x stable releases: patch support for critical/high defects and compatibility regressions.

## Escalation and Governance

- Security/trust-boundary findings must be recorded in `docs/SECURITY_TRUST_BOUNDARY_REVIEW.md`.
- Open high-severity findings require explicit waiver disposition before release.
- Release readiness claims require a passing M25 gate artifact: `tmp/diagnostics/m25_release_candidate_gate.latest.json`.

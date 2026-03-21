# Changelog

## [1.0.0-rc.1] - 2026-03-09

### Added

- Added an executable M25 release candidate gate script (`scripts/check_release_candidate_gate.py`) and make target (`make m25-validate`).
- Added v1.0 RC readiness docs: checklist, security/trust review register, and support policy (`docs/RELEASE_READINESS_CHECKLIST.md`, `docs/SECURITY_TRUST_BOUNDARY_REVIEW.md`, `docs/SUPPORT_POLICY.md`).

### Changed

- Expanded release artifact packaging inputs to include RC readiness and policy documentation.
- Updated release/operator documentation for v1.0 RC gate workflow and evidence expectations.

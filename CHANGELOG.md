# Changelog

This file is the release narrative for World Runtime. For the current operational snapshot, use [STATUS.md](STATUS.md). For milestone-by-milestone history and planning context, use [ROADMAP.md](ROADMAP.md).

## Unreleased

### Post-RC stabilization

- No new tagged release after `v1.0.0-rc.1` yet.
- The next release-oriented work is expected to focus on v1.0 GA cutover discipline, downstream adoption checks, and first patch-window readiness.
- Public-launch readiness work includes front-door documentation tightening, GitHub community scaffolding, and support-posture clarification for best-effort public maintenance.

## [1.0.0-rc.1] - 2026-03-09

### Highlights

- Declared the repository at **M25 complete** and moved World Runtime into a **v1.0 release candidate** posture.
- Converted milestone completion into an explicit release gate with documented go/no-go criteria and machine-readable diagnostics evidence.
- Published support, trust-boundary, and extension-adoption materials needed for partner-facing release evaluation.

### Added

- Aggregate release candidate validation command and diagnostics output via `make m25-validate` and `scripts/check_release_candidate_gate.py`.
- Release-readiness documentation: [docs/RELEASE_READINESS_CHECKLIST.md](docs/RELEASE_READINESS_CHECKLIST.md), [docs/SECURITY_TRUST_BOUNDARY_REVIEW.md](docs/SECURITY_TRUST_BOUNDARY_REVIEW.md), and [docs/SUPPORT_POLICY.md](docs/SUPPORT_POLICY.md).
- Release artifact inputs covering runtime, protocol, onboarding, and policy docs for the RC bundle.

### Changed

- Elevated the repo from milestone-complete implementation history to a release-candidate evaluation workflow.
- Tightened the operator/release documentation around evidence expectations, compatibility commitments, and support posture.

## Release Context

The tagged RC sits on top of the cumulative milestone arc:

- M20: public API and SDK support surface
- M21: safety-constrained domain expansion
- M22: provenance and audit evidence hardening
- M23: performance, persistence, and recovery validation
- M24: extension contracts, scaffolds, and partner onboarding
- M25: release-candidate gate and support/readiness materials

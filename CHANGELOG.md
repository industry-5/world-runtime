# Changelog

This file is the release narrative for World Runtime. For the current operational snapshot, use [STATUS.md](STATUS.md). For milestone-by-milestone history and planning context, use [ROADMAP.md](ROADMAP.md).

## Unreleased

### Post-GA stabilization

- No new tagged release after `v1.0.0` yet.
- The next release-oriented work is expected to focus on first patch-window readiness, downstream adoption checks, and public maintenance discipline.
- Public-launch follow-through work includes front-door documentation tightening, GitHub community scaffolding, and support-posture clarification for best-effort public maintenance.

## [1.0.0] - 2026-03-22

### Highlights

- Promoted World Runtime from release candidate to **v1.0 GA**.
- Aligned repo versioning, release docs, and support posture around the GA release.
- Tightened the public export story so the open-source repo can ship a curated public surface without private showcase packages.

### Changed

- Updated the repository package version from `1.0.0-rc.1` to `1.0.0`.
- Converted release-candidate wording across the front door, support, and readiness docs to GA wording.
- Added a curated public-export workflow so the public repo can be regenerated cleanly from the private development repo.

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

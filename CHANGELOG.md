# Changelog

This file is the release narrative for World Runtime. For the current operational snapshot, use [STATUS.md](STATUS.md). For milestone-by-milestone history and planning context, use [ROADMAP.md](ROADMAP.md).

## Unreleased

- No unreleased entries right now.

## [1.1.0] - 2026-04-23

### Highlights

- Promoted the completed v1.1 capability set into the public release as **v1.1.0**.
- Expanded the supported runtime story from core API/SDK surfaces to include package-hosted consumption, managed local services, provider/task routing, runtime-admin inspection plus bounded reconcile, and a local AI structured-extraction reference stack.
- Aligned the release narrative, support policy, consumer guidance, export flow, and release notes around the 1.1.0 public promotion.

### Added

- Installable package scaffolding, packaged bootstrap fixtures, and supported `python -m world_runtime serve` / `world-runtime serve` entrypoints for pinned downstream consumption.
- Managed runtime host and service-supervision assets including service manifests, readiness/health probes, lifecycle telemetry, and service-host smoke validation.
- Provider binding and task profile contracts, deterministic provider/task routing, routing traces, and provider inventory validation.
- Supported runtime-admin inventory, provider inspection, task resolution, and bounded reconcile surfaces through the App Server, Public API `/v1`, and starter SDK.
- A local AI structured-extraction reference stack with extraction-oriented provider/task inventory, schema-constrained fixtures, smoke/eval coverage, and operator playbook guidance.
- Dedicated release notes in [docs/releases/1.1.0.md](docs/releases/1.1.0.md).

### Changed

- Updated the repository package version from `1.0.0` to `1.1.0`.
- Reframed release-facing docs to describe the new capabilities as shipped release features rather than milestone-only work.
- Tightened the public export path so staged public artifacts can be audited for forbidden product references and reader-facing milestone wording before publication.

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

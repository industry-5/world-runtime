# World Runtime Status

_Last updated: 2026-03-14 (America/Chicago)_

## Project Phase

- Project: `world-runtime`
- Milestone status: **M0-M25 complete**
- Current phase: **v1.0 release candidate**
- Most recently completed milestone: **M25 - v1.0 release candidate gate**
- Next milestone candidate: **v1.0 GA release execution and post-RC stabilization**

## Current Release Posture

- Tagged release candidate: `v1.0.0-rc.1` (2026-03-09)
- Repository package version: `VERSION` -> `1.0.0-rc.1`
- Interpretation: the repository version file is aligned to the current public release-candidate tag for the public-launch phase
- Release gate references:
  - [CHANGELOG.md](CHANGELOG.md)
  - [docs/RELEASE_READINESS_CHECKLIST.md](docs/RELEASE_READINESS_CHECKLIST.md)
  - [docs/SUPPORT_POLICY.md](docs/SUPPORT_POLICY.md)

This page is the current-state ledger for the repo: release posture, maintained command baseline, and recent evidence.

## Current Command Baseline

Use this bundle as the default high-confidence pre-merge or release-critical validation set:

```bash
make test
make evals
make validate
make examples
make adapters
make integration-stacks
make connectors
make connector-plugins
make protocol-compat
make public-api-compat
make extension-contracts
make ci-gate
make deploy-local
make deploy-dev
make workflow-quickstart
make observability
make provenance-audit
make benchmark
make recovery-check
make m25-validate
```

## Runtime Surface Snapshot

- Kernel: event store/replay/snapshots, policy engine, simulation engine, reasoning adapter
- App Server: legacy `handle_request` and stabilized wire `handle_message`
- Protocol: [APP_SERVER_PROTOCOL.md](APP_SERVER_PROTOCOL.md) and `schemas/app_server.*.schema.json`
- Public integration surface: versioned `v1` HTTP API and starter Python SDK
- CI/CD: merge gate in `.github/workflows/ci.yml` and release workflow in `.github/workflows/release.yml`
- Observability: telemetry, traces, diagnostics methods, and audit artifact generation
- Releases: `VERSION`-driven artifact builder plus `dist/releases/` bundles
- Deployments: local and dev profiles with sqlite persistence
- Integration stacks: validated external ingress/egress deployment patterns
- Connectors: inbound/outbound execution adapters, provider transport plugins, durable idempotency state, dead-letter replay workflows
- Connector governance: provider/source-aware policy filters, approval-gated execution, durable connector decision records
- Approval hardening: actor-attributed approvals, role/capability checks, escalation/override states, replay-safe approval rehydration
- Extension seams: documented contracts, scaffold templates, validation tooling, compatibility matrix, and partner onboarding assets

## Domain Package Rollup

- Root status tracks rollup state only for domain packages.
- The World Game showcase stack currently uses:
  - `labs/world_game_studio_next` as the primary showcase surface for demos and workshops
  - `adapters/world_game` as the domain/runtime source of truth behind that experience
- `adapter-world-game` maintains detailed package-local planning and status in:
  - [adapters/world_game/ROADMAP.md](adapters/world_game/ROADMAP.md)
  - [adapters/world_game/STATUS.md](adapters/world_game/STATUS.md)
- `labs/world_game_studio` has been retired after stabilization and is no longer a supported or documented UI path.
- Package-local and lab-local docs remain the source of truth for World Game milestone history and current showcase/package snapshots.

## Recent Milestone Completions

### M25 - v1.0 release candidate gate

- Added executable RC gate validation and machine-readable diagnostics (`scripts/check_release_candidate_gate.py`, `make m25-validate`, `tmp/diagnostics/m25_release_candidate_gate.latest.json`)
- Added readiness, trust-boundary, and support-policy docs for the RC decision
- Expanded release artifacts to include RC readiness and policy materials

### M24 - Packaging, extension contracts, and partner onboarding

- Added explicit extension contract docs, partner onboarding, scaffold templates, validation tooling, and compatibility matrix
- Expanded release bundle inputs and tests to include onboarding and extension assets

### M23 - Performance, persistence, and recovery hardening

- Added benchmark harness, persistence recovery validation, sqlite backup/restore utilities, and operator playbook coverage
- Produced reproducible diagnostics artifacts for benchmark and recovery checks

### M22 - Provenance and evidence hardening

- Added provenance envelope support, deterministic audit export, sensitive-field redaction, and evidence linkage across decision flows
- Added provenance-oriented diagnostics and test coverage

### M21 - Safety-constrained domain expansion

- Added `adapter-air-traffic`, constrained scenario content, safety evals, and playbook/operator workflow support for high-constraint domains

### M20 - Public API surface and SDK starter

- Added versioned public API facade, starter Python SDK, compatibility checks, example client, and operator guidance for supported external entry points

For the full strategic and historical milestone record, see [ROADMAP.md](ROADMAP.md).

## Recent Validation Evidence

### M25 evidence

- `make test` -> passed
- `make validate` -> passed
- `make m25-validate` -> passed; wrote `tmp/diagnostics/m25_release_candidate_gate.latest.json`
- `make benchmark` -> passed; wrote `tmp/diagnostics/m23_benchmarks.latest.json`
- `make recovery-check` -> passed; wrote `tmp/diagnostics/m23_recovery.latest.json`
- `make provenance-audit` -> passed; wrote `tmp/diagnostics/audit_export.latest.json`
- `make protocol-compat` -> passed
- `make public-api-compat` -> passed
- `make extension-contracts` -> passed
- `make release-artifacts RELEASE_VERSION=1.0.0-rc.1` -> passed; wrote `dist/releases/v1.0.0-rc.1/` and `dist/releases/v1.0.0-rc.1.tar.gz`
- `make release-dry-run` -> passed; validated CI gate + artifact build for `VERSION` (`v1.0.0-rc.1`)

### M24 and earlier evidence references

- M24 extension/onboarding evidence remains captured in this repo’s release and validation history and is summarized in [ROADMAP.md](ROADMAP.md)
- Package-local validation history for `adapter-world-game` lives in [adapters/world_game/STATUS.md](adapters/world_game/STATUS.md)

## Known Notes

- `jsonschema.RefResolver` deprecation warnings are expected in tests and scripts and are currently non-blocking
- App Server protocol compatibility policy is major-version compatible
- Observability diagnostics artifacts are written under `tmp/diagnostics/`
- `make integration-stacks`, `make connectors`, `make connector-plugins`, `make provenance-audit`, `make benchmark`, `make recovery-check`, and `make m25-validate` are all part of the maintained release-candidate confidence surface
- Public support posture is best-effort; Issues are open and PRs are welcome, but maintainers may decline work outside project direction or support capacity

## Handoff Checklist For New Thread

1. Re-read current repo state from disk rather than relying on thread memory.
2. Confirm `git status` and avoid reverting unrelated changes.
3. Re-run the baseline command bundle for the surfaces you are touching.
4. Keep root docs focused on rollup truth; send domain-package milestone depth to package-local docs.
5. End implementation threads by updating the relevant current-state docs and release narrative when behavior or supported workflows change.

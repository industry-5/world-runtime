# World Runtime Status

_Last updated: 2026-03-09 (America/Chicago)_

## Current Phase

- Project: `world-runtime`
- Milestone status: **M0-M25 complete**
- Most recently completed milestone: **M25 - v1.0 release candidate gate**

## Completed Milestones

- M0: Repo legibility
- M1: Schemas and contracts
- M2: Event store and projection kernel
- M3: Policy engine
- M4: Simulation engine
- M5: Reasoning adapter
- M6: App Server
- M7: Eval harness
- M8: Domain adapters
- M9: Operator workflows
- M10: Reference deployments
- M11: Persistence adapters + migration strategy
- M12: App Server protocol stabilization
- M13: CI/CD and release automation
- M14: Observability hardening
- M15: Integration reference stacks
- M16: Connector execution adapters
- M17: External connector transport plugins
- M18: Connector policy guardrails
- M19: Approval workflow and actor identity hardening
- M20: Public API surface and SDK starter
- M21: Safety-constrained domain expansion
- M22: Provenance and evidence hardening
- M23: Performance, persistence, and recovery hardening
- M24: Packaging, extension contracts, and partner onboarding
- M25: v1.0 release candidate gate

## Current Command Baseline

Use this bundle as the default pre-merge check set:

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

## Current Runtime Surfaces

- Kernel: event store/replay/snapshots, policy engine, simulation engine, reasoning adapter
- App Server: legacy `handle_request` and stabilized wire `handle_message`
- Protocol: `APP_SERVER_PROTOCOL.md`, wire schemas in `schemas/app_server.*.schema.json`
- CI/CD: GitHub Actions for merge gating (`.github/workflows/ci.yml`) and tag/manual release artifacts (`.github/workflows/release.yml`)
- Observability: shared telemetry+trace store (`core/observability.py`), App Server diagnostics methods (`telemetry.summary`, `telemetry.events`, `trace.list`, `diagnostics.dashboard`, `audit.export`), dashboard/audit artifact generator (`scripts/run_observability_diagnostics.py`)
- Releases: `VERSION`-driven artifact builder (`scripts/build_release_artifacts.py`) and release manifest/checksum outputs under `dist/releases/`
- Adapters: supply-network, narrative-world, and safety-constrained air-traffic via adapter registry
- Deployments: local/dev profiles with sqlite persistence
- Integration stacks: external ingress/egress deployment patterns (`infra/integration_stacks/*.json`) validated and smoke-tested via `core/integration_stacks.py` + `scripts/check_integration_stacks.py`
- Connectors: runtime-safe inbound/outbound execution adapters with provider transport/auth plugins, persistent idempotency state, and dead-letter replay workflows (`core/connectors.py`, `core/connector_state_store.py`, `core/connector_transports.py`, App Server connector methods)
- Connector guardrails: provider/source-aware policy scope filtering, connector policy evidence, approval-gated execution, and durable connector decision records (`core/policy_engine.py`, `core/app_server.py`, `core/connector_state_store.py`)
- Approval workflow hardening: actor-attributed approvals, role/capability authorization checks, explicit escalation/override states, approval history query methods, and replay-safe approval-chain rehydration (`core/app_server.py`, `schemas/common.schema.json`, `schemas/decision.schema.json`)
- Public API + SDK: versioned external `v1` HTTP API wrapper and starter Python SDK for proposal/simulation/approval/connector/observability flows (`api/runtime_api.py`, `api/http_server.py`, `api/PUBLIC_API_V1.md`, `sdk/python_client.py`)
- Extension onboarding: explicit extension contracts + compatibility matrix docs, scaffold templates for adapters/connector plugins, and validation tooling for extension seams (`docs/EXTENSION_CONTRACTS.md`, `docs/PARTNER_ONBOARDING.md`, `docs/COMPATIBILITY_MATRIX.md`, `templates/*`, `scripts/scaffold_extension.py`, `scripts/check_extension_contracts.py`)
- Release candidate gate: aggregate M25 go/no-go validation with readiness checklist, trust-boundary review, support policy, and machine-readable diagnostics (`scripts/check_release_candidate_gate.py`, `docs/RELEASE_READINESS_CHECKLIST.md`, `docs/SECURITY_TRUST_BOUNDARY_REVIEW.md`, `docs/SUPPORT_POLICY.md`)
- Migrations: versioned SQL in `infra/migrations/persistence/`
- Operational hardening: reproducible benchmark harness, persistence recovery/migration-volume checks, and sqlite backup/restore utilities with diagnostics artifacts (`scripts/run_performance_benchmarks.py`, `scripts/check_persistence_recovery.py`, `core/persistence_recovery.py`)

## Known Notes

- `jsonschema.RefResolver` deprecation warnings are expected in tests/scripts and currently non-blocking.
- Compatibility policy for App Server protocol is major-version compatible.
- M14 observability diagnostics artifacts are written to `tmp/diagnostics/` by `make observability`.
- M15 integration stack checks run with `make integration-stacks`.
- M16 connector checks run with `make connectors`.
- M17 connector plugin checks run with `make connector-plugins`.
- M18 connector guardrail checks run with `python3 -m pytest -q tests/test_connector_policy_guardrails.py`.
- M19 approval identity checks run with `python3 -m pytest -q tests/test_app_server.py tests/test_connector_policy_guardrails.py`.
- M20 public API compatibility checks run with `make public-api-compat` and `python3 -m pytest -q tests/test_public_api_surface.py tests/test_public_api_compatibility.py`.
- M21 safety-constrained domain checks run with `make air-traffic-evals` and `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-air-traffic`.
- M22 provenance checks run with `make provenance-audit` and `python3 -m pytest -q tests/test_provenance.py tests/test_app_server.py::test_audit_export_is_redacted_and_reproducible`.
- M23 performance/recovery checks run with `make benchmark`, `make recovery-check`, and `make m23-validate`.
- M24 extension/onboarding checks run with `make extension-contracts`, `make scaffold-smoke`, and `make m24-validate`.
- M25 release-candidate checks run with `make m25-validate` and `python3 scripts/check_release_candidate_gate.py`.

## Next Milestone Candidate

- v1.0 GA release execution and post-RC stabilization
  - release tagging/signoff, downstream adoption checks, and first patch-window readiness

## Completion Notes (M25)

- Added executable M25 release candidate gate script with grouped baseline/milestone/regression command matrix and machine-readable diagnostics output (`scripts/check_release_candidate_gate.py`, `tmp/diagnostics/m25_release_candidate_gate.latest.json`).
- Added repository command surface for M25 gate execution (`make m25-validate` in `Makefile`).
- Added v1.0 readiness checklist with explicit go/no-go criteria and aggregate validation matrix (`docs/RELEASE_READINESS_CHECKLIST.md`).
- Added security and trust-boundary review register + waiver policy for release disposition (`docs/SECURITY_TRUST_BOUNDARY_REVIEW.md`).
- Added published support policy and compatibility commitments covering protocol, public API, SDK, migrations, and extension seams (`docs/SUPPORT_POLICY.md`).
- Added changelog and expanded release artifact bundle inputs to include M25 readiness/policy docs (`CHANGELOG.md`, `scripts/build_release_artifacts.py`, `tests/test_release_artifacts.py`).

## Completion Notes (M24)

- Added explicit extension contract documentation for adapters, connector plugins, policy packs, and simulation boundaries (`docs/EXTENSION_CONTRACTS.md`).
- Added partner onboarding assets and operational runbook for extension authoring (`docs/PARTNER_ONBOARDING.md`, `playbooks/partner-onboarding.md`).
- Added adapter and connector plugin scaffold templates plus generator CLI (`templates/adapter_starter/`, `templates/connector_plugin_starter/`, `scripts/scaffold_extension.py`).
- Added extension contract validation script and tests to keep extension surfaces explicit and stable (`scripts/check_extension_contracts.py`, `tests/test_extension_contracts.py`, `tests/test_extension_scaffold.py`).
- Added compatibility matrix across runtime, protocol, SDK, migrations, and plugin/adapter seams (`docs/COMPATIBILITY_MATRIX.md`).
- Expanded release artifact bundle contents to include extension onboarding assets and scaffold tooling (`scripts/build_release_artifacts.py`, `tests/test_release_artifacts.py`).

## Completion Notes (M23)

- Added sqlite backup/restore and persistence table count utilities used for recovery validation (`core/persistence_recovery.py`).
- Added benchmark harness covering replay, policy, simulation, connector, and public API flows for local/dev profiles with reproducible workload fingerprinting (`scripts/run_performance_benchmarks.py`).
- Added persistence hardening checks for restart idempotency, backup/restore round-trip verification, and migration validation at larger fixture volumes (`scripts/check_persistence_recovery.py`).
- Added M23 command surface (`make benchmark`, `make recovery-check`, `make m23-validate`) and operator playbook (`playbooks/performance-persistence-recovery.md`).
- Added test coverage for backup/restore primitives and reduced-volume benchmark/recovery script execution (`tests/test_persistence_recovery.py`).

## Completion Notes (M22)

- Added provenance utility primitives for evidence normalization, sensitive-field redaction, and deterministic audit fingerprinting (`core/provenance.py`).
- Added optional schema-level provenance envelope support and updated decision example contract (`schemas/common.schema.json`, `schemas/decision.schema.json`, `examples/decision.example.json`).
- Added provenance-rich decision records and connector policy decision provenance linkage across proposal, policy evaluation, approval, and execution outcome (`core/app_server.py`).
- Added App Server `audit.export` method for redacted, machine-readable audit artifacts with provenance diagnostics (`core/app_server.py`).
- Added diagnostics script support and command surface for provenance artifact generation (`scripts/run_observability_diagnostics.py`, `Makefile`, `README.md`, `playbooks/operator-observability-diagnostics.md`, `ARCHITECTURE.md`, `ROADMAP.md`).
- Added provenance-focused test coverage for redaction/fingerprinting and audit export behavior (`tests/test_provenance.py`, `tests/test_app_server.py`).

## Completion Notes (M21)

- Added new `adapter-air-traffic` domain package with adapter schemas, default safety policy pack, and registry wiring (`adapters/air_traffic/*`, `adapters/registry.py`).
- Added `air-traffic-mini` scenario pack with constrained proposal path, conflicting proposals, simulation artifact, and approval-tracked decision (`examples/scenarios/air-traffic-mini/*`).
- Added explicit deny, warn, require-approval, and simulate-before-action safety constraints in domain policy/eval paths (`adapters/air_traffic/policies/default_policy.json`, `core/eval_harness.py`).
- Added domain safety coverage in tests and eval suite (`tests/test_air_traffic_domain.py`, `tests/test_eval_harness.py`, `evals/suites.manifest.json`).
- Extended example/adapter/workflow checks and playbooks for operator legibility in high-constraint conditions (`scripts/check_examples.py`, `core/operator_workflows.py`, `scripts/run_operator_workflow.py`, `playbooks/adapter-air-traffic.md`, `playbooks/operator-quickstart.md`).
- Updated repo command and docs surfaces for M21 (`Makefile`, `README.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `adapters/README.md`).

## Completion Notes (M20)

- Added versioned `v1` public API facade and endpoint mapping over supported App Server methods (`api/runtime_api.py` + `api/http_server.py`).
- Added starter Python SDK for external clients without importing internal runtime modules (`sdk/python_client.py`).
- Added versioned API contract docs and compatibility/deprecation notes (`api/PUBLIC_API_V1.md`, `APP_SERVER_PROTOCOL.md`, `sdk/README.md`).
- Added public API example client and operator quickstart guidance for local/dev auth/config (`examples/clients/public_api_python_sdk_example.py`, `playbooks/operator-quickstart.md`).
- Added public-surface compatibility checks and tests (`scripts/check_public_api_compatibility.py`, `tests/test_public_api_compatibility.py`, `tests/test_public_api_surface.py`).
- Updated repo-level command surface and roadmap/architecture/readme references for supported public entrypoints (`Makefile`, `ROADMAP.md`, `README.md`, `ARCHITECTURE.md`).

## Validation Evidence (M21)

- `make test` -> 113 passed
- `make validate` -> schema checks passed + 113 passed
- `make air-traffic-evals` -> 3 passed
- `make adapters` -> adapter checks passed (including `adapter-air-traffic`)
- `make examples` -> scenario coherence checks passed (including `air-traffic-mini`)
- `make evals` -> suite `world-runtime-v0.1` passed (7/7)
- `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-air-traffic` -> succeeded
- `make public-api-compat` -> Public API compatibility check passed
- `make protocol-compat` -> protocol compatibility check passed
- `make ci-gate` -> passed (validate + evals + examples + adapters + protocol/public API compatibility)

## Validation Evidence (M22)

- `make test` -> 117 passed
- `make validate` -> schema checks passed + 117 passed
- `make provenance-audit` -> proposal-review diagnostics passed + `tmp/diagnostics/audit_export.latest.json` generated
- `make observability` -> diagnostics artifact generation passed
- `make evals` -> suite `world-runtime-v0.1` passed (7/7)
- `make examples` -> scenario coherence checks passed
- `make adapters` -> adapter checks passed
- `make protocol-compat` -> protocol compatibility check passed
- `make public-api-compat` -> public API compatibility check passed
- `make connectors` -> connector checks passed (17 passed, 13 deselected)

## Validation Evidence (M23)

- `make benchmark` -> passed; wrote `tmp/diagnostics/m23_benchmarks.latest.json` (local/dev workload envelope metrics).
- `make recovery-check` -> passed; wrote `tmp/diagnostics/m23_recovery.latest.json` (restart idempotency, backup/restore, migration-volume checks).
- `python3 -m pytest -q tests/test_persistence_recovery.py` -> passed.

## Validation Evidence (M24)

- `make test` -> passed (`122 passed`, 4 expected deprecation warnings from `jsonschema.RefResolver`).
- `make validate` -> schema checks passed + `122 passed`.
- `make extension-contracts` -> passed.
- `make scaffold-smoke` -> passed (adapter and connector plugin starters generated under `tmp/scaffold_smoke/`).
- `make m24-validate` -> passed (extension checks + scaffold smoke + release artifacts).
- `make protocol-compat` -> passed.
- `make public-api-compat` -> passed.
- `make adapters` -> passed.
- `make examples` -> passed.

## Validation Evidence (M25)

- `make test` -> passed (`123 passed`, 4 expected deprecation warnings from `jsonschema.RefResolver`).
- `make validate` -> schema checks passed + `123 passed`.
- `make m25-validate` -> passed; wrote `tmp/diagnostics/m25_release_candidate_gate.latest.json`.
- `make benchmark` -> passed; wrote `tmp/diagnostics/m23_benchmarks.latest.json`.
- `make recovery-check` -> passed; wrote `tmp/diagnostics/m23_recovery.latest.json`.
- `make provenance-audit` -> passed; wrote `tmp/diagnostics/audit_export.latest.json`.
- `make protocol-compat` -> passed.
- `make public-api-compat` -> passed.
- `make extension-contracts` -> passed.
- `make release-artifacts RELEASE_VERSION=1.0.0-rc.1` -> passed; wrote `dist/releases/v1.0.0-rc.1/` and `dist/releases/v1.0.0-rc.1.tar.gz`.
- `make release-dry-run` -> passed; validated CI gate + artifact build for `VERSION` (`v0.1.0`).

## Handoff Checklist For New Thread

1. Re-read current repo state from disk (do not rely on thread memory).
2. Confirm `git status` and avoid reverting unrelated changes.
3. Re-run baseline command bundle.
4. Implement only the selected milestone scope.
5. End with updated `STATUS.md` timestamp + concise completion notes.

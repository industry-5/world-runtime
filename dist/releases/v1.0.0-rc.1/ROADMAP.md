# ROADMAP.md

<a id="world-runtime-roadmap"></a>

# World-Runtime Roadmap

<a id="goal"></a>

## Goal

Create a harness-first, agent-runnable reference repository for executable world-model systems.

The roadmap is intentionally milestone-based, test-driven, and repo-first. Each phase must leave the repository more understandable, more runnable, more governable, and more extensible by both humans and coding agents.

World-Runtime is not trying to become a generic application framework. Its purpose is to establish a durable runtime shape for systems built around:

- explicit world state
- append-only events
- deterministic projection
- simulation of possible futures
- policy-driven orchestration
- agent-facing interfaces for planning, execution, and review

* * *

<a id="current-status"></a>

## Current status

**Current milestone state:** M0–M25 completed.

**Current repo shape:** the repository has moved beyond concept validation and now operates as a real runtime harness with schemas, event/project/replay kernel, policy engine, simulation engine, reasoning adapter, App Server, eval harness, domain adapters, operator workflows, reference deployments, persistence, protocol stabilization, release automation, observability, integration stacks, connector execution, external transport plugins, provenance-grade audit export, operational benchmark/recovery validation harnesses, and partner-facing extension contracts/templates/onboarding assets.

**Current phase:** v1.0 release candidate ready.

**Next recommended milestone:** v1.0 GA release execution and post-RC stabilization.

**Path to v1.0:** M21–M25.

**Definition of v1.0:** production-capable runtime for domain deployments, with stable extension surfaces, policy-governed external effects, attributable approvals, broader domain proof, audit-grade provenance, operational recovery guidance, and partner-ready onboarding.

* * *

<a id="roadmap-principles"></a>

## Roadmap principles

Every milestone should improve the repository along four dimensions:

1. **Legibility** — humans and agents can understand the system quickly.
2. **Runnable quality** — the repo is executable, testable, and observable.
3. **Governability** — external effects, approvals, and trust boundaries remain explicit.
4. **Extensibility** — domain teams can add adapters, simulators, policies, and connectors without rewriting the kernel.

The roadmap is intentionally milestone-based because milestone boundaries are easier for coding agents to execute against, easier for humans to review, and easier to validate through tests and playbooks.

* * *

<a id="release-trajectory"></a>

## Release trajectory

<a id="v01-reference-repo-and-local-runtime-kernel"></a>

### v0.1 — Reference repo and local runtime kernel

M0–M17 establish the reference architecture, core runtime kernel, test/eval harness, domain adapter model, deployment profiles, persistence, observability, integration stacks, and connector transport/plugin surfaces.

<a id="v02-governed-external-effects-and-stronger-public-runtime-surfaces"></a>

### v0.2 — Governed external effects and stronger public runtime surfaces

M18–M20 focus on connector policy guardrails, attributable approval workflows, and a public API/SDK layer.

<a id="v03-broader-domain-proof-and-operational-hardening"></a>

### v0.3 — Broader domain proof and operational hardening

M21–M24 expand domain stress coverage, provenance, recovery, performance, packaging, and partner extension surfaces.

<a id="v10-production-capable-runtime-for-domain-deployments"></a>

### v1.0 — Production-capable runtime for domain deployments

M25 converts accumulated milestone work into a release-quality gate with explicit readiness criteria.

* * *

<a id="current-constraints"></a>

## Current constraints

The repository is now v1.0 release-candidate complete. The remaining constraint is execution discipline for GA release cutover and post-RC stabilization.

* * *

<a id="active-milestone-queue-m18m25"></a>

## Active milestone queue (M18–M25)

<a id="m18-connector-policy-guardrails"></a>

### M18 — Connector policy guardrails

**Status:** Completed (2026-03-09)

**Depends on:** M16 connector execution adapters, M17 external connector transport plugins.

**Unlocks:** safer connector execution, real approval gating for external effects, more credible public API exposure in M20.

<a id="objective"></a>

#### Objective

Move connectors from runtime-safe transport mechanics to policy-governed integration surfaces.

<a id="why-now"></a>

#### Why now

M17 established transport plugins, persistent connector state, and dead-letter replay paths. The next risk is no longer transport plumbing. The next risk is uncontrolled external effects. Connector execution now needs provider-aware policy evaluation, approval gates, and durable audit records.

<a id="deliverables"></a>

#### Deliverables

- provider-aware connector policy model
- connector-specific policy evaluation entry points
- approval-required outcomes for risky outbound actions
- inbound trust classification and source validation hooks
- durable connector policy decision records with evidence
- connector guardrail playbook and examples

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- outbound connector operations can be denied or approval-gated before transport execution
- inbound operations can be rejected based on source and provider policy
- policy reports include connector-visible evidence
- approval-required connector requests do not execute until approved
- tests cover provider-aware rules and durable decision recording

<a id="suggested-implementation-notes"></a>

#### Suggested implementation notes

Representative code areas:

- `core/connectors.py`
- `core/policy_engine.py`
- `core/app_server.py`
- `schemas/decision.schema.json`
- `schemas/policy.schema.json`
- `examples/`
- `playbooks/connector-execution.md`
- `tests/test_connectors.py`
- `tests/test_connector_policy_guardrails.py`

<a id="completion-evidence-placeholder"></a>

#### Completion evidence

- policy-aware connector execution path in App Server connector methods (`connector.inbound.run`, `connector.outbound.run`)
- provider/source-aware connector policy scope model and policy evidence capture
- approval-gated connector flow that blocks transport execution until approval is `approved`
- durable connector policy decision records and retrieval methods (`connector.policy_decision.list`, `connector.policy_decision.get`)
- guardrail tests (`tests/test_connector_policy_guardrails.py`) and playbook updates (`playbooks/connector-execution.md`)

* * *

<a id="m19-approval-workflow-and-actor-identity-hardening"></a>

### M19 — Approval workflow and actor identity hardening

**Status:** Completed (2026-03-09)

**Depends on:** M18 connector policy guardrails.

**Unlocks:** attributable approvals, authorized overrides, governance-grade execution review, stronger auditability.

<a id="objective"></a>

#### Objective

Introduce a minimal but real actor and approval model so decisions and overrides are attributable.

<a id="why-now"></a>

#### Why now

Approval-required outcomes are only as trustworthy as the identity and authorization model behind them. Once connectors and other actions can be gated, the runtime must record who approved, rejected, escalated, or overrode those actions.

<a id="deliverables"></a>

#### Deliverables

- actor identity representation for operators, services, and agents
- role or capability checks for approvals and overrides
- approval request lifecycle states
- durable approval chain recording on decisions
- override and escalation workflow support
- approval-focused playbook updates

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- approvals are attributable to specific actors
- unauthorized actors cannot approve restricted actions
- override and escalation paths are explicit and durable
- decision history shows who approved what and when
- replay preserves approval-chain provenance

<a id="suggested-implementation-notes"></a>

#### Suggested implementation notes

Representative code areas:

- actor schema or actor extensions in existing schemas
- `schemas/decision.schema.json`
- `core/app_server.py`
- `core/operator_workflows.py`
- `core/event_store.py`
- `examples/`
- `playbooks/operator-proposal-review.md`
- tests for approval attribution and authorization

<a id="completion-evidence-placeholder"></a>

#### Completion evidence

- actor-aware approval flow with attributable `approval_chain` entries and actor identity payloads
- role/capability enforcement for approvals and overrides (`approval.respond`, proposal/connector capabilities, escalation/override capabilities)
- explicit approval lifecycle support for `approved`, `rejected`, `escalated`, and `overridden`
- durable approval chain provenance persisted as approval events and rehydrated across runtime replay
- operator/connector playbook updates and approval-focused test coverage (`tests/test_app_server.py`, `tests/test_connector_policy_guardrails.py`)

* * *

<a id="m20-public-api-surface-and-sdk-starter"></a>

### M20 — Public API surface and SDK starter

**Status:** Completed (2026-03-09)

**Depends on:** M19 approval workflow and actor identity hardening.

**Unlocks:** external integrability, partner pilots, cleaner separation between supported surfaces and internal implementation.

<a id="objective"></a>

#### Objective

Turn the runtime from a repo-internal harness into a stable external integration surface.

<a id="why-now"></a>

#### Why now

Once governance and approval surfaces are credible, the next step is to expose supported entry points for third-party users without forcing them to import internal modules or reverse-engineer App Server internals.

<a id="deliverables"></a>

#### Deliverables

- HTTP or JSON API wrapper over core App Server methods
- versioned API contract documentation
- starter SDK in one implementation language
- example clients for common flows
- authentication and configuration examples for local and dev
- compatibility and deprecation notes

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- third parties can invoke core runtime flows without importing internal modules
- API and SDK surfaces are versioned and documented
- public entrypoints cover proposal, simulation, approval, connector execution, and observability basics
- compatibility tests cover public surfaces, not just internal protocol methods

<a id="suggested-implementation-notes"></a>

#### Suggested implementation notes

Representative code areas:

- `/api`
- `/sdk`
- `APP_SERVER_PROTOCOL.md`
- `README.md`
- `playbooks/operator-quickstart.md`
- protocol compatibility tests

<a id="completion-evidence-placeholder"></a>

#### Completion evidence

- Public API package with versioned `v1` endpoints over App Server methods (`api/runtime_api.py`, `api/http_server.py`, `api/PUBLIC_API_V1.md`)
- Starter Python SDK for session/proposal/simulation/approval/connector/observability flows (`sdk/python_client.py`, `sdk/README.md`)
- Public-surface compatibility checks and tests (`scripts/check_public_api_compatibility.py`, `tests/test_public_api_compatibility.py`, `tests/test_public_api_surface.py`)
- Smoke-testable SDK client example with local/dev auth configuration (`examples/clients/public_api_python_sdk_example.py`, `make api-server`, `make sdk-example`)

* * *

<a id="m21-safety-constrained-domain-expansion"></a>

### M21 — Safety-constrained domain expansion

**Status:** Completed (2026-03-09)

**Depends on:** M20 public API surface and SDK starter.

**Unlocks:** stronger proof that the architecture holds under high-constraint operational conditions, not just current reference domains.

<a id="objective"></a>

#### Objective

Prove the kernel under a high-constraint operational domain.

<a id="recommended-first-scenario"></a>

#### Recommended first scenario

`air-traffic-mini`

<a id="why-this-domain"></a>

#### Why this domain

A safety-constrained operational domain stresses policy, simulation, approval sequencing, and operator review more sharply than the current adapters. It provides a better test of whether the runtime can support consequential orchestration rather than only plausible orchestration.

<a id="deliverables"></a>

#### Deliverables

- new safety-constrained domain adapter
- domain schemas, policies, examples, and playbooks
- scenario pack and domain evals
- demonstration workflow showing conflicting proposals and constrained decision paths
- explicit deny, warn, require-approval, and simulate-before-action patterns

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- the new adapter works without broad kernel rewrites
- policy and simulation meaningfully constrain unsafe actions
- domain evals catch safety regressions
- operator workflows remain understandable under stronger constraints

<a id="suggested-implementation-notes"></a>

#### Suggested implementation notes

Representative code areas:

- `adapters/air_traffic` or equivalent
- `examples/scenarios/air-traffic-mini/`
- domain playbooks
- eval suite manifest updates
- adapter tests and scenario tests

<a id="completion-evidence-placeholder"></a>

#### Completion evidence

- Added `adapter-air-traffic` with isolated domain schemas/policies bound to `examples/scenarios/air-traffic-mini` without kernel contract rewrites (`adapters/air_traffic/*`, `adapters/registry.py`).
- Added safety-focused scenario pack including conflicting proposals, constrained decision path, and simulation evidence (`examples/scenarios/air-traffic-mini/*`).
- Added domain safety eval case and suite coverage for deny/warn/require-approval behavior (`core/eval_harness.py`, `evals/suites.manifest.json`, `tests/test_eval_harness.py`, `tests/test_air_traffic_domain.py`).
- Extended operator workflow wiring and scenario/playbook checks so constrained-domain flows remain runnable and understandable (`core/operator_workflows.py`, `scripts/run_operator_workflow.py`, `scripts/check_examples.py`, `playbooks/adapter-air-traffic.md`).

* * *

<a id="m22-provenance-and-evidence-hardening"></a>

### M22 — Provenance and evidence hardening

**Status:** Completed (2026-03-09)

**Depends on:** M21 safety-constrained domain expansion.

**Unlocks:** audit-grade decision reconstruction, more trustworthy reviews, better post-incident analysis.

<a id="objective"></a>

#### Objective

Make runtime decisions audit-grade.

<a id="why-now"></a>

#### Why now

As more consequential domains are added, the system needs stronger proof of why a decision happened, what evidence informed it, and how that decision moved from proposal through execution.

<a id="deliverables"></a>

#### Deliverables

- richer evidence attachment model for reasoning, policy, simulation, approval, and connector decisions
- trace linkage across proposal, simulation, policy evaluation, approval, execution, and outcome
- audit export artifact format
- provenance-focused diagnostics additions
- evidence retention and redaction rules for sensitive fields

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- every major decision can be traced end to end
- evidence is machine-readable and human-inspectable
- sensitive fields are redacted without losing decision usefulness
- post-hoc audit export is consistent and reproducible

<a id="suggested-implementation-notes"></a>

#### Suggested implementation notes

Representative code areas:

- `core/observability.py`
- `core/reasoning_adapter.py`
- `core/policy_engine.py`
- `core/connectors.py`
- diagnostics scripts
- decision schemas and provenance tests

<a id="completion-evidence-placeholder"></a>

#### Completion evidence

- Standardized provenance envelope for decision records with stage and evidence references (`schemas/common.schema.json`, `schemas/decision.schema.json`, `examples/decision.example.json`).
- Added App Server audit export method with deterministic fingerprinting and sensitive-field redaction (`core/app_server.py`, `core/provenance.py`).
- Added cross-stage linkage for decision and connector-policy paths (proposal, policy evaluation, approval, execution outcome) with machine-readable evidence and human-readable summaries (`core/app_server.py`).
- Added provenance-oriented diagnostics artifact generation and operator command surface (`scripts/run_observability_diagnostics.py`, `Makefile`, `playbooks/operator-observability-diagnostics.md`).
- Added provenance export/redaction test coverage (`tests/test_app_server.py`, `tests/test_provenance.py`).

* * *

<a id="m23-performance-persistence-and-recovery-hardening"></a>

### M23 — Performance, persistence, and recovery hardening

**Status:** Completed (2026-03-09)

**Depends on:** M22 provenance and evidence hardening.

**Unlocks:** defensible operational baselines, safer deployments, more credible production-readiness claims.

<a id="objective"></a>

#### Objective

Raise the runtime from reference deployment to repeatable operational service baseline.

<a id="why-now"></a>

#### Why now

Before v1.0, the project needs stronger evidence around throughput, replay cost, persistence durability, migration behavior, restart correctness, and backup or restore procedures.

<a id="deliverables"></a>

#### Deliverables

- benchmark harness for replay, policy, simulation, connectors, and public API flows
- documented performance envelopes for local and dev profiles
- persistence stress tests and crash or recovery tests
- backup and restore workflow for baseline persistence profile
- migration verification against larger fixture volumes
- idempotent restart behavior checks

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- benchmark runs are reproducible
- crash and restart preserve correctness and idempotency
- migration paths are validated against realistic fixture sizes
- backup and restore procedures are documented and tested
- performance results are included in milestone evidence

<a id="suggested-implementation-notes"></a>

#### Suggested implementation notes

Representative code areas:

- `core/persistence.py`
- `core/event_store.py`
- `core/connector_state_store.py`
- `infra/migrations/`
- new benchmark scripts and tests
- deployment playbooks

<a id="completion-evidence-placeholder"></a>

#### Completion evidence

- Added reproducible benchmark harness covering replay, policy evaluation, simulation, connector execution, and public API flows for local/dev profiles with workload fingerprinting and JSON artifacts (`scripts/run_performance_benchmarks.py`, `make benchmark`, `tmp/diagnostics/m23_benchmarks.latest.json`).
- Added persistence recovery validation for restart idempotency, backup/restore round-trip checks, and migration verification at larger fixture volumes with JSON evidence (`scripts/check_persistence_recovery.py`, `make recovery-check`, `tmp/diagnostics/m23_recovery.latest.json`).
- Added reusable sqlite backup/restore and table-count utilities for operational recovery checks (`core/persistence_recovery.py`).
- Added M23-focused test coverage for backup/restore and benchmark/recovery script smoke validation (`tests/test_persistence_recovery.py`).
- Added M23 operator playbook and command surface updates (`playbooks/performance-persistence-recovery.md`, `Makefile`, `README.md`, `ARCHITECTURE.md`, `STATUS.md`).

* * *

<a id="m24-packaging-extension-contracts-and-partner-onboarding"></a>

### M24 — Packaging, extension contracts, and partner onboarding

**Status:** Completed (2026-03-09)

**Depends on:** M23 performance, persistence, and recovery hardening.

**Unlocks:** external design partners, cleaner contributor workflows, more durable extension ecosystem.

<a id="objective"></a>

#### Objective

Make World-Runtime adoptable by external domain teams.

<a id="why-now"></a>

#### Why now

A runtime can be technically strong and still be hard to adopt. Before v1.0, extension boundaries and onboarding flows need to become supported product surfaces rather than implicit repo knowledge.

<a id="deliverables"></a>

#### Deliverables

- explicit extension contracts for adapters, connector providers, policy packs, and simulators
- packaging and distribution layout improvements
- partner and contributor onboarding guide
- template generator or starter packs for new adapters and connectors
- version compatibility matrix
- improved release bundle for adopters

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- a new partner can create an adapter or connector plugin from supported templates
- extension boundaries are documented and tested
- release artifacts are sufficient for guided onboarding
- compatibility expectations across runtime, protocol, SDK, migrations, and plugins are explicit

<a id="suggested-implementation-notes"></a>

#### Suggested implementation notes

Representative code areas:

- `README.md`
- `ARCHITECTURE.md`
- extension contract docs
- release artifact scripts and manifests
- `examples/` or `templates/`

<a id="completion-evidence-placeholder"></a>

#### Completion evidence

- Added explicit extension contract documentation for adapters, connector plugins, policy packs, and simulation profile boundaries (`docs/EXTENSION_CONTRACTS.md`).
- Added partner onboarding guide and operational playbook with scaffold + validation workflows (`docs/PARTNER_ONBOARDING.md`, `playbooks/partner-onboarding.md`).
- Added scaffold starter templates and generator for adapter + connector plugin bootstrapping (`templates/adapter_starter/`, `templates/connector_plugin_starter/`, `scripts/scaffold_extension.py`).
- Added extension contract validation checks and test coverage (`scripts/check_extension_contracts.py`, `tests/test_extension_contracts.py`, `tests/test_extension_scaffold.py`).
- Added compatibility matrix for runtime, protocol, SDK, migrations, and extension seams (`docs/COMPATIBILITY_MATRIX.md`).
- Expanded release bundle inputs and assertions to include M24 onboarding assets (`scripts/build_release_artifacts.py`, `tests/test_release_artifacts.py`).

* * *

<a id="m25-v10-release-candidate-gate"></a>

### M25 — v1.0 release candidate gate

**Status:** Completed (2026-03-09)

**Depends on:** M24 packaging, extension contracts, and partner onboarding.

**Unlocks:** v1.0 release decision.

<a id="objective"></a>

#### Objective

Convert milestone completion into a release-quality go or no-go gate.

<a id="why-now"></a>

#### Why now

The repo should not declare v1.0 because several good milestones happened. It should declare v1.0 only when release criteria are explicit, executable where possible, and supported by documented evidence.

<a id="deliverables"></a>

#### Deliverables

- v1.0 readiness checklist
- aggregate release candidate test, eval, benchmark, and recovery matrix
- security and trust-boundary review pass
- documentation freeze and changelog
- support policy and compatibility statement
- tagged release candidate artifact set

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- baseline commands pass consistently
- domain, eval, benchmark, provenance, and recovery gates pass
- security and trust-boundary issues are resolved or explicitly waived
- release artifacts are reproducible and documented
- the repository can truthfully claim stable runtime surfaces and production-capable domain deployment readiness

<a id="suggested-implementation-notes"></a>

#### Suggested implementation notes

Representative code areas:

- `STATUS.md`
- `README.md`
- release workflows
- release artifact manifests
- operator and handoff playbooks

<a id="completion-evidence-placeholder"></a>

#### Completion evidence

- Added v1.0 readiness checklist with explicit go/no-go criteria and aggregate command matrix (`docs/RELEASE_READINESS_CHECKLIST.md`).
- Added executable aggregate RC gate command/script with machine-readable diagnostics output (`make m25-validate`, `scripts/check_release_candidate_gate.py`, `tmp/diagnostics/m25_release_candidate_gate.latest.json`).
- Added security and trust-boundary review register with explicit disposition model and waiver section (`docs/SECURITY_TRUST_BOUNDARY_REVIEW.md`).
- Added published support policy and compatibility commitments for protocol/API/SDK/migrations/extensions (`docs/SUPPORT_POLICY.md`).
- Added release changelog and expanded release artifacts to include RC readiness and policy docs (`CHANGELOG.md`, `scripts/build_release_artifacts.py`, `tests/test_release_artifacts.py`).

* * *

<a id="completed-milestone-history-m0m17"></a>

## Completed milestone history (M0–M17)

The milestone history below is intentionally preserved. It is part of the repository’s build record and should remain useful to both human readers and coding agents.

<a id="m0-repo-legibility"></a>

### M0 — Repo legibility

**Status:** Completed

**Completion evidence:** repo legibility docs (`README.md`, `ARCHITECTURE.md`, `ROADMAP.md`), runnable command surface in `Makefile`, baseline playbooks/tests scaffold.

<a id="objective"></a>

#### Objective

Make the repository understandable before making it powerful.

<a id="deliverables"></a>

#### Deliverables

- `README.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- contribution guide
- issue templates
- initial repo layout
- placeholder playbooks
- eval directory skeleton

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- a new engineer can explain the system after reading repo docs
- a coding agent can identify major subsystems and propose implementation steps
- repo structure is stable enough for milestone work

<a id="notes"></a>

#### Notes

This milestone is non-optional. A repo that agents cannot navigate is effectively not buildable in an agent-native way.

* * *

<a id="m1-schemas-and-contracts"></a>

### M1 — Schemas and contracts

**Status:** Completed

**Completion evidence:** versioned JSON schemas in `schemas/`, fixture corpus in `examples/`, schema checks in `scripts/check_schemas.py`, validation tests in `tests/test_schema_validation.py`.

<a id="objective"></a>

#### Objective

Define the stable language of the runtime.

<a id="deliverables"></a>

#### Deliverables

- entity schema
- relationship schema
- event schema
- action proposal schema
- decision record schema
- simulation schema
- initial App Server contract
- sample fixture data

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- schemas validate example fixtures
- protocol examples parse cleanly
- type generation works for selected implementation language(s)

<a id="notes"></a>

#### Notes

This milestone creates the system’s shared vocabulary.

* * *

<a id="m2-event-store-and-projection-kernel"></a>

### M2 — Event store and projection kernel

**Status:** Completed

**Completion evidence:** append-only in-memory event store plus offsets and snapshots (`core/event_store.py`), replay engine (`core/replay_engine.py`), projection behavior tests (`tests/test_replay_engine.py`, `tests/test_projection_basics.py`).

<a id="objective"></a>

#### Objective

Establish deterministic state reconstruction.

<a id="deliverables"></a>

#### Deliverables

- append-only event store
- event replay service
- one projection engine
- snapshot support
- projection tests

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- current state can be rebuilt from events
- replay is deterministic
- projection is idempotent
- snapshots restore correctly

<a id="notes"></a>

#### Notes

Without this milestone, the runtime does not yet exist in a meaningful sense.

* * *

<a id="m3-policy-engine"></a>

### M3 — Policy engine

**Status:** Completed

**Completion evidence:** deterministic policy engine and reports (`core/policy_engine.py`), deny, warn, and require-approval coverage (`tests/test_policy_milestone3.py`).

<a id="objective"></a>

#### Objective

Add safe decision boundaries.

<a id="deliverables"></a>

#### Deliverables

- rule definition format
- policy evaluator
- allow, deny, warn, and require-approval outcomes
- policy reports
- policy tests

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- invalid actions are denied
- approval-requiring actions are flagged
- policy results are durable and inspectable

<a id="notes"></a>

#### Notes

Deterministic safety must come before LLM-enabled proposal systems.

* * *

<a id="m4-simulation-engine"></a>

### M4 — Simulation engine

**Status:** Completed

**Completion evidence:** branch creation, hypothetical application, diffs, and lineage (`core/simulation_engine.py`), isolation tests (`tests/test_simulation_engine.py`).

<a id="objective"></a>

#### Objective

Support safe what-if exploration.

<a id="deliverables"></a>

#### Deliverables

- simulation branch creation
- hypothetical event application
- state comparison tools
- lineage tracking
- simulation tests

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- simulation branches are isolated
- branch results are reproducible
- simulation state does not leak into canonical state

<a id="notes"></a>

#### Notes

This is the first milestone where the runtime begins to feel cognitively useful.

* * *

<a id="m5-reasoning-adapter"></a>

### M5 — Reasoning adapter

**Status:** Completed

**Completion evidence:** reasoning context, retrieval, answer, and proposal surfaces (`core/reasoning_adapter.py`), evidence and non-mutation tests (`tests/test_reasoning_adapter.py`).

<a id="objective"></a>

#### Objective

Add semantic interpretation and explanation without surrendering control.

<a id="deliverables"></a>

#### Deliverables

- context builder
- structured retrieval interface
- LLM adapter
- explanation surface
- proposal generator

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- natural-language questions can be answered from structured state
- explanations cite runtime-visible evidence
- proposals do not directly mutate state

<a id="notes"></a>

#### Notes

The LLM is advisory, not authoritative.

* * *

<a id="m6-app-server"></a>

### M6 — App Server

**Status:** Completed

**Completion evidence:** stable App Server runtime methods and events (`core/app_server.py`), CLI test client (`cli/test_client.py`), end-to-end App Server tests (`tests/test_app_server.py`).

<a id="objective"></a>

#### Objective

Expose the runtime as a harness-ready execution surface.

<a id="deliverables"></a>

#### Deliverables

- session management
- task submission
- event streaming
- approval requests
- eval invocation
- CLI integration
- test client

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- a coding agent can interact with the runtime through stable methods
- tasks stream status updates
- approval paths work end to end

<a id="notes"></a>

#### Notes

This milestone turns the repo into a real harness environment.

* * *

<a id="m7-eval-harness"></a>

### M7 — Eval harness

**Status:** Completed

**Completion evidence:** eval harness and suite manifest (`core/eval_harness.py`, `evals/suites.manifest.json`), runnable eval script (`scripts/run_evals.py`), eval tests (`tests/test_eval_harness.py`).

<a id="objective"></a>

#### Objective

Make correctness, safety, and regressions measurable.

<a id="deliverables"></a>

#### Deliverables

- functional eval suite
- simulation eval suite
- policy eval suite
- reasoning eval suite
- safety eval suite
- benchmark smoke tests

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- evals run in CI
- PRs require passing relevant evals
- regression cases are durable and versioned

<a id="notes"></a>

#### Notes

Evals are a first-class product surface, not an afterthought.

* * *

<a id="m8-domain-adapters"></a>

### M8 — Domain adapters

**Status:** Completed

**Completion evidence:** adapter framework and registry (`adapters/base.py`, `adapters/registry.py`), two adapters with adapter-level schemas and policies (`adapters/supply_network`, `adapters/narrative_world`), adapter checks, tests, and playbooks.

<a id="objective"></a>

#### Objective

Prove that the kernel is general and reusable.

<a id="deliverables"></a>

#### Deliverables

- at least two domain adapters
- adapter-level schemas
- adapter-level policies
- adapter examples
- adapter playbooks

<a id="suggested-first-adapters"></a>

#### Suggested first adapters

- supply network
- narrative world

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- adapters work without kernel changes
- same event, projection, policy, and simulation patterns apply
- domain-specific behavior is isolated from core

<a id="notes"></a>

#### Notes

This is where the architecture proves its range.

* * *

<a id="m9-operator-workflows"></a>

### M9 — Operator workflows

**Status:** Completed

**Completion evidence:** operator workflow runner (`core/operator_workflows.py`), workflow CLI (`scripts/run_operator_workflow.py`), workflow make targets and playbooks, workflow tests (`tests/test_operator_workflows.py`).

<a id="objective"></a>

#### Objective

Make the runtime usable by teams, not just architects.

<a id="deliverables"></a>

#### Deliverables

- quickstart examples
- operational playbooks
- failure recovery workflows
- proposal review workflows
- simulation analysis workflows

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- operators can run common workflows without editing internals
- major runtime actions have documented procedures

* * *

<a id="m10-reference-deployments"></a>

### M10 — Reference deployments

**Status:** Completed

**Completion evidence:** local and dev deployment profiles plus config packs and deployment examples (`infra/`), deployment loader (`core/deployment.py`), deployment bootstrap script (`scripts/deploy_reference.py`), deployment tests (`tests/test_reference_deployments.py`).

<a id="objective"></a>

#### Objective

Demonstrate real use in bounded environments.

<a id="deliverables"></a>

#### Deliverables

- local deployment profile
- dev deployment profile
- sample persistence backend config
- sample LLM provider config
- reference adapter deployments

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- local deployment works out of the box
- example environments are reproducible

* * *

<a id="m11-persistence-adapters"></a>

### M11 — Persistence adapters

**Status:** Completed

**Completion evidence:** persistence abstraction and implementations for events, snapshots, and decisions, migration-backed storage profile, persistence validation and recovery-oriented tests.

<a id="objective"></a>

#### Objective

Move the runtime from in-memory kernel defaults to reproducible persisted state.

<a id="deliverables"></a>

#### Deliverables

- persistence abstraction for core stores
- baseline durable backend profile
- migration strategy
- persistence-focused tests
- documentation for storage assumptions

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- core runtime state can be persisted and restored using supported adapters
- migration path exists for the baseline persistence profile
- persistence tests run in CI and local development

* * *

<a id="m12-app-server-protocol-stabilization"></a>

### M12 — App Server protocol stabilization

**Status:** Completed

**Completion evidence:** explicit protocol definitions, compatibility checks, and version-aware validation for App Server wire contracts.

<a id="objective"></a>

#### Objective

Stabilize the runtime control surface for agents and tools.

<a id="deliverables"></a>

#### Deliverables

- explicit protocol contract definitions
- compatibility policy
- version-aware validation
- protocol test coverage

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- protocol changes are detectable through compatibility checks
- supported contract versions are documented
- agent integrations have a stable baseline surface

* * *

<a id="m13-ci-cd-and-release-automation"></a>

### M13 — CI/CD and release automation

**Status:** Completed

**Completion evidence:** gated CI workflows, release-dry-run support, artifact versioning, and automated validation paths integrated into repository workflows.

<a id="objective"></a>

#### Objective

Make repository quality repeatable and releaseable.

<a id="deliverables"></a>

#### Deliverables

- CI workflow gates
- release automation
- artifact versioning
- automated validation orchestration

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- core test and validation surfaces run in CI
- release artifacts can be produced reproducibly
- milestone progress is easier to verify through automation

* * *

<a id="m14-observability-hardening"></a>

### M14 — Observability hardening

**Status:** Completed

**Completion evidence:** shared observability subsystem (`core/observability.py`), App Server telemetry, trace, and diagnostics methods, operator diagnostics generator (`scripts/run_observability_diagnostics.py`), and diagnostics coverage in tests and playbooks.

<a id="objective"></a>

#### Objective

Make runtime behavior visible enough to operate and debug with confidence.

<a id="deliverables"></a>

#### Deliverables

- structured telemetry
- runtime traces
- operator diagnostics
- observability playbooks
- test coverage for trace and diagnostics surfaces

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- major runtime flows produce inspectable diagnostics
- traces support debugging across subsystem boundaries
- operators have a documented path for runtime inspection

* * *

<a id="m15-integration-reference-stacks"></a>

### M15 — Integration reference stacks

**Status:** Completed

**Completion evidence:** integration stack manifests (`infra/integration_stacks/*.json`), stack loader and validator (`core/integration_stacks.py`), stack smoke command (`scripts/check_integration_stacks.py`), and integration stack test and playbook coverage.

<a id="objective"></a>

#### Objective

Demonstrate repeatable end-to-end deployment shapes that include external systems.

<a id="deliverables"></a>

#### Deliverables

- integration stack manifests
- stack loader and validator
- stack smoke checks
- stack playbooks and examples

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- stack definitions validate and run in supported environments
- external integration layouts are reproducible
- operators can reason about complete stack composition

* * *

<a id="m16-connector-execution-adapters"></a>

### M16 — Connector execution adapters

**Status:** Completed

**Completion evidence:** connector runtime primitives (`core/connectors.py`), App Server connector methods (`core/app_server.py`), integration stack connector execution smoke coverage (`core/integration_stacks.py`), and connector-focused checks and tests (`scripts/check_connectors.py`, `tests/test_connectors.py`).

<a id="objective"></a>

#### Objective

Give the runtime a safe execution surface for inbound and outbound connectors.

<a id="deliverables"></a>

#### Deliverables

- connector runtime primitives
- App Server connector methods
- retries and idempotency handling
- dead-letter handling
- connector tests and checks

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- inbound and outbound connector execution works through supported runtime paths
- connector retries and dead-letter flows are testable
- connector behavior is visible in stack validation and playbooks

* * *

<a id="m17-external-connector-transport-plugins"></a>

### M17 — External connector transport plugins

**Status:** Completed

**Completion evidence:** transport plugin registry and providers (`core/connector_transports.py`), sqlite-backed connector state store (`core/connector_state_store.py` plus `infra/migrations/persistence/0003_connectors.sql`), runtime and App Server dead-letter replay flow (`core/connectors.py`, `core/app_server.py`), and connector plugin persistence and replay coverage (`tests/test_connectors.py`, `tests/test_app_server.py`, `tests/test_persistence_adapters.py`, `scripts/check_connector_plugins.py`).

<a id="objective"></a>

#### Objective

Extend connector execution with provider-specific transport, persistence, and replay behavior.

<a id="deliverables"></a>

#### Deliverables

- transport plugin registry
- provider-specific transport implementations
- persistent connector idempotency and replay state
- dead-letter replay workflows
- validation checks and tests for plugin behavior

<a id="acceptance-criteria"></a>

#### Acceptance criteria

- connector providers can be added through the transport plugin seam
- connector state survives supported persistence workflows
- dead-letter replay is durable and testable
- plugin validation catches unsupported or invalid configurations

* * *

<a id="cross-cutting-requirements"></a>

## Cross-cutting requirements

Every milestone must preserve and improve the following qualities.

<a id="documentation"></a>

### Documentation

Every milestone must update:

- documentation
- examples
- playbooks
- tests

<a id="agent-legibility"></a>

### Agent legibility

Every milestone must improve:

- naming clarity
- task decomposition
- schema discoverability
- eval coverage

<a id="safety-and-governance"></a>

### Safety and governance

Every milestone must preserve:

- explicit trust boundaries
- approval enforcement
- simulation isolation
- auditability
- policy visibility

<a id="operational-quality"></a>

### Operational quality

Every milestone should strengthen:

- diagnostics
- reproducibility
- failure handling
- release evidence

* * *

<a id="standard-milestone-execution-pattern"></a>

## Standard milestone execution pattern

For any milestone:

1. restate acceptance criteria before coding
2. add failing tests or validation checks
3. scaffold interfaces
4. implement the minimal working path
5. update docs, examples, and playbooks
6. add or extend evals and diagnostics
7. run milestone-specific validation
8. update `STATUS.md` with completion evidence and next recommended milestone

* * *

<a id="suggested-validation-discipline"></a>

## Suggested validation discipline

Each milestone should separate validation into three layers:

<a id="baseline-validation"></a>

### Baseline validation

- core tests
- schema validation
- lint or static checks if present

<a id="milestone-specific-validation"></a>

### Milestone-specific validation

- commands or test targets directly tied to the milestone
- smoke runs for new examples or workflows
- targeted diagnostics or compatibility checks

<a id="broader-regression-validation"></a>

### Broader regression validation

- adapter checks
- eval runs
- deployment smoke tests
- release-dry-run or equivalent, when touched surfaces justify it

This keeps milestone threads focused while still encouraging strong regression coverage.

* * *

<a id="strategic-direction"></a>

## Strategic direction

The near-term goal is not to build a universal system.

The near-term goal is to create:

- a stable kernel
- a strong harness
- repeatable extension patterns
- governed external effects
- trustworthy operator and agent workflows

If enough runtimes like this exist and become interoperable, larger networked cognitive systems may emerge later.

That is a direction, not a dependency for success.

# World Runtime Roadmap

_Last updated: 2026-03-12 (America/Chicago)_

## Goal

Create a harness-first, agent-runnable reference runtime for executable world-model systems.

World Runtime is not trying to become a generic application framework. Its purpose is to establish a durable runtime shape for systems built around:

- explicit world state
- append-only events
- deterministic projection
- simulation of possible futures
- policy-governed orchestration
- agent-facing interfaces for planning, execution, and review

## Roadmap Principles

Every milestone should improve the repository along four dimensions:

1. Legibility: humans and agents can understand the system quickly.
2. Runnable quality: the repo is executable, testable, and observable.
3. Governability: external effects, approvals, and trust boundaries remain explicit.
4. Extensibility: domain teams can add adapters, simulators, policies, and connectors without rewriting the kernel.

## Current Phase And Next Milestone

- Milestone state: **M0-M25 complete**
- Current phase: **v1.0 release candidate**
- Most recent milestone: **M25 - v1.0 release candidate gate**
- Next milestone candidate: **v1.0 GA release execution and post-RC stabilization**
- Root-doc stance: this file is the strategic and historical roadmap; use [STATUS.md](STATUS.md) for the current operational snapshot and [CHANGELOG.md](CHANGELOG.md) for release-by-release narrative

## Release Trajectory

### v0.1 - Reference repo and local runtime kernel

M0-M17 establish the reference architecture, core runtime kernel, App Server surface, eval harness, operator workflows, persistence, observability, integration stacks, and connector/plugin seams.

### v0.2 - Governed external effects and stronger public runtime surfaces

M18-M20 add policy-governed connector behavior, attributable approval workflows, and a supported public API/SDK surface.

### v0.3 - Broader domain proof and operational hardening

M21-M24 extend the system into safety-constrained domains, provenance, recovery, performance, and partner-ready extension support.

### v1.0 - Production-capable runtime for domain deployments

M25 converts milestone completion into an explicit release-candidate gate with documented readiness criteria, support commitments, and artifact evidence.

## Near-Term Roadmap

### v1.0 GA release execution and post-RC stabilization

Objective:

- convert RC readiness into a disciplined GA release decision and a credible first patch window

Likely work areas:

- release tagging and signoff discipline
- downstream adoption and partner verification checks
- version alignment between repo package/versioned artifacts and broader release labeling
- first post-RC bug-fix and support window readiness
- documentation and release workflow polish based on RC feedback

Success criteria:

- GA release criteria are explicit and executable
- versioning language is aligned across repo metadata, release artifacts, and public docs
- support expectations for v1.x are clear to contributors and adopters
- downstream users can validate the supported integration path without repo archaeology

## Active Milestone Queue (Completed Late-Stage Arc)

The late-stage arc below is preserved in more detail because it defines the path to the current release-candidate posture.

### M18 - Connector policy guardrails

- Status: Completed (2026-03-09)
- Objective: move connectors from transport plumbing to policy-governed integration surfaces
- Delivered: provider-aware connector policy scope, source validation hooks, approval-gated execution, durable connector policy decision records, guardrail playbook coverage
- Why it mattered: M17 made connectors possible; M18 made them governable

### M19 - Approval workflow and actor identity hardening

- Status: Completed (2026-03-09)
- Objective: make approvals, escalations, and overrides attributable
- Delivered: actor identity payloads, role/capability checks, explicit approval lifecycle states, durable approval-chain replay
- Why it mattered: approval-required runtime actions needed identity and authorization credibility

### M20 - Public API surface and SDK starter

- Status: Completed (2026-03-09)
- Objective: expose supported third-party entry points without requiring internal imports
- Delivered: versioned HTTP API, starter Python SDK, compatibility/deprecation notes, example client, public-surface compatibility checks
- Why it mattered: it turned a repo-internal harness into an externally supportable integration surface

### M21 - Safety-constrained domain expansion

- Status: Completed (2026-03-09)
- Objective: prove the kernel in a high-constraint operational domain
- Delivered: `adapter-air-traffic`, constrained scenario pack, explicit deny/warn/require-approval/simulate-before-action patterns, eval and operator coverage
- Why it mattered: the runtime needed proof under stronger governance pressure than the initial reference domains

### M22 - Provenance and evidence hardening

- Status: Completed (2026-03-09)
- Objective: make runtime decisions audit-grade
- Delivered: provenance envelope support, cross-stage evidence linkage, deterministic audit export, redaction rules, provenance diagnostics
- Why it mattered: consequential runtime decisions need inspectable, reproducible evidence

### M23 - Performance, persistence, and recovery hardening

- Status: Completed (2026-03-09)
- Objective: raise the runtime from reference deployment to operational baseline
- Delivered: benchmark harness, persistence recovery validation, backup/restore utilities, migration-volume checks, reproducible diagnostics artifacts
- Why it mattered: v1.0 claims required repeatable performance and recovery evidence, not just functional correctness

### M24 - Packaging, extension contracts, and partner onboarding

- Status: Completed (2026-03-09)
- Objective: make World Runtime adoptable by external domain teams
- Delivered: extension contract docs, scaffold templates, validation tooling, compatibility matrix, partner onboarding assets, improved release bundles
- Why it mattered: a strong runtime is still hard to adopt if extension seams are implicit

### M25 - v1.0 release candidate gate

- Status: Completed (2026-03-09)
- Objective: convert milestone completion into a release-quality go/no-go gate
- Delivered: readiness checklist, aggregate validation matrix, security/trust-boundary review, support policy, changelog, tagged RC artifact set
- Why it mattered: the repo should claim v1.0 readiness only through explicit, executable release evidence

## Historical Milestone Appendix (M0-M17)

The milestone history below is intentionally preserved as part of the repository’s build record. It is condensed for scanability but still captures the milestone arc and completion character.

### M0-M5: Runtime foundation

- M0 - Repo legibility: established baseline docs, repo layout, and runnable command surface so humans and coding agents could navigate the project
- M1 - Schemas and contracts: defined the stable language of entities, events, proposals, decisions, simulations, and protocol fixtures
- M2 - Event store and projection kernel: introduced deterministic state reconstruction, replay, and snapshots
- M3 - Policy engine: added allow/deny/warn/require-approval decision boundaries
- M4 - Simulation engine: introduced isolated what-if branches, diffs, and lineage tracking
- M5 - Reasoning adapter: added LLM-assisted interpretation and proposal generation without direct authority over canonical state

### M6-M10: Harness and operations baseline

- M6 - App Server: exposed the runtime as a stable harness-ready execution surface
- M7 - Eval harness: made correctness, regressions, and safety measurable through durable suites
- M8 - Domain adapters: proved the kernel could support multiple domain packages without kernel rewrites
- M9 - Operator workflows: added quickstart, proposal review, simulation analysis, and failure-recovery flows
- M10 - Reference deployments: introduced reproducible local and dev deployment profiles

### M11-M17: Persistence, protocol, and external effects

- M11 - Persistence adapters: moved core runtime state beyond in-memory defaults into reproducible persisted storage
- M12 - App Server protocol stabilization: made wire compatibility explicit and testable
- M13 - CI/CD and release automation: turned quality and artifact generation into repeatable workflow gates
- M14 - Observability hardening: added telemetry, traces, diagnostics, and operator inspection paths
- M15 - Integration reference stacks: demonstrated repeatable end-to-end deployment shapes with external systems
- M16 - Connector execution adapters: added inbound/outbound execution surfaces, retries, and dead-letter handling
- M17 - External connector transport plugins: added provider-specific transport seams, persistent connector state, and replay behavior

## Domain Package Rollup

- Root roadmap tracks rollup state only for domain packages.
- `adapter-world-game` carries richer package-local planning in [adapters/world_game/ROADMAP.md](adapters/world_game/ROADMAP.md) and package-local status in [adapters/world_game/STATUS.md](adapters/world_game/STATUS.md).
- Root docs should avoid duplicating package-level milestone detail unless it changes top-level strategy or release posture.

## Cross-Cutting Requirements

### Documentation

Every milestone should update:

- documentation
- examples
- playbooks
- tests

### Agent Legibility

Every milestone should improve:

- naming clarity
- task decomposition
- schema discoverability
- eval coverage

### Safety And Governance

Every milestone should preserve:

- explicit trust boundaries
- approval enforcement
- simulation isolation
- auditability
- policy visibility

### Operational Quality

Every milestone should strengthen:

- diagnostics
- reproducibility
- failure handling
- release evidence

## Validation Discipline

### Standard milestone execution pattern

1. Restate acceptance criteria before coding.
2. Add failing tests or validation checks.
3. Scaffold interfaces.
4. Implement the minimal working path.
5. Update docs, examples, and playbooks.
6. Add or extend evals and diagnostics.
7. Run milestone-specific validation.
8. Update current-state docs and release history where applicable.

### Baseline validation

- core tests
- schema validation
- lint or static checks if present

### Milestone-specific validation

- commands or test targets directly tied to the milestone
- smoke runs for new examples or workflows
- targeted diagnostics or compatibility checks

### Broader regression validation

- adapter checks
- eval runs
- deployment smoke tests
- release-dry-run or equivalent when touched surfaces justify it

## Strategic Direction

The near-term goal is not to build a universal system.

The near-term goal is to create:

- a stable kernel
- a strong harness
- repeatable extension patterns
- governed external effects
- trustworthy operator and agent workflows

If enough runtimes like this exist and become interoperable, larger networked cognitive systems may emerge later. That is a direction, not a dependency for success.

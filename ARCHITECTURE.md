# World Runtime Architecture

<a id="1-architectural-intent"></a>

## 1\. Architectural intent

World Runtime is a system for modeling, simulating, and orchestrating complex environments using explicit world state.

It is designed around one core idea:

> the system should understand the world it operates in, not just the workflows that pass through it.

This architecture supports humans, services, and AI agents working against a shared model of reality.

<a id="2-top-level-system"></a>

## 2\. Top-level system

```
World Graph
    ↑
Event Engine
    ↓
Projection Engine
    ↓
Policy Engine
    ↓
Simulation Engine
    ↓
Orchestration Layer
    ↔
Reasoning Layer
    ↔
App Server / Clients / Agents
```

<a id="3-core-subsystems"></a>

## 3\. Core subsystems

<a id="31-world-graph"></a>

### 3.1 World Graph

The World Graph stores the structural model of the system:

- entities
- relationships
- projected state references

Examples of entities:

- person
- organization
- machine
- product
- location
- character
- contract
- resource

Responsibilities:

- canonical identity
- relationship modeling
- queryable structure
- snapshot support

The World Graph is the structural backbone, but it is not the source of truth by itself. Canonical truth comes from events plus projection.

* * *

<a id="32-event-engine"></a>

### 3.2 Event Engine

The Event Engine records immutable changes over time.

Responsibilities:

- append-only event log
- event ordering/versioning
- replay support
- event correlation/causation
- triggering projection updates

An event is not a command.  
An event is a durable record that something happened.

Examples:

- supplier\_failed
- shipment\_delayed
- contract\_signed
- inventory\_adjusted
- character\_betrayed\_ally

* * *

<a id="33-projection-engine"></a>

### 3.3 Projection Engine

The Projection Engine rebuilds current state from the event log.

Responsibilities:

- deterministic replay
- materialized views
- snapshots
- incremental rebuild
- projection versioning

Projections are derived state, not canonical truth.

Design rule:

- canonical truth = events
- current usable state = projections

* * *

<a id="34-policy-engine"></a>

### 3.4 Policy Engine

The Policy Engine evaluates proposed actions against explicit rules and approval boundaries.

Responsibilities:

- validate proposals
- deny invalid actions
- warn on risky actions
- require approval where needed
- emit policy decision records

Policy decisions should be deterministic before any LLM-based reasoning is involved.

Examples:

- deny deleting canonical state
- require approval for schema migration
- warn if a proposal conflicts with hard capacity constraints

* * *

<a id="35-simulation-engine"></a>

### 3.5 Simulation Engine

The Simulation Engine creates isolated branches of world state for what-if exploration.

Responsibilities:

- branch from canonical state
- apply hypothetical events
- compare projected outcomes
- preserve simulation lineage
- prevent branch leakage into production state

A simulation branch must never mutate canonical state directly.

* * *

<a id="36-reasoning-layer"></a>

### 3.6 Reasoning Layer

The Reasoning Layer provides semantic interpretation and explanation.

Responsibilities:

- translate natural language into structured queries
- retrieve relevant context
- explain world state
- summarize simulation results
- generate candidate proposals

The Reasoning Layer is advisory.

It may:

- interpret
- summarize
- propose
- explain

It may not:

- directly mutate canonical state
- bypass policy
- bypass approvals

* * *

<a id="37-orchestration-layer"></a>

### 3.7 Orchestration Layer

The Orchestration Layer coordinates candidate actions and produces decision records.

Responsibilities:

- gather proposals
- evaluate conflicts
- rank alternatives
- combine policy and simulation results
- create decision records
- dispatch approved actions

This is the coordination layer of the runtime.

* * *

<a id="38-app-server"></a>

### 3.8 App Server

The App Server exposes the runtime to:

- Codex
- CLI clients
- API clients
- internal tools
- future agent systems

Responsibilities:

- create persistent sessions/threads
- accept tasks
- stream progress/events
- expose runtime methods
- request approvals
- return diffs/results
- run evals

The App Server is the main harness surface.

* * *

<a id="39-implemented-runtime-surfaces"></a>

### 3.9 Implemented runtime surfaces

The current implementation includes concrete runtime surfaces for:

- event store + replay + snapshots
- deterministic policy evaluation with durable policy reports
- simulation branches with isolation and lineage tracking
- reasoning adapter with evidence-backed responses and non-mutating proposal generation
- managed runtime host supervision for declarative local services with readiness/health probes, restart policy, and lifecycle telemetry
- provider registry and task-profile catalogs with deterministic routing, bounded fallback semantics, and inspectable routing traces on top of the managed-service substrate
- additive runtime-admin surfaces for runtime inventory, provider inventory, task resolution, and bounded reconcile through the App Server, Public API `/v1`, and starter SDK
- a managed local AI reference stack for schema-constrained structured extraction, using the managed-service host, routing substrate, and runtime-admin surfaces without promoting those manifests to new stable embedding contracts
- App Server methods/events for:
  - session
  - task
  - approval
  - eval
  - simulation
  - policy/proposal/decision workflows
  - runtime admin inventory, provider inspection, task resolution, and reconcile
- public API `v1` HTTP wrapper and starter Python SDK surface for external clients
- eval harness for functional/simulation/policy/reasoning/safety/regression checks
- adapter registry with supply-network, air-traffic, and world-game adapters
- operator workflow runner and reference deployment loader
- connector runtime with policy guardrails (provider/source-aware policy scope, approval-gated execution, durable connector decision records)
- integration stack loader/validator for external ingress/egress patterns (`core/integration_stacks.py`)
- integration stack smoke checks (`scripts/check_integration_stacks.py`)
- connector execution runtime for inbound/outbound adapters with retries, transport plugins, persistent idempotency state, and dead-letter queues/replay (`core/connectors.py`, `core/connector_state_store.py`, `core/connector_transports.py`)
- App Server connector execution and dead-letter APIs (`connector.inbound.run`, `connector.outbound.run`, `connector.dead_letter.list`, `connector.dead_letter.replay`)
- provenance-aware decision envelopes and audit export surface with redaction/fingerprinting (`decision.provenance`, `audit.export`, `scripts/run_observability_diagnostics.py --include-audit-export`)
- operational hardening harness for benchmark reproducibility, restart/idempotency recovery checks, migration-volume verification, and backup/restore evidence (`scripts/run_performance_benchmarks.py`, `scripts/check_persistence_recovery.py`, `playbooks/performance-persistence-recovery.md`)
- extension-contract and partner onboarding surfaces with scaffold templates, extension contract checks, and compatibility matrix guidance (`docs/EXTENSION_CONTRACTS.md`, `docs/PARTNER_ONBOARDING.md`, `docs/COMPATIBILITY_MATRIX.md`, `scripts/scaffold_extension.py`, `scripts/check_extension_contracts.py`)
- release-candidate readiness gate with explicit go/no-go checklist, security/trust-boundary review register, support policy, and aggregate diagnostics artifact (`scripts/check_release_candidate_gate.py`, `docs/RELEASE_READINESS_CHECKLIST.md`, `docs/SECURITY_TRUST_BOUNDARY_REVIEW.md`, `docs/SUPPORT_POLICY.md`)

* * *

<a id="310-observability-layer"></a>

### 3.10 Observability layer

The Observability layer provides structured telemetry, runtime traces, and operator-facing diagnostics.

Responsibilities:

- record structured runtime telemetry events
- track request/task/eval traces with status and duration
- expose summary and dashboard views for operators
- preserve additive compatibility with existing runtime methods

Current implementation includes:

- shared observability store (`core/observability.py`)
- App Server methods for telemetry/traces/dashboard retrieval
- telemetry instrumentation across app server, eval harness, workflows, and deployment smoke checks
- diagnostics artifact generator (`scripts/run_observability_diagnostics.py`)

<a id="4-canonical-data-flow"></a>

## 4\. Canonical data flow

<a id="41-production-flow"></a>

### 4.1 Production flow

```
Action Proposal
  ↓
Policy Evaluation
  ↓
Approval (if required)
  ↓
Execution
  ↓
Event Append
  ↓
Projection Update
  ↓
World State Queryable

```

<a id="42-simulation-flow"></a>

### 4.2 Simulation flow

```
Current Canonical State
  ↓
Create Simulation Branch
  ↓
Apply Hypothetical Events / Actions
  ↓
Run Projection / Analysis
  ↓
Compare Outcomes
  ↓
Return Results

```

<a id="43-reasoning-flow"></a>

### 4.3 Reasoning flow

```
Natural Language Request
  ↓
Context Builder
  ↓
Structured Query / Retrieval
  ↓
LLM Interpretation
  ↓
Explanation / Proposal

```

<a id="5-core-abstractions"></a>

## 5\. Core abstractions

<a id="entity"></a>

### Entity

A durable object in the world.

Minimum fields:

- `entity_id`
- `entity_type`
- `attributes`
- `created_at`
- `version`

<a id="relationship"></a>

### Relationship

A typed edge between entities.

Minimum fields:

- `relationship_id`
- `from_entity_id`
- `to_entity_id`
- `relationship_type`
- `attributes`
- `effective_at`

<a id="event"></a>

### Event

An immutable record of change.

Minimum fields:

- `event_id`
- `event_type`
- `occurred_at`
- `recorded_at`
- `actor`
- `subject_entities`
- `payload`
- `causation_id`
- `correlation_id`

<a id="projection"></a>

### Projection

A materialized state view derived from events.

<a id="rule"></a>

### Rule

A deterministic condition or validation.

<a id="policy"></a>

### Policy

A ruleset that returns:

- allow
- deny
- warn
- require\_approval

<a id="action-proposal"></a>

### Action Proposal

A candidate mutation or response.

<a id="simulation-run"></a>

### Simulation Run

A branch with assumptions, inputs, outputs, and lineage.

<a id="decision-record"></a>

### Decision Record

A durable record of orchestration output.

<a id="6-trust-boundaries"></a>

## 6\. Trust boundaries

<a id="61-trust-safety-guarantees"></a>

### 6.1 Trust/safety guarantees

The current runtime enforces and tests these invariants:

- simulation branches do not leak into canonical state
- approvals are enforced for policy-gated proposal paths
- reasoning queries and proposal generation do not mutate canonical event log

<a id="humans"></a>

### Humans

May:

- inspect state
- submit proposals
- approve sensitive actions

<a id="agents-llms"></a>

### Agents / LLMs

May:

- inspect context
- answer questions
- summarize
- generate proposals

May not:

- mutate canonical state directly
- bypass policy checks
- bypass approvals

<a id="runtime"></a>

### Runtime

Owns:

- event append
- projection updates
- policy enforcement
- simulation isolation
- decision execution

<a id="7-domain-neutral-kernel-domain-specific-adapters"></a>

## 7\. Domain-neutral kernel, domain-specific adapters

The kernel must remain neutral.

Adapters define domain-specific:

- entity types
- event taxonomies
- projections
- policies
- simulators

Example adapter categories:

- enterprise
- supply network
- semantic governance
- safety-constrained air traffic

This separation is essential for long-term reuse.

<a id="8-technology-stance-for-v01"></a>

## 8\. Technology stance for v0.1

Implementation technology is intentionally flexible, but v0.1 should support:

- typed schemas
- append-only event storage
- deterministic projection
- pluggable policy engine
- pluggable simulation engine
- LLM adapter abstraction
- local-first App Server
- eval-first workflow

<a id="9-non-goals-for-v01"></a>

## 9\. Non-goals for v0.1

v0.1 does not attempt to solve:

- planet-scale federation
- deep autonomy
- general AGI planning
- universal ontology design
- fully distributed trustless coordination

Those are future evolution paths, not starter architecture concerns.

<a id="10-summary"></a>

## 10\. Summary

World Runtime is best understood as:

- not an app
- not just a graph
- not just an event system
- not just an AI layer

It is a runtime that lets humans and agents interact with an executable model of a world through:

- events
- projections
- simulations
- policies
- orchestrated decisions

* * *

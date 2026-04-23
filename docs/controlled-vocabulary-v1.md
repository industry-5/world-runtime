# Controlled Vocabulary v1

_Last updated: 2026-03-28 (America/Chicago)_

This document defines the shared `world-runtime` glossary and lightweight taxonomy for the runtime substrate.

Its purpose is to keep one stable language for:

- structural runtime records
- governance and decision flow
- derived and read-only runtime surfaces
- the explicit handoff point where domain adapters take over

`world-runtime` owns runtime substrate vocabulary, not domain semantics. This page does not rename schemas, APIs, protocol methods, or storage artifacts. It aligns the current shipped language that already exists in the repository contracts.

Private lab and downstream UI terms do not belong in this core vocabulary. Use [docs/ui-vocabulary-v1.md](./ui-vocabulary-v1.md) for shell, scene, visualization, and generic media-display language, and use [docs/ui-visual-design.md](./ui-visual-design.md) for visual defaults and layout guidance.

## Vocabulary Method

- glossary: the primary front door; short definitions for the runtime terms that appear across contracts and docs
- taxonomy: the organizing frame inside the glossary; terms are grouped by authority and state role
- ontology: deferred; `world-runtime` v1 does not define a broad upstream world-model ontology

## Taxonomy By Authority Layer

| Authority layer | Role in the runtime | Representative terms |
| --- | --- | --- |
| runtime-authoritative structural state | core record shapes that let the runtime model world structure and change over time | entity, relationship, event |
| runtime-governed decision and workflow state | generic records for proposing, evaluating, approving, and executing action | proposal, decision, policy, rule, simulation, approval, actor, adapter |
| derived and advisory runtime surfaces | read-only or explanatory surfaces derived from authoritative state and workflow activity | projection, provenance, evidence |
| app-server operational terms | harness-level runtime objects that support interaction with the system | session, task |
| domain extension vocabulary | domain-owned nouns and lifecycle language layered on top of inherited runtime terms | `market_venue`, `utility_asset`, `wg_region`, domain-specific projections and policy packs |

## Term Registry

### Runtime-Authoritative Structural State

#### Entity

- Display label: `Entity`
- Machine label / contract anchor: `entity`; [schemas/entity.schema.json](../schemas/entity.schema.json)
- Concise definition: a generic runtime record for something with stable identity in the world model
- Boundary statement: `world-runtime` defines the record shape and identity role of an entity, but domains define concrete `entity_type` values and their semantics

#### Relationship

- Display label: `Relationship`
- Machine label / contract anchor: `relationship`; [schemas/relationship.schema.json](../schemas/relationship.schema.json)
- Concise definition: a generic runtime record that links two entities with a typed connection
- Boundary statement: `world-runtime` defines the structural join and lifecycle shape of a relationship, but domains define concrete `relationship_type` values and what those links mean

#### Event

- Display label: `Event`
- Machine label / contract anchor: `event`; [schemas/event.schema.json](../schemas/event.schema.json)
- Concise definition: an append-only runtime record that something happened at a point in time
- Boundary statement: `world-runtime` defines the durable event envelope and replay role of events, but domains define concrete `event_type` values and domain payload meaning

### Runtime-Governed Decision And Workflow State

#### Proposal

- Display label: `Proposal`
- Machine label / contract anchor: `proposal`; [schemas/proposal.schema.json](../schemas/proposal.schema.json)
- Concise definition: a generic action candidate submitted for policy, approval, and decision workflows
- Boundary statement: `world-runtime` defines proposal structure and lifecycle posture, but domains define concrete `proposal_type`, `action_type`, and domain-specific effects

#### Decision

- Display label: `Decision`
- Machine label / contract anchor: `decision`; [schemas/decision.schema.json](../schemas/decision.schema.json)
- Concise definition: a runtime record that captures which proposal or action path was selected, with policy and approval context
- Boundary statement: `world-runtime` defines the generic decision envelope and audit role, but domains define the business or world meaning of the selected action

#### Policy

- Display label: `Policy`
- Machine label / contract anchor: `policy`; [schemas/policy.schema.json](../schemas/policy.schema.json)
- Concise definition: a generic rule pack that evaluates actions, events, adapters, or connector traffic against explicit outcomes
- Boundary statement: `world-runtime` defines policy structure and allowed outcome vocabulary, but domains define policy content, scopes, and domain-specific guardrails

#### Rule

- Display label: `Rule`
- Machine label / contract anchor: `rule`; [schemas/rule.schema.json](../schemas/rule.schema.json)
- Concise definition: an individual policy condition and outcome unit inside a policy pack
- Boundary statement: `world-runtime` defines the rule container and evaluation role, but domains and operators define the actual conditions, thresholds, and domain intent

#### Simulation

- Display label: `Simulation`
- Machine label / contract anchor: `simulation`; [schemas/simulation.schema.json](../schemas/simulation.schema.json)
- Concise definition: a bounded what-if run that branches from a known base without mutating canonical runtime state directly
- Boundary statement: `world-runtime` defines the generic simulation record and isolation boundary, but domains define simulation semantics, assumptions, and scenario-specific outcomes

#### Approval

- Display label: `Approval`
- Machine label / contract anchor: `approval`; [schemas/common.schema.json](../schemas/common.schema.json), [schemas/decision.schema.json](../schemas/decision.schema.json), [APP_SERVER_PROTOCOL.md](../APP_SERVER_PROTOCOL.md)
- Concise definition: the generic governance status and workflow step that records whether a proposal or decision path is permitted to proceed
- Boundary statement: `world-runtime` defines approval status language and enforcement posture, but domains and deployments define who must approve, why, and under what circumstances

#### Actor

- Display label: `Actor`
- Machine label / contract anchor: `actorRef`; [schemas/common.schema.json](../schemas/common.schema.json)
- Concise definition: a generic reference to the human, agent, service, system, or organization participating in runtime activity
- Boundary statement: `world-runtime` defines the reference shape and generic actor classes, but domains define domain roles, capabilities, and organizational meaning beyond the shared reference envelope

#### Adapter

- Display label: `Adapter`
- Machine label / contract anchor: `DomainAdapter`; [docs/EXTENSION_CONTRACTS.md](./EXTENSION_CONTRACTS.md), [adapters/base.py](../adapters/base.py)
- Concise definition: a domain extension package that brings concrete taxonomies, fixtures, policies, and scenario behavior into the runtime through a stable contract
- Boundary statement: `world-runtime` defines the adapter seam and required abstract members, but adapters own domain vocabularies and must not redefine core runtime terms incompatibly

### Derived And Advisory Runtime Surfaces

#### Projection

- Display label: `Projection`
- Machine label / contract anchor: `projection`; [schemas/projection.schema.json](../schemas/projection.schema.json), [ARCHITECTURE.md](../ARCHITECTURE.md)
- Concise definition: a derived read model built from events for current-state, summary, index, or view-oriented consumption
- Boundary statement: a projection is a consumption surface, not an authoritative mutation path; domains may define projection names and shapes, but projections do not replace canonical event-backed truth

#### Provenance

- Display label: `Provenance`
- Machine label / contract anchor: `provenanceEnvelope`; [schemas/common.schema.json](../schemas/common.schema.json), [schemas/decision.schema.json](../schemas/decision.schema.json)
- Concise definition: the generic trace context that explains how a runtime artifact was produced, reviewed, and linked to supporting evidence
- Boundary statement: `world-runtime` defines the shared provenance envelope and stage structure, but domains define artifact-specific provenance stories and workflow meanings

#### Evidence

- Display label: `Evidence`
- Machine label / contract anchor: `evidenceRef`; [schemas/common.schema.json](../schemas/common.schema.json), [schemas/proposal.schema.json](../schemas/proposal.schema.json)
- Concise definition: a generic reference to supporting material used in policy, review, decision, or provenance flows
- Boundary statement: `world-runtime` defines the reference shape for evidence, but domains define what counts as persuasive evidence and what the referenced material means

### App-Server Operational Terms

#### Session

- Display label: `Session`
- Machine label / contract anchor: `session`; [APP_SERVER_PROTOCOL.md](../APP_SERVER_PROTOCOL.md), [core/app_server.py](../core/app_server.py)
- Concise definition: an app-server interaction scope that groups runtime activity under a stable conversational or operational context
- Boundary statement: sessions are harness-level runtime objects, not domain entities; domains may participate in session-scoped workflows but should not collapse their own business objects into session terminology

#### Task

- Display label: `Task`
- Machine label / contract anchor: `task`; [APP_SERVER_PROTOCOL.md](../APP_SERVER_PROTOCOL.md), [core/app_server.py](../core/app_server.py)
- Concise definition: an app-server work item submitted against a session and tracked through queued, running, and completed states
- Boundary statement: tasks are harness-level execution records, not domain proposals or decisions, even when a task happens to invoke a domain workflow

## Core Boundary

`world-runtime` defines the shape and governance role of generic runtime nouns.

Adapters and downstream domains define:

- concrete `entity_type`
- concrete `event_type`
- concrete `relationship_type`
- concrete `proposal_type`
- concrete `action_type`
- scenario semantics
- domain lifecycle language
- domain-specific projection names, policy packs, and workflow stages

The runtime owns interoperable envelopes. Domains own the world-specific meanings carried inside those envelopes.

## What Stays Downstream

The following kinds of vocabulary remain domain-owned and should not be promoted into core `world-runtime` vocabulary in this v1 document:

- sector nouns such as `market_venue`, `utility_asset`, `trading_firm`, `wg_region`, and `wg_policy_instrument`
- domain-specific projection names such as world, city, market, or canon-specific read models
- domain-specific policy packs and rule labels
- domain-specific workflow stages, workshop phases, editorial states, or approval semantics beyond the shared runtime approval language
- private UI shell and stage terms such as `lab-shell`, `lab-stage`, rails, trays, docks, scene catalogs, media previews, or UI-facing provenance/readiness display states; keep these in [docs/ui-vocabulary-v1.md](./ui-vocabulary-v1.md)

These downstream terms may inherit the generic runtime envelopes, but they do not become core runtime vocabulary merely because they are important inside one adapter or downstream product.

## Inheritance Rules For Downstream Repos

Downstream repos and adapters should follow these rules:

- inherit the core runtime vocabulary defined here
- extend it with domain vocabulary rather than replacing it
- do not redefine core terms such as entity, event, proposal, policy, projection, or simulation with incompatible meanings
- keep domain-specific semantics in adapter or downstream documentation, schemas, and workflows
- do not promote derived or advisory domain artifacts into authoritative runtime truth without an explicit domain-governed workflow that makes that promotion intentional and auditable

## Contract Notes

This document is documentation-only.

It does not introduce:

- schema changes
- protocol changes
- API renames
- adapter naming lint
- new compatibility guarantees beyond the existing published contracts

Current anchors for this vocabulary include:

- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [docs/EXTENSION_CONTRACTS.md](./EXTENSION_CONTRACTS.md)
- [schemas/common.schema.json](../schemas/common.schema.json)
- [schemas/entity.schema.json](../schemas/entity.schema.json)
- [schemas/event.schema.json](../schemas/event.schema.json)
- [schemas/proposal.schema.json](../schemas/proposal.schema.json)
- [schemas/decision.schema.json](../schemas/decision.schema.json)
- [schemas/policy.schema.json](../schemas/policy.schema.json)
- [schemas/projection.schema.json](../schemas/projection.schema.json)
- [schemas/simulation.schema.json](../schemas/simulation.schema.json)
- [APP_SERVER_PROTOCOL.md](../APP_SERVER_PROTOCOL.md)

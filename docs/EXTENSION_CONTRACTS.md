# Extension Contracts

World Runtime supports four first-class extension seams for partner teams.

## 1. Domain adapters

Adapter implementations must satisfy `adapters.base.DomainAdapter`:

- `adapter_id` (stable id, format recommendation: `adapter-<slug>`)
- `domain_name` (human-readable)
- `entity_types` and `event_types` (declared taxonomies)
- `scenario_dir(repo_root)`
- `default_policy_path(repo_root)`
- `adapter_schema_paths(repo_root)`

Contract boundaries:

- Adapter code may define domain taxonomies and fixtures.
- Adapter code may not bypass policy/approval enforcement in `core/app_server.py`.
- Adapter policy packs should validate against `schemas/policy.schema.json`.

Starter template:

- `templates/adapter_starter/`
- Scaffold command: `python3 scripts/scaffold_extension.py adapter --name "My Domain" --output-dir tmp/my-domain-adapter`

## 2. Connector transport plugins

Connector plugins must satisfy `core.connector_transports.TransportPlugin`:

- `provider` string (stable provider id)
- `send(payload, attempt, auth, options) -> dict`

Contract boundaries:

- Plugin code receives payload/auth/options and returns provider response.
- Plugin code does not decide policy outcomes; policy decisions happen before transport execution.
- Plugin ids must be provider-scoped and referenced by outbound requests via `transport_plugin.provider`.

Starter template:

- `templates/connector_plugin_starter/`
- Scaffold command:
  `python3 scripts/scaffold_extension.py connector-plugin --name "My Queue" --provider "my.queue" --output-dir tmp/my-queue-plugin`

## 3. Policy packs

Policy packs are JSON documents validated by `schemas/policy.schema.json`.

Required fields:

- `policy_id`
- `policy_name`
- `policy_type`
- `rules`
- `default_outcome`
- `created_at`
- `version`

Policy compatibility boundary:

- Rule outcomes remain in the policy outcome set (`allow`, `warn`, `require_approval`, `deny`).
- Connector-specific scope fields (`connector_ids`, `providers`, `sources`, `directions`) are additive.

## 4. Simulation profiles

Simulation requests and stored simulation records follow `schemas/simulation.schema.json`.

Required fields:

- `simulation_id`
- `simulation_type`
- `status`
- `created_at`

Simulation compatibility boundary:

- Canonical event log writes stay outside simulation branch execution.
- Extension code can add `inputs`, `assumptions`, and `hypothetical_events` without mutating canonical state.

## Validation

Use these commands before proposing extension bundles:

- `make extension-contracts`
- `make adapters`
- `make connector-plugins`
- `make protocol-compat`
- `make public-api-compat`

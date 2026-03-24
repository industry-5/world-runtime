# Connector Execution Playbook (M18-M19)

## Goal

Operate inbound and outbound connector execution safely with retries, persistent idempotency, transport plugins, policy guardrails, approval-gated execution, and dead-letter replay handling.

## Runtime surfaces

- `core/connectors.py`
- App Server methods:
  - `connector.inbound.run`
  - `connector.outbound.run`
  - `connector.dead_letter.list`
  - `connector.dead_letter.replay`
  - `connector.policy_decision.list`
  - `connector.policy_decision.get`

## Operator checks

1. Run connector checks:

```bash
make connectors
make connector-plugins
```

M18 policy guardrail checks:

```bash
python3 -m pytest -q tests/test_connector_policy_guardrails.py
```

2. Run full baseline:

```bash
make test
make evals
make validate
make examples
make adapters
make integration-stacks
```

## Inbound run shape

Required fields:

- `session_id`
- `connector_id`
- `event_type_map`
- `external_event`

Optional fields:

- `retry.max_attempts` (default: 3)
- `idempotency_key`
- `fail_until_attempt` (test/smoke simulation)
- `policies` connector policy bundle (provider/source-aware)
- `approval_id` approval to resume execution after policy gate

## Outbound run shape

Required fields:

- `session_id`
- `connector_id`
- `action_type_map`
- `action`

Optional fields:

- `retry.max_attempts` (default: 3)
- `idempotency_key`
- `fail_until_attempt` (test/smoke simulation)
- `fail_permanently` (test/smoke simulation)
- `transport_plugin`:
  - `provider` (examples: `mock.webhook`, `mock.queue`)
  - `auth` provider-specific auth payload
  - `options` provider-specific transport options (for example endpoint/queue)
- `policies` connector policy bundle (provider-aware)
- `approval_id` approval to resume execution after policy gate

## Guardrail policy scope model

Connector policies can scope to:

- `scope.connector_ids`
- `scope.directions` (`inbound` or `outbound`)
- `scope.providers`
- `scope.sources`
- existing `scope.action_types` / `scope.event_types`

Rule evaluations include `evidence` with matched field/operator/expected/actual details.

## Approval-gated connector flow

1. First call with `policies` may return `status=awaiting_approval` and an `approval` payload.
2. Respond using `approval.respond` with attributable actor identity:
   - include `actor_id`, `actor_type`, and `capabilities`.
   - outbound approvals require `connector.outbound.approve`.
   - inbound approvals require `connector.inbound.approve`.
   - overrides require `approval.override`.
   - escalations require `approval.escalate`.
3. Re-run the connector method with the same payload and `approval_id`.
4. Execution starts only when approval status is `approved` or `overridden`.

## Connector policy decision records

- Guardrail outcomes are durably recorded with `decision_id`, policy report, provider/source context, and execution result (when executed).
- Decision payloads include attributable approval chain history when an approval exists.
- Query records with:
  - `connector.policy_decision.list`
  - `connector.policy_decision.get`

## Dead-letter handling

1. Query dead letters:
   - `connector.dead_letter.list`
2. Filter by `connector_id` or `direction`.
3. Recover by replaying corrected payloads with `connector.dead_letter.replay` and a new idempotency key.
4. Confirm replay metadata on the original dead-letter entry (`replay_status`, `replayed_at`, `replay_result`).

## Persistence behavior

- With in-memory event store, connector idempotency and dead letters are in-memory.
- With sqlite event store, connector idempotency + dead letters are persisted in sqlite and survive runtime restart.

## Expected outcomes

- duplicate idempotency key -> `status=duplicate`
- transient failure within retry budget -> `status=completed`
- exhausted retries or permanent failure -> `status=dead_lettered`
- dead-letter replay success -> `replay_status=succeeded`
- policy denied -> `status=rejected` (no connector transport execution)
- policy requires approval -> `status=awaiting_approval` until approved
- policy escalated -> `status=escalated` (no connector transport execution)

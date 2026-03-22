from core.connectors import (
    ConnectorRuntime,
    InboundConnectorConfig,
    OutboundConnectorConfig,
    PermanentConnectorError,
    RetryPolicy,
    TransientConnectorError,
)
from core.event_store import InMemoryEventStore


def test_inbound_retries_then_succeeds_and_is_idempotent():
    runtime = ConnectorRuntime(InMemoryEventStore())
    config = InboundConnectorConfig(
        connector_id="connector.ingress",
        event_type_map={"incident.external": "incident_internal"},
        retry=RetryPolicy(max_attempts=3),
    )

    attempts = {"count": 0}

    def _preprocessor(event, attempt):
        attempts["count"] += 1
        if attempt == 1:
            raise TransientConnectorError("temporary outage")
        return event

    first = runtime.run_inbound(
        config=config,
        external_event={
            "external_id": "evt-001",
            "event_type": "incident.external",
            "payload": {"k": "v"},
        },
        preprocessor=_preprocessor,
    )
    duplicate = runtime.run_inbound(
        config=config,
        external_event={
            "external_id": "evt-001",
            "event_type": "incident.external",
            "payload": {"k": "v"},
        },
    )

    assert first["status"] == "completed"
    assert first["attempts"] == 2
    assert attempts["count"] == 2
    assert duplicate["status"] == "duplicate"
    assert runtime.list_dead_letters() == []


def test_outbound_dead_letters_after_retry_exhaustion():
    runtime = ConnectorRuntime(InMemoryEventStore())
    config = OutboundConnectorConfig(
        connector_id="connector.egress",
        action_type_map={"reroute_shipment": "dispatch.reroute"},
        retry=RetryPolicy(max_attempts=2),
    )

    def _transport(_, __):
        raise TransientConnectorError("tms unavailable")

    result = runtime.run_outbound(
        config=config,
        action={"action_id": "act-001", "action_type": "reroute_shipment", "payload": {}},
        transport=_transport,
    )

    assert result["status"] == "dead_lettered"
    assert result["attempts"] == 2

    dead_letters = runtime.list_dead_letters(connector_id="connector.egress", direction="outbound")
    assert len(dead_letters) == 1
    assert dead_letters[0]["reason"] == "execution_failed"


def test_outbound_permanent_failure_dead_letters_without_retries():
    runtime = ConnectorRuntime(InMemoryEventStore())
    config = OutboundConnectorConfig(
        connector_id="connector.egress",
        action_type_map={"reroute_shipment": "dispatch.reroute"},
        retry=RetryPolicy(max_attempts=3),
    )

    attempts = {"count": 0}

    def _transport(_, __):
        attempts["count"] += 1
        raise PermanentConnectorError("invalid payload")

    result = runtime.run_outbound(
        config=config,
        action={"action_id": "act-002", "action_type": "reroute_shipment", "payload": {}},
        transport=_transport,
    )

    assert result["status"] == "dead_lettered"
    assert result["attempts"] == 1
    assert attempts["count"] == 1


def test_outbound_supports_transport_plugin_auth():
    runtime = ConnectorRuntime(InMemoryEventStore())
    config = OutboundConnectorConfig(
        connector_id="connector.egress",
        action_type_map={"reroute_shipment": "dispatch.reroute"},
        retry=RetryPolicy(max_attempts=2),
    )

    result = runtime.run_outbound(
        config=config,
        action={"action_id": "act-003", "action_type": "reroute_shipment", "payload": {}},
        transport_plugin={
            "provider": "mock.webhook",
            "auth": {"type": "api_key", "api_key": "key-123"},
            "options": {"endpoint": "https://example.test/hook"},
        },
    )

    assert result["status"] == "completed"
    assert result["transport_provider"] == "mock.webhook"
    assert result["transport_response"]["auth_type"] == "api_key"


def test_dead_letter_replay_updates_entry_and_succeeds():
    runtime = ConnectorRuntime(InMemoryEventStore())
    config = OutboundConnectorConfig(
        connector_id="connector.egress",
        action_type_map={"reroute_shipment": "dispatch.reroute"},
        retry=RetryPolicy(max_attempts=1),
    )

    def _transport(_, __):
        raise PermanentConnectorError("invalid payload")

    failed = runtime.run_outbound(
        config=config,
        action={"action_id": "act-004", "action_type": "reroute_shipment", "payload": {}},
        transport=_transport,
    )
    assert failed["status"] == "dead_lettered"

    replayed = runtime.replay_dead_letter(
        dead_letter_id=failed["dead_letter_id"],
        outbound_config=config,
        transport_plugin={
            "provider": "mock.queue",
            "auth": {"type": "access_key", "access_key_id": "id", "secret_access_key": "secret"},
            "options": {"queue": "queue.shipment.reroute"},
        },
        idempotency_key="act-004-replay",
    )

    assert replayed["replay_status"] == "succeeded"
    listed = runtime.list_dead_letters(connector_id="connector.egress", direction="outbound")
    assert listed[0]["replay_status"] == "succeeded"
    assert listed[0]["replay_result"]["status"] == "completed"

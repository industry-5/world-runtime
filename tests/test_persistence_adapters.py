from pathlib import Path

from core.deployment import DeploymentLoader
from core.connectors import (
    ConnectorRuntime,
    InboundConnectorConfig,
    OutboundConnectorConfig,
    RetryPolicy,
    TransientConnectorError,
)
from core.event_store import InMemoryEventStore
from core.migrations import apply_sqlite_migrations
from core.sqlite_event_store import SQLiteEventStore


REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = REPO_ROOT / "infra" / "migrations" / "persistence"


def test_sqlite_migrations_are_idempotent(tmp_path: Path):
    db_path = tmp_path / "migrations.sqlite"

    first = apply_sqlite_migrations(db_path, MIGRATIONS_DIR)
    second = apply_sqlite_migrations(db_path, MIGRATIONS_DIR)

    assert len(first["applied"]) >= 1
    assert second["applied"] == []
    assert len(second["skipped"]) >= 1


def test_sqlite_event_store_append_and_snapshot(tmp_path: Path):
    db_path = tmp_path / "store.sqlite"
    store = SQLiteEventStore(db_path, MIGRATIONS_DIR)

    first = store.append("stream.1", {"event_id": "evt.1", "event_type": "shipment_delayed", "payload": {}})
    second = store.append("stream.1", {"event_id": "evt.2", "event_type": "shipment_delayed", "payload": {}})

    assert first["offset"] == 0
    assert second["offset"] == 1
    assert second["sequence"] == 1

    snapshot = store.create_snapshot("world_state", 1, {"events_processed": 2})
    latest = store.latest_snapshot("world_state")

    assert snapshot["source_event_offset"] == 1
    assert latest["state"]["events_processed"] == 2
    assert len(store.read_all()) == 2


def test_in_memory_store_sequence_conflict_guard():
    store = InMemoryEventStore()
    store.append("stream.1", {"event_id": "evt.1", "event_type": "x", "payload": {}})

    raised = False
    try:
        store.append(
            "stream.1",
            {"event_id": "evt.2", "event_type": "x", "payload": {}},
            expected_sequence=0,
        )
    except ValueError:
        raised = True

    assert raised is True


def test_deployment_loader_builds_sqlite_store_for_profiles():
    loader = DeploymentLoader(REPO_ROOT)

    local_profile = loader.load_profile("local")
    local_runtime = loader.build_runtime(local_profile)

    dev_profile = loader.load_profile("dev")
    dev_runtime = loader.build_runtime(dev_profile)

    assert local_runtime["store"].__class__.__name__ == "SQLiteEventStore"
    assert dev_runtime["store"].__class__.__name__ == "SQLiteEventStore"


def test_connector_state_persists_in_sqlite_between_runtime_instances(tmp_path: Path):
    db_path = tmp_path / "connector-state.sqlite"
    store = SQLiteEventStore(db_path, MIGRATIONS_DIR)

    inbound_config = InboundConnectorConfig(
        connector_id="connector.ingress",
        event_type_map={"incident.external": "incident_internal"},
        retry=RetryPolicy(max_attempts=2),
    )
    outbound_config = OutboundConnectorConfig(
        connector_id="connector.egress",
        action_type_map={"reroute_shipment": "dispatch.reroute"},
        retry=RetryPolicy(max_attempts=2),
    )

    first_runtime = ConnectorRuntime(store)
    inbound_first = first_runtime.run_inbound(
        config=inbound_config,
        external_event={
            "external_id": "evt-100",
            "event_type": "incident.external",
            "payload": {"k": "v"},
        },
    )
    assert inbound_first["status"] == "completed"

    def _always_transient(_, __):
        raise TransientConnectorError("temporary outage")

    outbound_failed = first_runtime.run_outbound(
        config=outbound_config,
        action={"action_id": "act-900", "action_type": "reroute_shipment", "payload": {}},
        transport=_always_transient,
    )
    assert outbound_failed["status"] == "dead_lettered"

    second_runtime = ConnectorRuntime(store)
    inbound_duplicate = second_runtime.run_inbound(
        config=inbound_config,
        external_event={
            "external_id": "evt-100",
            "event_type": "incident.external",
            "payload": {"k": "v"},
        },
    )

    assert inbound_duplicate["status"] == "duplicate"
    dead_letters = second_runtime.list_dead_letters(connector_id="connector.egress", direction="outbound")
    assert len(dead_letters) == 1


def test_connector_policy_decisions_persist_in_sqlite_between_runtime_instances(tmp_path: Path):
    db_path = tmp_path / "connector-policy.sqlite"
    store = SQLiteEventStore(db_path, MIGRATIONS_DIR)

    runtime = ConnectorRuntime(store)
    runtime.record_policy_decision(
        decision_id="decision.connector.persist.0001",
        connector_id="connector.egress",
        direction="outbound",
        idempotency_key="outbound:connector.egress:act-901",
        final_outcome="deny",
        status="rejected",
        provider="mock.webhook",
        source="operator_console",
        policy_report={
            "proposal_id": "proposal.connector.outbound.outbound:connector.egress:act-901",
            "final_outcome": "deny",
            "requires_approval": False,
            "denied": True,
            "evaluations": [],
        },
    )

    second_runtime = ConnectorRuntime(store)
    listed = second_runtime.list_policy_decisions(connector_id="connector.egress", direction="outbound")

    assert len(listed) == 1
    assert listed[0]["decision_id"] == "decision.connector.persist.0001"
    assert listed[0]["final_outcome"] == "deny"
    assert listed[0]["status"] == "rejected"

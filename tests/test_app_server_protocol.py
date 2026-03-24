from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

from conftest import load_json
from core.app_server import WorldRuntimeAppServer
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = REPO_ROOT / "schemas"


def build_server(supply_network_scenario_dir, air_traffic_scenario_dir):
    store = InMemoryEventStore()
    supply_event = load_json(supply_network_scenario_dir / "events.json")[0]
    air_traffic_event = load_json(air_traffic_scenario_dir / "events.json")[0]
    store.append("shipment.88421", supply_event)
    store.append("flight.ual2187", air_traffic_event)

    replay = ReplayEngine(store, SimpleProjector)
    sim_engine = SimulationEngine(replay, SimpleProjector)
    reasoning = ReasoningAdapter(replay)
    policy = DeterministicPolicyEngine()
    return WorldRuntimeAppServer(
        reasoning_adapter=reasoning,
        simulation_engine=sim_engine,
        replay_engine=replay,
        policy_engine=policy,
    )


def validator_for(schema_name: str):
    schema = load_json(SCHEMAS_DIR / schema_name)
    resolver = RefResolver(base_uri=f"{SCHEMAS_DIR.as_uri()}/", referrer=schema)
    return Draft202012Validator(schema, resolver=resolver)


def test_wire_request_success_response_validates(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)

    request = {
        "wire_type": "request",
        "protocol_version": "1.0",
        "id": "req-1",
        "method": "session.create",
        "params": {},
    }
    response = server.handle_message(request)

    request_validator = validator_for("app_server.request.schema.json")
    response_validator = validator_for("app_server.response.schema.json")

    assert list(request_validator.iter_errors(request)) == []
    assert list(response_validator.iter_errors(response)) == []
    assert response["ok"] is True
    assert response["result"]["session_id"].startswith("session.")


def test_wire_request_incompatible_protocol_returns_error(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)

    request = {
        "protocol_version": "2.0",
        "id": "req-2",
        "method": "session.create",
        "params": {},
    }
    response = server.handle_message(request)

    assert response["ok"] is False
    assert response["error"]["code"] == "protocol_version_incompatible"


def test_wire_request_validation_error_returns_invalid_request(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)

    bad_request = {
        "protocol_version": "1.0",
        "id": "req-3",
        "params": {},
    }
    response = server.handle_message(bad_request)

    assert response["ok"] is False
    assert response["error"]["code"] == "invalid_request"


def test_legacy_handle_request_remains_supported(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)

    legacy = server.handle_request("session.create")
    assert legacy["ok"] is True
    assert legacy["result"]["session_id"].startswith("session.")


def test_notifications_include_protocol_fields(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]

    server.task_submit(
        session_id=session_id,
        method="reasoning.query",
        params={
            "projection_name": "world_state",
            "query": "What is the delay status for shipment.88421?",
        },
    )

    events = server.task_events_subscribe(session_id=session_id)["events"]
    assert len(events) >= 1

    notification_validator = validator_for("app_server.notification.schema.json")
    first_notification = {
        "wire_type": events[0]["wire_type"],
        "protocol_version": events[0]["protocol_version"],
        "method": events[0]["method"],
        "params": events[0]["params"],
    }
    assert list(notification_validator.iter_errors(first_notification)) == []

from core.app_server import WorldRuntimeAppServer
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine
from conftest import load_json


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


def test_outbound_guardrail_denies_before_transport(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]
    policy = {
        "policy_id": "policy.connector.provider-blocklist",
        "policy_name": "blocklisted_provider_denied",
        "default_outcome": "allow",
        "scope": {"directions": ["outbound"], "providers": ["mock.webhook"]},
        "rules": [
            {
                "rule_id": "rule.connector.provider.block",
                "rule_name": "Deny blocked outbound provider",
                "condition": {
                    "field": "connector_context.provider",
                    "operator": "equals",
                    "value": "mock.webhook",
                },
                "outcome": "deny",
                "message_template": "Provider is not trusted for outbound effects.",
            }
        ],
    }

    result = server.handle_request(
        "connector.outbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.egress",
            "action_type_map": {"reroute_shipment": "dispatch.reroute"},
            "action": {
                "action_id": "act-guardrail-001",
                "action_type": "reroute_shipment",
                "payload": {"shipment_id": "shipment.88421"},
                "source": "control_plane",
            },
            "transport_plugin": {
                "provider": "mock.webhook",
                "auth": {"type": "api_key", "api_key": "key-123"},
                "options": {"endpoint": "https://example.test/hook"},
            },
            "policies": [policy],
        },
    )

    assert result["ok"] is True
    assert result["result"]["status"] == "rejected"
    assert result["result"]["policy_report"]["final_outcome"] == "deny"

    decisions = server.handle_request(
        "connector.policy_decision.list",
        {"session_id": session_id, "direction": "outbound"},
    )
    assert decisions["ok"] is True
    assert decisions["result"]["decisions"][0]["status"] == "rejected"


def test_outbound_guardrail_approval_gate_blocks_then_executes(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]
    policy = {
        "policy_id": "policy.connector.provider-approval",
        "policy_name": "provider_requires_approval",
        "default_outcome": "allow",
        "scope": {"directions": ["outbound"], "providers": ["mock.queue"]},
        "rules": [
            {
                "rule_id": "rule.connector.provider.approval",
                "rule_name": "Approval required for queue provider",
                "condition": {
                    "field": "connector_context.provider",
                    "operator": "equals",
                    "value": "mock.queue",
                },
                "outcome": "require_approval",
                "message_template": "Queue delivery needs operator approval.",
            }
        ],
    }

    first = server.handle_request(
        "connector.outbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.egress",
            "action_type_map": {"reroute_shipment": "dispatch.reroute"},
            "action": {
                "action_id": "act-guardrail-002",
                "action_type": "reroute_shipment",
                "payload": {"shipment_id": "shipment.88421"},
            },
            "transport_plugin": {
                "provider": "mock.queue",
                "auth": {
                    "type": "access_key",
                    "access_key_id": "id",
                    "secret_access_key": "secret",
                },
                "options": {"queue": "queue.shipment.reroute"},
            },
            "policies": [policy],
        },
    )

    assert first["ok"] is True
    assert first["result"]["status"] == "awaiting_approval"
    approval_id = first["result"]["approval"]["approval_id"]

    approved = server.handle_request(
        "approval.respond",
        {
            "approval_id": approval_id,
            "decision": "approved",
            "comment": "approved by test",
            "actor": {
                "actor_id": "human.connector-operator-01",
                "actor_type": "human",
                "roles": ["operator"],
                "capabilities": ["approval.respond", "connector.outbound.approve"],
            },
        },
    )
    assert approved["ok"] is True
    assert approved["result"]["status"] == "approved"

    second = server.handle_request(
        "connector.outbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.egress",
            "action_type_map": {"reroute_shipment": "dispatch.reroute"},
            "action": {
                "action_id": "act-guardrail-002",
                "action_type": "reroute_shipment",
                "payload": {"shipment_id": "shipment.88421"},
            },
            "transport_plugin": {
                "provider": "mock.queue",
                "auth": {
                    "type": "access_key",
                    "access_key_id": "id",
                    "secret_access_key": "secret",
                },
                "options": {"queue": "queue.shipment.reroute"},
            },
            "policies": [policy],
            "approval_id": approval_id,
        },
    )

    assert second["ok"] is True
    assert second["result"]["status"] == "completed"
    assert second["result"]["approval"]["status"] == "approved"

    decision = server.handle_request(
        "connector.policy_decision.get",
        {"session_id": session_id, "decision_id": second["result"]["decision_id"]},
    )
    assert decision["ok"] is True
    assert decision["result"]["execution_result"]["status"] == "completed"


def test_outbound_override_requires_override_capability(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]
    policy = {
        "policy_id": "policy.connector.provider-approval",
        "policy_name": "provider_requires_approval",
        "default_outcome": "allow",
        "scope": {"directions": ["outbound"], "providers": ["mock.queue"]},
        "rules": [
            {
                "rule_id": "rule.connector.provider.approval",
                "rule_name": "Approval required for queue provider",
                "condition": {
                    "field": "connector_context.provider",
                    "operator": "equals",
                    "value": "mock.queue",
                },
                "outcome": "require_approval",
            }
        ],
    }

    first = server.handle_request(
        "connector.outbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.egress",
            "action_type_map": {"reroute_shipment": "dispatch.reroute"},
            "action": {
                "action_id": "act-guardrail-003",
                "action_type": "reroute_shipment",
                "payload": {"shipment_id": "shipment.88421"},
            },
            "transport_plugin": {
                "provider": "mock.queue",
                "auth": {"type": "access_key", "access_key_id": "id", "secret_access_key": "secret"},
                "options": {"queue": "queue.shipment.reroute"},
            },
            "policies": [policy],
        },
    )
    assert first["ok"] is True
    approval_id = first["result"]["approval"]["approval_id"]

    denied_override = server.handle_request(
        "approval.respond",
        {
            "approval_id": approval_id,
            "decision": "overridden",
            "actor": {
                "actor_id": "human.operator-01",
                "actor_type": "human",
                "roles": ["operator"],
                "capabilities": ["approval.respond", "connector.outbound.approve"],
            },
        },
    )
    assert denied_override["ok"] is False
    assert "required approval capability" in denied_override["error"]

    allowed_override = server.handle_request(
        "approval.respond",
        {
            "approval_id": approval_id,
            "decision": "overridden",
            "actor": {
                "actor_id": "human.admin-01",
                "actor_type": "human",
                "roles": ["admin"],
                "capabilities": ["approval.respond", "connector.outbound.approve", "approval.override"],
            },
        },
    )
    assert allowed_override["ok"] is True
    assert allowed_override["result"]["status"] == "overridden"

    resumed = server.handle_request(
        "connector.outbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.egress",
            "action_type_map": {"reroute_shipment": "dispatch.reroute"},
            "action": {
                "action_id": "act-guardrail-003",
                "action_type": "reroute_shipment",
                "payload": {"shipment_id": "shipment.88421"},
            },
            "transport_plugin": {
                "provider": "mock.queue",
                "auth": {"type": "access_key", "access_key_id": "id", "secret_access_key": "secret"},
                "options": {"queue": "queue.shipment.reroute"},
            },
            "policies": [policy],
            "approval_id": approval_id,
        },
    )
    assert resumed["ok"] is True
    assert resumed["result"]["status"] == "completed"
    assert resumed["result"]["approval"]["status"] == "overridden"


def test_inbound_guardrail_rejects_untrusted_source_with_evidence(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]
    policy = {
        "policy_id": "policy.connector.source-restriction",
        "policy_name": "inbound_source_restriction",
        "default_outcome": "allow",
        "scope": {"directions": ["inbound"], "sources": ["third_party_feed"]},
        "rules": [
            {
                "rule_id": "rule.connector.source.reject",
                "rule_name": "Reject untrusted source",
                "condition": {
                    "field": "connector_context.source",
                    "operator": "equals",
                    "value": "third_party_feed",
                },
                "outcome": "deny",
                "message_template": "Inbound source is not trusted.",
            }
        ],
    }

    response = server.handle_request(
        "connector.inbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.ingress",
            "event_type_map": {"shipment.delay": "shipment_delayed"},
            "external_event": {
                "event_id": "evt-guardrail-001",
                "event_type": "shipment.delay",
                "payload": {"shipment_id": "shipment.88421", "delay_hours": 3},
                "source": "third_party_feed",
            },
            "policies": [policy],
        },
    )

    assert response["ok"] is True
    assert response["result"]["status"] == "rejected"
    evidence = response["result"]["policy_report"]["evaluations"][0]["evidence"]
    assert evidence["actual"] == "third_party_feed"

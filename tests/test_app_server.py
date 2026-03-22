from core.app_server import WorldRuntimeAppServer
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine
from conftest import load_json
import json


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
    server = WorldRuntimeAppServer(
        reasoning_adapter=reasoning,
        simulation_engine=sim_engine,
        replay_engine=replay,
        policy_engine=policy,
    )
    return server


def test_session_lifecycle(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)

    create = server.handle_request("session.create")
    assert create["ok"] is True
    session_id = create["result"]["session_id"]

    resume = server.handle_request("session.resume", {"session_id": session_id})
    assert resume["ok"] is True
    assert resume["result"]["status"] == "open"

    close = server.handle_request("session.close", {"session_id": session_id})
    assert close["ok"] is True
    assert close["result"]["status"] == "closed"


def test_task_submit_and_event_stream_reasoning(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]

    response = server.handle_request(
        "task.submit",
        {
            "session_id": session_id,
            "method": "reasoning.query",
            "params": {
                "projection_name": "world_state",
                "query": "What is the delay status for shipment.88421?",
            },
        },
    )

    assert response["ok"] is True
    task_id = response["result"]["task_id"]
    assert response["result"]["status"] == "completed"

    status = server.handle_request("task.status", {"task_id": task_id})
    assert status["ok"] is True
    assert status["result"]["result"]["query_type"] == "shipment_delay"

    events = server.handle_request(
        "task.events.subscribe",
        {"session_id": session_id, "since": 0},
    )
    event_types = [evt["type"] for evt in events["result"]["events"]]
    assert "task.started" in event_types
    assert "task.progress" in event_types
    assert "task.completed" in event_types


def test_approval_flow_end_to_end(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]

    proposal = load_json(supply_network_scenario_dir / "proposal.json")
    policy = {
        "policy_id": "policy.approval",
        "policy_name": "approval_required_policy",
        "default_outcome": "allow",
        "rules": [
            {
                "rule_id": "rule.approval",
                "rule_name": "requires approval",
                "condition": {
                    "field": "proposed_action.action_type",
                    "operator": "equals",
                    "value": proposal["proposed_action"]["action_type"],
                },
                "outcome": "require_approval",
            }
        ],
    }

    task = server.handle_request(
        "task.submit",
        {
            "session_id": session_id,
            "method": "proposal.submit",
            "params": {
                "proposal": proposal,
                "policies": [policy],
            },
        },
    )
    assert task["ok"] is True
    task_result = task["result"]["result"]
    assert task_result["policy_report"]["requires_approval"] is True
    assert task_result["approval_id"] is not None

    approval_id = task_result["approval_id"]
    approval = server.handle_request(
        "approval.respond",
        {
            "approval_id": approval_id,
            "decision": "approved",
            "comment": "approved in test",
            "actor": {
                "actor_id": "human.ops-manager-01",
                "actor_type": "human",
                "roles": ["operator"],
                "capabilities": ["approval.respond", "proposal.approve"],
            },
        },
    )
    assert approval["ok"] is True
    assert approval["result"]["status"] == "approved"
    assert len(approval["result"]["approval_chain"]) == 1


def test_approval_enforces_actor_capabilities_and_history(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]

    task = server.task_submit(
        session_id=session_id,
        method="proposal.submit",
        params={
            "proposal": load_json(supply_network_scenario_dir / "proposal.json"),
            "policies": [
                {
                    "policy_id": "policy.approval",
                    "policy_name": "approval_required_policy",
                    "default_outcome": "allow",
                    "rules": [
                        {
                            "rule_id": "rule.approval",
                            "rule_name": "requires approval",
                            "condition": {
                                "field": "proposed_action.action_type",
                                "operator": "equals",
                                "value": "reroute_shipment",
                            },
                            "outcome": "require_approval",
                        }
                    ],
                }
            ],
        },
    )
    approval_id = task["result"]["approval_id"]

    unauthorized = server.handle_request(
        "approval.respond",
        {
            "approval_id": approval_id,
            "decision": "approved",
            "actor": {
                "actor_id": "human.viewer-01",
                "actor_type": "human",
                "roles": ["viewer"],
                "capabilities": ["approval.respond"],
            },
        },
    )
    assert unauthorized["ok"] is False
    assert "required approval capability" in unauthorized["error"]

    authorized = server.handle_request(
        "approval.respond",
        {
            "approval_id": approval_id,
            "decision": "approved",
            "actor": {
                "actor_id": "human.ops-manager-01",
                "actor_type": "human",
                "roles": ["operator"],
                "capabilities": ["approval.respond", "proposal.approve"],
            },
        },
    )
    assert authorized["ok"] is True

    history = server.handle_request(
        "approval.history",
        {"session_id": session_id, "approval_id": approval_id},
    )
    assert history["ok"] is True
    assert history["result"]["approval_chain"][0]["actor"]["actor_id"] == "human.ops-manager-01"


def test_approval_chain_rehydrates_from_event_store(supply_network_scenario_dir, air_traffic_scenario_dir):
    store = InMemoryEventStore()
    supply_event = load_json(supply_network_scenario_dir / "events.json")[0]
    air_traffic_event = load_json(air_traffic_scenario_dir / "events.json")[0]
    store.append("shipment.88421", supply_event)
    store.append("flight.ual2187", air_traffic_event)

    replay_one = ReplayEngine(store, SimpleProjector)
    sim_one = SimulationEngine(replay_one, SimpleProjector)
    server_one = WorldRuntimeAppServer(
        reasoning_adapter=ReasoningAdapter(replay_one),
        simulation_engine=sim_one,
        replay_engine=replay_one,
        policy_engine=DeterministicPolicyEngine(),
    )
    session_one = server_one.session_create()["session_id"]

    approval = server_one.approval_request(
        session_id=session_one,
        task_id=server_one._create_virtual_task_for_proposal(session_one, {"proposal_id": "proposal.1"}),
        reason="policy requires approval",
        actor_requirements={"required_capabilities": ["approval.respond", "proposal.approve"]},
    )
    server_one.approval_respond(
        approval_id=approval["approval_id"],
        decision="approved",
        actor={
            "actor_id": "human.ops-manager-01",
            "actor_type": "human",
            "roles": ["operator"],
            "capabilities": ["approval.respond", "proposal.approve"],
        },
    )

    replay_two = ReplayEngine(store, SimpleProjector)
    sim_two = SimulationEngine(replay_two, SimpleProjector)
    server_two = WorldRuntimeAppServer(
        reasoning_adapter=ReasoningAdapter(replay_two),
        simulation_engine=sim_two,
        replay_engine=replay_two,
        policy_engine=DeterministicPolicyEngine(),
    )
    session_two = server_two.session_create()["session_id"]
    restored = server_two.approval_get(session_id=session_two, approval_id=approval["approval_id"])

    assert restored["status"] == "approved"
    assert restored["approval_chain"][0]["actor"]["actor_id"] == "human.ops-manager-01"


def test_eval_invocation_and_report_lookup(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]

    listing = server.handle_request("eval.list")
    assert listing["ok"] is True
    assert len(listing["result"]["evals"]) >= 3

    run = server.handle_request(
        "eval.run",
        {"session_id": session_id, "eval_id": "eval.smoke.policy"},
    )
    assert run["ok"] is True
    assert run["result"]["status"] == "passed"

    report = server.handle_request("eval.report", {"report_id": run["result"]["report_id"]})
    assert report["ok"] is True
    assert report["result"]["eval_id"] == "eval.smoke.policy"


def test_simulation_task_executes_and_streams_events(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]

    run = server.handle_request(
        "task.submit",
        {
            "session_id": session_id,
            "method": "simulation.run",
            "params": {
                "simulation_id": "sim.appserver.0001",
                "projection_name": "world_state",
                "hypothetical_events": [
                    {
                        "event_type": "shipment_delayed",
                        "payload": {
                            "shipment_id": "shipment.88421",
                            "delay_hours": 1,
                            "cause": "simulated_reroute",
                        },
                    }
                ],
            },
        },
    )

    assert run["ok"] is True
    assert run["result"]["result"]["status"] == "completed"
    assert run["result"]["result"]["simulated_state"]["shipments"]["shipment.88421"]["delay_hours"] == 1


def test_telemetry_and_diagnostics_methods_are_available(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]
    server.task_submit(
        session_id=session_id,
        method="reasoning.query",
        params={
            "projection_name": "world_state",
            "query": "Summarize current world state",
        },
    )

    summary = server.handle_request("telemetry.summary")
    assert summary["ok"] is True
    assert summary["result"]["totals"]["events"] >= 1
    assert summary["result"]["totals"]["traces"] >= 1

    events = server.handle_request("telemetry.events", {"component": "app_server", "limit": 5})
    assert events["ok"] is True
    assert len(events["result"]["events"]) >= 1

    traces = server.handle_request("trace.list", {"limit": 5})
    assert traces["ok"] is True
    assert len(traces["result"]["traces"]) >= 1

    dashboard = server.handle_request("diagnostics.dashboard")
    assert dashboard["ok"] is True
    assert "cards" in dashboard["result"]


def test_connector_methods_support_retries_idempotency_and_dead_letters(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]

    inbound = server.handle_request(
        "connector.inbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.ingress",
            "event_type_map": {"shipment.delay": "shipment_delayed"},
            "external_event": {
                "event_id": "evt-100",
                "event_type": "shipment.delay",
                "payload": {"shipment_id": "shipment.88421", "delay_hours": 3},
            },
            "retry": {"max_attempts": 3},
            "fail_until_attempt": 1,
        },
    )
    assert inbound["ok"] is True
    assert inbound["result"]["status"] == "completed"
    assert inbound["result"]["attempts"] == 2

    inbound_duplicate = server.handle_request(
        "connector.inbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.ingress",
            "event_type_map": {"shipment.delay": "shipment_delayed"},
            "external_event": {
                "event_id": "evt-100",
                "event_type": "shipment.delay",
                "payload": {"shipment_id": "shipment.88421", "delay_hours": 3},
            },
        },
    )
    assert inbound_duplicate["ok"] is True
    assert inbound_duplicate["result"]["status"] == "duplicate"

    outbound_failed = server.handle_request(
        "connector.outbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.egress",
            "action_type_map": {"reroute_shipment": "dispatch.reroute"},
            "action": {
                "action_id": "act-700",
                "action_type": "reroute_shipment",
                "payload": {"shipment_id": "shipment.88421"},
            },
            "retry": {"max_attempts": 2},
            "fail_permanently": True,
        },
    )
    assert outbound_failed["ok"] is True
    assert outbound_failed["result"]["status"] == "dead_lettered"

    dead_letters = server.handle_request(
        "connector.dead_letter.list",
        {
            "session_id": session_id,
            "direction": "outbound",
        },
    )
    assert dead_letters["ok"] is True
    assert len(dead_letters["result"]["dead_letters"]) == 1


def test_connector_dead_letter_replay_and_transport_plugin(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]

    failed = server.handle_request(
        "connector.outbound.run",
        {
            "session_id": session_id,
            "connector_id": "connector.integration.egress",
            "action_type_map": {"reroute_shipment": "dispatch.reroute"},
            "action": {
                "action_id": "act-701",
                "action_type": "reroute_shipment",
                "payload": {"shipment_id": "shipment.88421"},
            },
            "retry": {"max_attempts": 1},
            "fail_permanently": True,
        },
    )
    assert failed["ok"] is True
    assert failed["result"]["status"] == "dead_lettered"

    replay = server.handle_request(
        "connector.dead_letter.replay",
        {
            "session_id": session_id,
            "dead_letter_id": failed["result"]["dead_letter_id"],
            "action_type_map": {"reroute_shipment": "dispatch.reroute"},
            "idempotency_key": "act-701-replay",
            "transport_plugin": {
                "provider": "mock.webhook",
                "auth": {"type": "bearer", "token": "abc"},
                "options": {"endpoint": "https://example.test/connectors"},
            },
        },
    )
    assert replay["ok"] is True
    assert replay["result"]["replay_status"] == "succeeded"
    assert replay["result"]["result"]["status"] == "completed"
    assert replay["result"]["result"]["transport_provider"] == "mock.webhook"

    listed = server.handle_request(
        "connector.dead_letter.list",
        {
            "session_id": session_id,
            "direction": "outbound",
        },
    )
    assert listed["ok"] is True
    assert listed["result"]["dead_letters"][0]["replay_status"] == "succeeded"


def test_audit_export_is_redacted_and_reproducible(supply_network_scenario_dir, air_traffic_scenario_dir):
    server = build_server(supply_network_scenario_dir, air_traffic_scenario_dir)
    session_id = server.session_create()["session_id"]

    proposal = load_json(supply_network_scenario_dir / "proposal.json")
    proposal["proposed_action"]["parameters"]["api_key"] = "secret-token-123"
    proposal.setdefault("supporting_evidence", [])
    proposal["supporting_evidence"].append(
        {
            "evidence_type": "config",
            "ref_id": "cfg.secret.0001",
            "summary": "Captured connector token state.",
            "attributes": {"authorization": "Bearer secret-token-123"},
        }
    )
    policy = {
        "policy_id": "policy.approval",
        "policy_name": "approval_required_policy",
        "default_outcome": "allow",
        "rules": [
            {
                "rule_id": "rule.approval",
                "rule_name": "requires approval",
                "condition": {
                    "field": "proposed_action.action_type",
                    "operator": "equals",
                    "value": proposal["proposed_action"]["action_type"],
                },
                "outcome": "require_approval",
            }
        ],
    }

    submitted = server.proposal_submit(session_id=session_id, proposal=proposal, policies=[policy])
    approval_id = submitted["approval"]["approval_id"]
    server.approval_respond(
        approval_id=approval_id,
        decision="approved",
        actor={
            "actor_id": "human.ops-manager-01",
            "actor_type": "human",
            "roles": ["operator"],
            "capabilities": ["approval.respond", "proposal.approve"],
        },
    )
    decision = server.decision_create(
        session_id=session_id,
        proposal=proposal,
        policy_report=submitted["policy_report"],
        approval_id=approval_id,
    )

    first = server.audit_export(session_id=session_id, decision_id=decision["decision_id"])
    second = server.audit_export(session_id=session_id, decision_id=decision["decision_id"])

    assert first["fingerprint"] == second["fingerprint"]
    assert first["diagnostics"]["major_decisions"][0]["end_to_end_traceable"] is True
    assert first["redaction"]["redacted"] is True

    serialized = json.dumps(first, sort_keys=True)
    assert "secret-token-123" not in serialized
    assert "[REDACTED]" in serialized

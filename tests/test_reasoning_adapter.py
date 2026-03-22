from core.event_store import InMemoryEventStore
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from conftest import load_json


def build_reasoning_adapter(supply_network_scenario_dir, air_traffic_scenario_dir):
    store = InMemoryEventStore()

    supply_event = load_json(supply_network_scenario_dir / "events.json")[0]
    air_traffic_event = load_json(air_traffic_scenario_dir / "events.json")[0]

    store.append("shipment.88421", supply_event)
    store.append("flight.ual2187", air_traffic_event)

    replay = ReplayEngine(store, SimpleProjector)
    adapter = ReasoningAdapter(replay)
    return store, replay, adapter


def test_context_builder_exposes_state_and_recent_events(supply_network_scenario_dir, air_traffic_scenario_dir):
    _, _, adapter = build_reasoning_adapter(
        supply_network_scenario_dir,
        air_traffic_scenario_dir,
    )

    context = adapter.build_context("world_state", max_events=1)

    assert context["projection_name"] == "world_state"
    assert context["event_count"] == 2
    assert len(context["recent_events"]) == 1
    assert context["state"]["events_processed"] == 2


def test_shipment_delay_query_returns_evidence_citations(supply_network_scenario_dir, air_traffic_scenario_dir):
    _, _, adapter = build_reasoning_adapter(
        supply_network_scenario_dir,
        air_traffic_scenario_dir,
    )

    answer = adapter.answer_query(
        projection_name="world_state",
        query="What is the delay status for shipment.88421?",
    )

    assert answer.query_type == "shipment_delay"
    assert "shipment.88421" in answer.answer_text
    assert len(answer.evidence) >= 1
    assert any(item.ref_id == "evt.shipment-delay.0001" for item in answer.evidence)


def test_reasoning_queries_do_not_mutate_canonical_event_store(supply_network_scenario_dir, air_traffic_scenario_dir):
    store, _, adapter = build_reasoning_adapter(
        supply_network_scenario_dir,
        air_traffic_scenario_dir,
    )

    before = store.last_offset()
    adapter.answer_query("world_state", "What is delayed?")
    adapter.answer_query("world_state", "Summarize current world state")
    after = store.last_offset()

    assert before == after == 1


def test_generated_proposal_is_non_mutating_and_policy_ready(supply_network_scenario_dir, air_traffic_scenario_dir):
    store, _, adapter = build_reasoning_adapter(
        supply_network_scenario_dir,
        air_traffic_scenario_dir,
    )

    before = store.last_offset()
    proposal = adapter.generate_proposal(
        projection_name="world_state",
        instruction="Propose an action for shipment.88421 delay",
    )
    after = store.last_offset()

    assert before == after == 1
    assert proposal["status"] == "draft"
    assert proposal["proposed_action"]["action_type"] == "reroute_shipment"
    assert proposal["proposed_action"]["parameters"]["shipment_id"] == "shipment.88421"
    assert len(proposal["supporting_evidence"]) >= 1


def test_retrieve_events_filters_by_entity(supply_network_scenario_dir, air_traffic_scenario_dir):
    _, _, adapter = build_reasoning_adapter(
        supply_network_scenario_dir,
        air_traffic_scenario_dir,
    )

    shipment_events = adapter.retrieve_events(entity_id="shipment.88421")
    weather_events = adapter.retrieve_events(event_type="weather_alert_issued")

    assert any(e["event_id"] == "evt.shipment-delay.0001" for e in shipment_events)
    assert len(weather_events) == 1
    assert weather_events[0]["event_id"] == "evt.air-traffic.weather-alert.0001"

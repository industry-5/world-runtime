from core.projector import SimpleProjector
from conftest import load_json


def test_projection_handles_supply_delay(supply_network_scenario_dir):
    events = load_json(supply_network_scenario_dir / "events.json")
    projector = SimpleProjector()

    state = projector.replay(events)

    assert "shipment.88421" in state["shipments"]
    assert state["shipments"]["shipment.88421"]["cause"] == "weather"


def test_projection_ignores_unmodeled_air_traffic_events_without_failing(air_traffic_scenario_dir):
    events = load_json(air_traffic_scenario_dir / "events.json")
    projector = SimpleProjector()

    state = projector.replay(events)

    assert state["events_processed"] == len(events)
    assert state["last_event_id"] == events[-1]["event_id"]

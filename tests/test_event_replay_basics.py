from core.event_store import InMemoryEventStore
from core.projector import SimpleProjector
from conftest import load_json


def test_event_store_append_and_read(top_level_example_paths):
    event = load_json(top_level_example_paths["event"])
    store = InMemoryEventStore()

    stream_id = event["stream_id"]
    store.append(stream_id, event)

    read_back = store.read_stream(stream_id)
    assert len(read_back) == 1
    assert read_back[0]["event_id"] == event["event_id"]


def test_event_store_all_events_sorted(top_level_example_paths):
    event = load_json(top_level_example_paths["event"])
    store = InMemoryEventStore()
    store.append(event["stream_id"], event)

    events = store.all_events()
    assert len(events) == 1
    assert events[0]["event_id"] == event["event_id"]


def test_projector_replays_supply_event(supply_network_scenario_dir):
    events = load_json(supply_network_scenario_dir / "events.json")

    projector = SimpleProjector()
    state = projector.replay(events)

    assert state["events_processed"] == 1
    assert state["last_event_id"] == "evt.shipment-delay.0001"
    assert state["shipments"]["shipment.88421"]["delay_hours"] == 18

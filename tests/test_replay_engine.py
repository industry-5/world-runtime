from copy import deepcopy

from core.event_store import InMemoryEventStore
from core.projector import SimpleProjector
from core.replay_engine import ReplayEngine
from conftest import load_json


def test_event_store_assigns_offsets_and_stream_sequence(top_level_example_paths):
    store = InMemoryEventStore()
    event = load_json(top_level_example_paths["event"])
    event.pop("sequence", None)

    first = store.append("shipment.88421", event)
    second = store.append("shipment.88421", event)

    assert first["offset"] == 0
    assert second["offset"] == 1
    assert first["sequence"] == 0
    assert second["sequence"] == 1


def test_replay_rebuild_is_deterministic(supply_network_scenario_dir, air_traffic_scenario_dir):
    store = InMemoryEventStore()

    supply_event = load_json(supply_network_scenario_dir / "events.json")[0]
    air_traffic_event = load_json(air_traffic_scenario_dir / "events.json")[0]

    store.append("shipment.88421", supply_event)
    store.append("flight.ual2187", air_traffic_event)

    engine = ReplayEngine(store, SimpleProjector)

    first = engine.rebuild("world_state", use_snapshot=False)
    second = engine.rebuild("world_state", use_snapshot=False)

    assert first.state == second.state
    assert first.source_event_offset == second.source_event_offset == 1
    assert first.events_processed == second.events_processed == 2


def test_replay_supports_snapshots(supply_network_scenario_dir, air_traffic_scenario_dir):
    store = InMemoryEventStore()

    supply_event = load_json(supply_network_scenario_dir / "events.json")[0]
    air_traffic_event = load_json(air_traffic_scenario_dir / "events.json")[0]

    another_supply_event = deepcopy(supply_event)
    another_supply_event["event_id"] = "evt.shipment-delay.0002"
    another_supply_event["payload"]["delay_hours"] = 24
    another_supply_event["payload"]["cause"] = "port_congestion"

    store.append("shipment.88421", supply_event)
    store.append("flight.ual2187", air_traffic_event)
    store.append("shipment.88421", another_supply_event)

    engine = ReplayEngine(store, SimpleProjector)

    partial = engine.rebuild("world_state", up_to_offset=1, use_snapshot=False)
    engine.save_snapshot(
        projection_name="world_state",
        source_event_offset=partial.source_event_offset,
        state=partial.state,
    )

    from_snapshot = engine.rebuild("world_state", use_snapshot=True)
    full = engine.rebuild("world_state", use_snapshot=False)

    assert from_snapshot.from_snapshot is True
    assert from_snapshot.snapshot_offset == 1
    assert from_snapshot.state == full.state
    assert from_snapshot.source_event_offset == full.source_event_offset == 2


def test_rebuild_up_to_offset_returns_partial_state(supply_network_scenario_dir):
    store = InMemoryEventStore()
    event = load_json(supply_network_scenario_dir / "events.json")[0]

    event2 = deepcopy(event)
    event2["event_id"] = "evt.shipment-delay.0002"
    event2["payload"]["delay_hours"] = 3

    store.append("shipment.88421", event)
    store.append("shipment.88421", event2)

    engine = ReplayEngine(store, SimpleProjector)

    partial = engine.rebuild("world_state", up_to_offset=0)
    full = engine.rebuild("world_state")

    assert partial.source_event_offset == 0
    assert full.source_event_offset == 1
    assert partial.state["shipments"]["shipment.88421"]["delay_hours"] == 18
    assert full.state["shipments"]["shipment.88421"]["delay_hours"] == 3

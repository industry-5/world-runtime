from copy import deepcopy

from core.event_store import InMemoryEventStore
from core.projector import SimpleProjector
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine
from conftest import load_json


def build_sim_engine(supply_network_scenario_dir):
    store = InMemoryEventStore()
    base_event = load_json(supply_network_scenario_dir / "events.json")[0]
    store.append("shipment.88421", base_event)

    replay = ReplayEngine(store, SimpleProjector)
    sim_engine = SimulationEngine(replay, SimpleProjector)
    return store, replay, sim_engine


def test_simulation_branch_isolated_from_canonical_state(supply_network_scenario_dir):
    store, replay, sim_engine = build_sim_engine(supply_network_scenario_dir)

    sim_engine.create_branch(
        simulation_id="sim.test.0001",
        projection_name="world_state",
        scenario_name="Reroute scenario",
    )

    hypothetical = {
        "event_id": "evt.simulated.reroute.0001",
        "event_type": "shipment_delayed",
        "payload": {
            "shipment_id": "shipment.88421",
            "delay_hours": 2,
            "cause": "reroute_success"
        }
    }
    sim_engine.apply_hypothetical_event("sim.test.0001", hypothetical)
    result = sim_engine.run("sim.test.0001")

    canonical = replay.rebuild("world_state", use_snapshot=False)

    assert result.simulated_state["shipments"]["shipment.88421"]["delay_hours"] == 2
    assert canonical.state["shipments"]["shipment.88421"]["delay_hours"] == 18
    assert store.last_offset() == 0


def test_simulation_lineage_is_preserved(supply_network_scenario_dir):
    _, _, sim_engine = build_sim_engine(supply_network_scenario_dir)

    parent = sim_engine.create_branch(
        simulation_id="sim.parent.0001",
        projection_name="world_state",
    )
    child = sim_engine.create_branch(
        simulation_id="sim.child.0001",
        projection_name="world_state",
        parent_simulation_id="sim.parent.0001",
    )

    assert parent.parent_simulation_id is None
    assert child.parent_simulation_id == "sim.parent.0001"
    assert child.base_event_offset == parent.base_event_offset


def test_simulation_generates_state_diff(supply_network_scenario_dir):
    _, _, sim_engine = build_sim_engine(supply_network_scenario_dir)

    sim_engine.create_branch(
        simulation_id="sim.diff.0001",
        projection_name="world_state",
    )

    hypothetical = {
        "event_type": "shipment_delayed",
        "payload": {
            "shipment_id": "shipment.88421",
            "delay_hours": 6,
            "cause": "minor_disruption"
        }
    }
    sim_engine.apply_hypothetical_event("sim.diff.0001", hypothetical)
    result = sim_engine.run("sim.diff.0001")

    assert result.status == "completed"
    assert result.hypothetical_events_applied == 1
    assert "shipments.shipment.88421.delay_hours" in result.state_diff
    assert "shipments.shipment.88421.cause" in result.state_diff
    assert result.comparison_summary["changed_path_count"] >= 2


def test_simulation_discard_marks_branch_cancelled(supply_network_scenario_dir):
    _, _, sim_engine = build_sim_engine(supply_network_scenario_dir)

    sim_engine.create_branch(
        simulation_id="sim.discard.0001",
        projection_name="world_state",
    )
    sim_engine.discard("sim.discard.0001")

    assert sim_engine.branches["sim.discard.0001"].status == "cancelled"


def test_simulation_result_is_durable_and_inspectable(supply_network_scenario_dir):
    _, _, sim_engine = build_sim_engine(supply_network_scenario_dir)

    sim_engine.create_branch(
        simulation_id="sim.inspect.0001",
        projection_name="world_state",
    )

    hypothetical = {
        "event_type": "shipment_delayed",
        "payload": {
            "shipment_id": "shipment.88421",
            "delay_hours": 9,
            "cause": "port_congestion"
        }
    }
    sim_engine.apply_hypothetical_event("sim.inspect.0001", hypothetical)
    sim_engine.run("sim.inspect.0001")

    saved = sim_engine.get_result("sim.inspect.0001")
    serialized = saved.as_dict()

    assert serialized["simulation_id"] == "sim.inspect.0001"
    assert serialized["status"] == "completed"
    assert serialized["hypothetical_events_applied"] == 1
    assert "changed_paths" in serialized["comparison_summary"]

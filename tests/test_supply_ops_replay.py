from pathlib import Path

from adapters.supply_ops.replay import (
    build_commitment_risk_event,
    build_recovery_hypothetical_events,
)
from adapters.supply_ops.translator import SupplyOpsTranslator
from core.event_store import InMemoryEventStore
from core.projector import SimpleProjector
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "adapters" / "supply_ops" / "fixtures"


def test_supply_ops_example_rebuilds_through_shared_replay_projector(
    supply_ops_scenario_dir,
):
    events = load_json(supply_ops_scenario_dir / "events.json")
    projection = load_json(supply_ops_scenario_dir / "projection.json")
    store = InMemoryEventStore()

    for index, event in enumerate(events):
        store.append("adapter-supply-ops.stream.%d" % index, event)

    replay = ReplayEngine(store, SimpleProjector)
    rebuilt = replay.rebuild("supply_ops_state", use_snapshot=False)

    assert rebuilt.source_event_offset == projection["source_event_offset"] == len(events) - 1
    assert rebuilt.state["events_processed"] == len(events)
    assert rebuilt.state["last_event_id"] == events[-1]["event_id"]
    assert rebuilt.state["commitments"]["commitment.retailer-4821"] == {
        "at_risk_units": 180,
        "risk_reason": "inventory_shortfall",
        "status": "capacity_requested",
        "planned_recovery_units": 180,
        "requested_capacity_units": 180,
    }
    assert rebuilt.state["inventory_positions"]["inventory.dallas.dc.widget-alpha"] == {
        "reallocated_units": 180,
        "destination_commitment_id": "commitment.retailer-4821",
    }
    assert rebuilt.state["capacity_buckets"]["capacity.dallas.packout.2026-03-23"] == {
        "requested_units": 180,
        "commitment_id": "commitment.retailer-4821",
    }


def test_translated_supply_ops_fixture_drives_simulation_branch_from_risk_baseline():
    translator = SupplyOpsTranslator()
    bundle = translator.load_fixture_bundle(REPO_ROOT, "require_approval_high_expedite")
    proposal = translator.translate(bundle)
    store = InMemoryEventStore()
    store.append(
        "adapter-supply-ops.commitment.retailer-4821",
        build_commitment_risk_event(bundle),
    )

    replay = ReplayEngine(store, SimpleProjector)
    simulation = SimulationEngine(replay, SimpleProjector)
    branch = simulation.create_branch(
        simulation_id="sim.supply-ops.replay-hardening.0001",
        projection_name="supply_ops_state",
        scenario_name="Recover translated high-expedite commitment from risk-only baseline",
        assumptions=["translated proposal stays proposal-shaped before hypothetical replay"],
        inputs={"proposal_id": proposal["proposal_id"]},
    )

    assert branch.base_event_offset == 0
    assert branch.base_state["commitments"]["commitment.retailer-4821"]["status"] == "at_risk"

    for event in build_recovery_hypothetical_events(proposal):
        simulation.apply_hypothetical_event(branch.simulation_id, event)

    result = simulation.run(branch.simulation_id)

    assert result.status == "completed"
    assert result.hypothetical_events_applied == 2
    assert result.base_state["commitments"]["commitment.retailer-4821"] == {
        "at_risk_units": 180,
        "risk_reason": "translated_fixture_signal",
        "status": "at_risk",
    }
    assert result.simulated_state["commitments"]["commitment.retailer-4821"] == {
        "at_risk_units": 180,
        "risk_reason": "translated_fixture_signal",
        "status": "capacity_requested",
        "planned_recovery_units": 180,
        "requested_capacity_units": 180,
    }
    assert result.simulated_state["inventory_positions"]["inventory.dallas.dc.widget-alpha"] == {
        "reallocated_units": 180,
        "destination_commitment_id": "commitment.retailer-4821",
    }
    assert result.simulated_state["capacity_buckets"]["capacity.dallas.packout.2026-03-23"] == {
        "requested_units": 180,
        "commitment_id": "commitment.retailer-4821",
    }
    assert result.comparison_summary["changed_paths"] == [
        "capacity_buckets.capacity.dallas.packout.2026-03-23",
        "commitments.commitment.retailer-4821.planned_recovery_units",
        "commitments.commitment.retailer-4821.requested_capacity_units",
        "commitments.commitment.retailer-4821.status",
        "events_processed",
        "inventory_positions.inventory.dallas.dc.widget-alpha",
        "last_event_id",
    ]


def test_translated_fixture_helpers_cover_all_supply_ops_translator_outputs():
    translator = SupplyOpsTranslator()

    for fixture_path in sorted((FIXTURES_DIR / "inbound").glob("*.json")):
        fixture_name = fixture_path.stem
        bundle = load_json(fixture_path)
        proposal = translator.translate(bundle)
        risk_event = build_commitment_risk_event(bundle)
        hypothetical_events = build_recovery_hypothetical_events(proposal)

        assert risk_event["event_type"] == "commitment_risk_detected"
        assert risk_event["payload"]["commitment_id"] == proposal["target_entities"][0]["entity_id"]
        assert len(hypothetical_events) == 2
        assert [event["event_type"] for event in hypothetical_events] == [
            "inventory_rebalance_planned",
            "capacity_reservation_requested",
        ]
        assert hypothetical_events[0]["payload"]["destination_commitment_id"] == proposal[
            "proposed_action"
        ]["parameters"]["commitment_id"]
        assert hypothetical_events[1]["payload"]["capacity_bucket_id"] == proposal[
            "proposed_action"
        ]["parameters"]["reserve_capacity_id"]

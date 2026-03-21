from pathlib import Path

from core.app_server import WorldRuntimeAppServer
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


REPO_ROOT = Path(__file__).resolve().parents[1]


def build_server():
    store = InMemoryEventStore()
    replay = ReplayEngine(store, SimpleProjector)
    sim_engine = SimulationEngine(replay, SimpleProjector)
    reasoning = ReasoningAdapter(replay)
    return WorldRuntimeAppServer(
        reasoning_adapter=reasoning,
        simulation_engine=sim_engine,
        replay_engine=replay,
        policy_engine=DeterministicPolicyEngine(),
    )


def test_world_game_collaboration_flow_end_to_end():
    server = build_server()
    session_id = server.handle_request("session.create")["result"]["session_id"]

    created = server.handle_request(
        "world_game.session.create",
        {
            "session_id": session_id,
            "label": "WG-M11 smoke",
            "actor_id": "actor.facilitator",
            "roles": ["facilitator"],
            "display_name": "Facilitator",
        },
    )
    assert created["ok"] is True
    assert created["result"]["session"]["session_meta"]["collaboration_enabled"] is True

    analyst = server.handle_request(
        "world_game.session.actor.add",
        {
            "session_id": session_id,
            "actor_id": "actor.analyst",
            "roles": ["analyst"],
            "requested_by_actor_id": "actor.facilitator",
        },
    )
    assert analyst["ok"] is True
    assert analyst["result"]["actor"]["roles"] == ["analyst"]

    approver = server.handle_request(
        "world_game.session.actor.add",
        {
            "session_id": session_id,
            "actor_id": "actor.approver",
            "roles": ["approver"],
            "requested_by_actor_id": "actor.facilitator",
        },
    )
    assert approver["ok"] is True

    listed = server.handle_request("world_game.session.actor.list", {"session_id": session_id})
    assert listed["ok"] is True
    assert listed["result"]["count"] == 3

    loaded = server.handle_request(
        "world_game.scenario.load",
        {
            "session_id": session_id,
            "scenario_id": "world-game-multi-region",
        },
    )
    assert loaded["ok"] is True

    set_stage = server.handle_request(
        "world_game.session.stage.set",
        {
            "session_id": session_id,
            "stage": "proposal_intake",
            "actor_id": "actor.facilitator",
        },
    )
    assert set_stage["ok"] is True
    assert set_stage["result"]["facilitation_state"]["stage"] == "proposal_intake"

    proposal = server.handle_request(
        "world_game.proposal.create",
        {
            "session_id": session_id,
            "title": "Distributed resilience path",
            "rationale": "Prioritize equitable energy resilience.",
            "assumptions": ["Demand remains within forecast band."],
            "intended_interventions": ["intervention.distributed-microgrids"],
            "expected_outcomes": ["Lower disparity spread"],
            "evidence_refs": [{"source_id": "evidence.grid.001", "summary": "Microgrid pilot results"}],
            "actor_id": "actor.analyst",
        },
    )
    assert proposal["ok"] is True
    proposal_id = proposal["result"]["proposal"]["proposal_id"]

    submitted = server.handle_request(
        "world_game.proposal.submit",
        {
            "session_id": session_id,
            "proposal_id": proposal_id,
            "actor_id": "actor.analyst",
        },
    )
    assert submitted["ok"] is True
    assert submitted["result"]["proposal"]["status"] == "submitted"

    unauthorized_advance = server.handle_request(
        "world_game.session.stage.advance",
        {
            "session_id": session_id,
            "actor_id": "actor.analyst",
        },
    )
    assert unauthorized_advance["ok"] is False
    assert "required capability" in unauthorized_advance["error"]

    stage_deliberation = server.handle_request(
        "world_game.session.stage.advance",
        {
            "session_id": session_id,
            "actor_id": "actor.facilitator",
        },
    )
    assert stage_deliberation["ok"] is True
    assert stage_deliberation["result"]["facilitation_state"]["stage"] == "deliberation"

    stage_selection = server.handle_request(
        "world_game.session.stage.advance",
        {
            "session_id": session_id,
            "actor_id": "actor.facilitator",
        },
    )
    assert stage_selection["ok"] is True
    assert stage_selection["result"]["facilitation_state"]["stage"] == "selection"

    adopted = server.handle_request(
        "world_game.proposal.adopt",
        {
            "session_id": session_id,
            "proposal_id": proposal_id,
            "actor_id": "actor.approver",
            "branch_id": "proposal-branch",
        },
    )
    assert adopted["ok"] is True
    assert adopted["result"]["proposal"]["status"] == "adopted"
    assert adopted["result"]["branch"]["branch_id"] == "proposal-branch"

    stage_simulation = server.handle_request(
        "world_game.session.stage.advance",
        {
            "session_id": session_id,
            "actor_id": "actor.facilitator",
        },
    )
    assert stage_simulation["ok"] is True
    assert stage_simulation["result"]["facilitation_state"]["stage"] == "simulation"

    turn = server.handle_request(
        "world_game.turn.run",
        {
            "session_id": session_id,
            "branch_id": "proposal-branch",
            "intervention_ids": ["intervention.distributed-microgrids"],
            "proposal_id": proposal_id,
            "actor_id": "actor.analyst",
        },
    )
    assert turn["ok"] is True
    assert turn["result"]["turn_result"]["committed"] is True

    annotation = server.handle_request(
        "world_game.annotation.create",
        {
            "session_id": session_id,
            "annotation_type": "risk",
            "target_type": "branch",
            "target_id": "proposal-branch",
            "body": "Watch upstream drought effects on agriculture.",
            "actor_id": "actor.analyst",
        },
    )
    assert annotation["ok"] is True
    annotation_id = annotation["result"]["annotation"]["annotation_id"]

    updated_annotation = server.handle_request(
        "world_game.annotation.update",
        {
            "session_id": session_id,
            "annotation_id": annotation_id,
            "body": "Watch upstream drought effects and fuel cost volatility.",
            "actor_id": "actor.analyst",
        },
    )
    assert updated_annotation["ok"] is True
    assert "fuel cost volatility" in updated_annotation["result"]["annotation"]["body"]

    compare = server.handle_request(
        "world_game.branch.compare",
        {
            "session_id": session_id,
            "branch_ids": ["baseline", "proposal-branch"],
            "include_annotation_summary": True,
        },
    )
    assert compare["ok"] is True
    assert "proposal-branch" in compare["result"]["annotation_summary"]

    provenance = server.handle_request(
        "world_game.provenance.inspect",
        {
            "session_id": session_id,
            "artifact_type": "branch",
            "artifact_id": "proposal-branch",
        },
    )
    assert provenance["ok"] is True
    lineage_types = [item["artifact_type"] for item in provenance["result"]["artifact"]["lineage"]]
    assert "proposal" in lineage_types
    assert "scenario" in lineage_types

    archived = server.handle_request(
        "world_game.annotation.archive",
        {
            "session_id": session_id,
            "annotation_id": annotation_id,
            "actor_id": "actor.analyst",
        },
    )
    assert archived["ok"] is True
    assert archived["result"]["annotation"]["status"] == "archived"


def test_world_game_actor_management_enforces_role_capabilities():
    server = build_server()
    session_id = server.handle_request("session.create")["result"]["session_id"]

    server.handle_request(
        "world_game.session.create",
        {
            "session_id": session_id,
            "actor_id": "actor.facilitator",
            "roles": ["facilitator"],
        },
    )
    server.handle_request(
        "world_game.session.actor.add",
        {
            "session_id": session_id,
            "actor_id": "actor.analyst",
            "roles": ["analyst"],
            "requested_by_actor_id": "actor.facilitator",
        },
    )

    unauthorized = server.handle_request(
        "world_game.session.actor.add",
        {
            "session_id": session_id,
            "actor_id": "actor.observer",
            "roles": ["observer"],
            "requested_by_actor_id": "actor.analyst",
        },
    )
    assert unauthorized["ok"] is False
    assert "required capability" in unauthorized["error"]

    removed = server.handle_request(
        "world_game.session.actor.remove",
        {
            "session_id": session_id,
            "actor_id": "actor.analyst",
            "requested_by_actor_id": "actor.facilitator",
        },
    )
    assert removed["ok"] is True
    remaining = removed["result"]["actors"]
    assert [item["actor_id"] for item in remaining] == ["actor.facilitator"]


def test_world_game_collaboration_session_export_import_round_trip():
    server = build_server()
    source_session_id = server.handle_request("session.create")["result"]["session_id"]

    created = server.handle_request(
        "world_game.session.create",
        {
            "session_id": source_session_id,
            "label": "WG-P5 durability source",
            "actor_id": "actor.facilitator",
            "roles": ["facilitator"],
            "display_name": "Facilitator",
        },
    )
    assert created["ok"] is True

    loaded = server.handle_request(
        "world_game.scenario.load",
        {
            "session_id": source_session_id,
            "scenario_id": "world-game-multi-region",
        },
    )
    assert loaded["ok"] is True

    analyst = server.handle_request(
        "world_game.session.actor.add",
        {
            "session_id": source_session_id,
            "actor_id": "actor.analyst",
            "roles": ["analyst"],
            "requested_by_actor_id": "actor.facilitator",
        },
    )
    assert analyst["ok"] is True

    server.handle_request(
        "world_game.session.stage.set",
        {
            "session_id": source_session_id,
            "stage": "proposal_intake",
            "actor_id": "actor.facilitator",
        },
    )

    proposal = server.handle_request(
        "world_game.proposal.create",
        {
            "session_id": source_session_id,
            "title": "Export/import continuity check",
            "rationale": "Ensure collaboration persistence survives process boundaries.",
            "intended_interventions": ["intervention.distributed-microgrids"],
            "expected_outcomes": ["Improved resilience"],
            "actor_id": "actor.analyst",
        },
    )
    assert proposal["ok"] is True
    proposal_id = proposal["result"]["proposal"]["proposal_id"]

    submitted = server.handle_request(
        "world_game.proposal.submit",
        {
            "session_id": source_session_id,
            "proposal_id": proposal_id,
            "actor_id": "actor.analyst",
        },
    )
    assert submitted["ok"] is True

    export_path = "tmp/world_game_studio_next/wg-p5-session-export.json"
    exported = server.handle_request(
        "world_game.session.export",
        {
            "session_id": source_session_id,
            "output_path": export_path,
            "actor_id": "actor.facilitator",
        },
    )
    assert exported["ok"] is True
    assert exported["result"]["bundle"]["bundle_type"] == "world_game.collaboration.session"
    assert exported["result"]["summary"]["proposal_count"] >= 1
    assert (REPO_ROOT / export_path).exists()

    target_session_id = server.handle_request("session.create")["result"]["session_id"]
    imported = server.handle_request(
        "world_game.session.import",
        {
            "session_id": target_session_id,
            "bundle": exported["result"]["bundle"],
            "actor_id": "actor.facilitator",
        },
    )
    assert imported["ok"] is True
    assert imported["result"]["session"]["session_meta"]["session_id"] == target_session_id
    assert imported["result"]["scenario"]["scenario_id"] == "world-game-multi-region"
    assert imported["result"]["summary"]["proposal_count"] >= 1

    listed = server.handle_request(
        "world_game.proposal.list",
        {
            "session_id": target_session_id,
        },
    )
    assert listed["ok"] is True
    assert any(item["proposal_id"] == proposal_id for item in listed["result"]["proposals"])

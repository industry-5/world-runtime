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


def test_world_game_runtime_flow_smoke():
    server = build_server()
    session = server.handle_request("session.create")
    session_id = session["result"]["session_id"]

    listed = server.handle_request("world_game.scenario.list")
    assert listed["ok"] is True
    scenario_ids = {item["scenario_id"] for item in listed["result"]["scenarios"]}
    assert "world-game-multi-region" in scenario_ids

    loaded = server.handle_request(
        "world_game.scenario.load",
        {
            "session_id": session_id,
            "scenario_id": "world-game-multi-region",
        },
    )
    assert loaded["ok"] is True
    assert loaded["result"]["branch"]["branch_id"] == "baseline"

    turn_main = server.handle_request(
        "world_game.turn.run",
        {
            "session_id": session_id,
            "branch_id": "baseline",
            "intervention_ids": ["intervention.distributed-microgrids"],
            "shock_ids": ["shock.upstream-drought-severe"],
            "approval_status": "approved",
        },
    )
    assert turn_main["ok"] is True
    assert turn_main["result"]["turn_result"]["committed"] is True

    created = server.handle_request(
        "world_game.branch.create",
        {
            "session_id": session_id,
            "source_branch_id": "baseline",
            "branch_id": "alt-branch",
        },
    )
    assert created["ok"] is True

    turn_alt = server.handle_request(
        "world_game.turn.run",
        {
            "session_id": session_id,
            "branch_id": "alt-branch",
            "intervention_ids": ["intervention.emergency-fuel-subsidy"],
            "shock_ids": [],
            "approval_status": "approved",
        },
    )
    assert turn_alt["ok"] is True
    assert turn_alt["result"]["policy_report"] is not None

    compared = server.handle_request(
        "world_game.branch.compare",
        {
            "session_id": session_id,
            "branch_ids": ["baseline", "alt-branch"],
        },
    )
    assert compared["ok"] is True
    assert len(compared["result"]["branches"]) == 2

    replay = server.handle_request(
        "world_game.replay.run",
        {
            "session_id": session_id,
            "branch_id": "baseline",
        },
    )
    assert replay["ok"] is True
    assert replay["result"]["replay_matches_live"] is True
    assert replay["result"]["replay_frame_count"] == replay["result"]["replay_turn_count"] + 1
    assert replay["result"]["replay_frames"][0]["turn_index"] == 0

    loaded_multi = server.handle_request(
        "world_game.scenario.load",
        {
            "session_id": session_id,
            "scenario_id": "world-game-multi-region",
        },
    )
    assert loaded_multi["ok"] is True
    assert loaded_multi["result"]["network_summary"]["enabled"] is True
    assert loaded_multi["result"]["equity_summary"]["enabled"] is True

    turn_multi = server.handle_request(
        "world_game.turn.run",
        {
            "session_id": session_id,
            "branch_id": "baseline",
            "intervention_ids": ["intervention.basin-efficiency-program"],
            "shock_ids": ["shock.upstream-drought-severe"],
            "approval_status": "approved",
        },
    )
    assert turn_multi["ok"] is True
    assert turn_multi["result"]["turn_result"]["network_diagnostics"]["mode"] == "networked_propagation"
    assert "equity_report" in turn_multi["result"]["turn_result"]

    network = server.handle_request(
        "world_game.network.inspect",
        {
            "session_id": session_id,
            "branch_id": "baseline",
        },
    )
    assert network["ok"] is True
    assert network["result"]["network_summary"]["flow_count"] >= 1

    equity = server.handle_request(
        "world_game.equity.report",
        {
            "session_id": session_id,
            "branch_id": "baseline",
        },
    )
    assert equity["ok"] is True
    assert "disparity_index" in equity["result"]["equity_report"]


def test_world_game_authoring_to_runtime_smoke_path():
    server = build_server()
    session = server.handle_request("session.create")
    session_id = session["result"]["session_id"]

    listed = server.handle_request("world_game.authoring.template.list")
    assert listed["ok"] is True
    bundle_lookup = {
        item["bundle_id"]: item for item in listed["result"]["bundles"]
    }
    bundle = bundle_lookup["wg.authoring.bundle.multi-region.v1"]
    template_id = bundle["templates"][0]["template_id"]

    instantiated = server.handle_request(
        "world_game.authoring.bundle.instantiate",
        {
            "bundle_path": bundle["bundle_path"],
            "template_id": template_id,
            "parameter_values": {
                "scenario_suffix": "wg-m10-smoke-path",
                "region_count": 2,
            },
            "scenario_output_path": "tmp/world_game_studio/wg-m10-smoke-path.scenario.json",
        },
    )
    assert instantiated["ok"] is True
    assert instantiated["result"]["scenario_id"].endswith("wg-m10-smoke-path")
    assert len(instantiated["result"]["scenario"]["regions"]) == 2

    loaded = server.handle_request(
        "world_game.scenario.load",
        {
            "session_id": session_id,
            "scenario_path": instantiated["result"]["scenario_output_path"],
        },
    )
    assert loaded["ok"] is True
    assert loaded["result"]["scenario_id"].endswith("wg-m10-smoke-path")

    run_turn_response = server.handle_request(
        "world_game.turn.run",
        {
            "session_id": session_id,
            "branch_id": "baseline",
            "intervention_ids": [loaded["result"]["intervention_ids"][0]],
            "shock_ids": [],
            "approval_status": "approved",
        },
    )
    assert run_turn_response["ok"] is True
    assert run_turn_response["result"]["turn_result"]["committed"] is True

from pathlib import Path

from adapters.world_game.runtime import initialize_baseline_state, load_world_game_scenario, replay_world_game, run_turn
from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[3]
SCENARIO_PATH = REPO_ROOT / "examples" / "scenarios" / "world-game-multi-region" / "scenario.json"
NETWORK_SCENARIO_PATH = REPO_ROOT / "examples" / "scenarios" / "world-game-multi-region" / "scenario.json"
POLICY_PACK_PATH = REPO_ROOT / "adapters" / "world_game" / "policies" / "world_game_policy_pack.json"


def test_world_game_replay_reconstructs_final_state():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    policies = load_json(POLICY_PACK_PATH)["policies"]
    engine = DeterministicPolicyEngine()

    state = initialize_baseline_state(scenario, branch_id="baseline")

    first = run_turn(
        state=state,
        scenario=scenario,
        intervention_ids=["intervention.basin-efficiency-program"],
        shock_ids=["shock.upstream-drought-severe"],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )
    second = run_turn(
        state=first["state"],
        scenario=scenario,
        intervention_ids=["intervention.distributed-microgrids"],
        shock_ids=["shock.coastal-port-disruption"],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )

    replay = replay_world_game(
        scenario=scenario,
        events=second["state"]["event_log"],
        policy_evaluator=engine,
        policies=policies,
    )

    assert second["state"]["turn"] == 2
    assert replay["state"]["turn"] == 2
    assert replay["state"]["scorecard"] == second["state"]["scorecard"]


def test_world_game_replay_preserves_network_diagnostics_and_equity_outputs():
    scenario = load_world_game_scenario(NETWORK_SCENARIO_PATH)
    policies = load_json(POLICY_PACK_PATH)["policies"]
    engine = DeterministicPolicyEngine()

    state = initialize_baseline_state(scenario, branch_id="baseline")
    executed = run_turn(
        state=state,
        scenario=scenario,
        intervention_ids=["intervention.basin-efficiency-program"],
        shock_ids=["shock.upstream-drought-severe"],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )

    replay = replay_world_game(
        scenario=scenario,
        events=executed["state"]["event_log"],
        policy_evaluator=engine,
        policies=policies,
    )

    live_diag = executed["state"]["latest_network_diagnostics"]
    replay_diag = replay["state"]["latest_network_diagnostics"]
    live_equity = executed["state"]["latest_equity_report"]
    replay_equity = replay["state"]["latest_equity_report"]

    assert replay_diag == live_diag
    assert replay_equity == live_equity

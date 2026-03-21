from pathlib import Path

from adapters.world_game.runtime import create_branch, initialize_baseline_state, load_world_game_scenario, run_turn
from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[3]
SCENARIO_PATH = REPO_ROOT / "examples" / "scenarios" / "world-game-multi-region" / "scenario.json"
POLICY_PACK_PATH = REPO_ROOT / "adapters" / "world_game" / "policies" / "world_game_policy_pack.json"


def test_world_game_branch_isolation_is_preserved():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    policies = load_json(POLICY_PACK_PATH)["policies"]
    engine = DeterministicPolicyEngine()

    baseline = initialize_baseline_state(scenario, branch_id="baseline")
    branch_a = create_branch(baseline, branch_id="branch.a", parent_branch_id="baseline")
    branch_b = create_branch(baseline, branch_id="branch.b", parent_branch_id="baseline")

    run_a = run_turn(
        state=branch_a,
        scenario=scenario,
        intervention_ids=["intervention.distributed-microgrids"],
        shock_ids=[],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )
    run_b = run_turn(
        state=branch_b,
        scenario=scenario,
        intervention_ids=["intervention.emergency-fuel-subsidy"],
        shock_ids=[],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )

    assert baseline["turn"] == 0
    assert run_a["state"]["turn"] == 1
    assert run_b["state"]["turn"] == 1
    assert run_a["state"]["scorecard"] != run_b["state"]["scorecard"]
    assert baseline["indicator_values"] != run_a["state"]["indicator_values"]
    assert baseline["indicator_values"] != run_b["state"]["indicator_values"]

from pathlib import Path

from adapters.world_game.runtime import compare_branches, create_branch, initialize_baseline_state, load_world_game_scenario, run_turn
from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[3]
SCENARIO_PATH = REPO_ROOT / "examples" / "scenarios" / "world-game-multi-region" / "scenario.json"
POLICY_PACK_PATH = REPO_ROOT / "adapters" / "world_game" / "policies" / "world_game_policy_pack.json"


def test_world_game_branch_comparison_is_deterministic():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    policies = load_json(POLICY_PACK_PATH)["policies"]
    engine = DeterministicPolicyEngine()

    base = initialize_baseline_state(scenario, branch_id="baseline")
    a = create_branch(base, branch_id="branch.a", parent_branch_id="baseline")
    b = create_branch(base, branch_id="branch.b", parent_branch_id="baseline")
    c = create_branch(base, branch_id="branch.c", parent_branch_id="baseline")

    a = run_turn(
        state=a,
        scenario=scenario,
        intervention_ids=["intervention.distributed-microgrids"],
        shock_ids=[],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )["state"]
    b = run_turn(
        state=b,
        scenario=scenario,
        intervention_ids=["intervention.basin-efficiency-program"],
        shock_ids=["shock.upstream-drought-severe"],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )["state"]
    c = run_turn(
        state=c,
        scenario=scenario,
        intervention_ids=["intervention.emergency-fuel-subsidy"],
        shock_ids=[],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )["state"]

    first = compare_branches(scenario, [a, b, c])
    second = compare_branches(scenario, [a, b, c])

    assert len(first["branches"]) == 3
    assert first["rankings"] == second["rankings"]
    assert first["summary"]["best_equity_branch"] in first["rankings"]

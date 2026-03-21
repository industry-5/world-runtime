from pathlib import Path

from adapters.world_game.runtime.engine import compute_scorecard
from adapters.world_game.runtime import initialize_baseline_state, load_world_game_scenario, run_turn
from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[3]
SCENARIO_PATH = REPO_ROOT / "examples" / "scenarios" / "world-game-multi-region" / "scenario.json"
POLICY_PACK_PATH = REPO_ROOT / "adapters" / "world_game" / "policies" / "world_game_policy_pack.json"


def test_world_game_policy_warn_require_approval_and_deny_paths():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    policies = load_json(POLICY_PACK_PATH)["policies"]
    engine = DeterministicPolicyEngine()

    warn_state = initialize_baseline_state(scenario, branch_id="warn")
    for region_id in warn_state["regions"]:
        warn_state["indicator_values"][region_id]["water_security"] = 30
        warn_state["indicator_values"][region_id]["emissions_intensity"] = 20
        warn_state["indicator_values"][region_id]["equity_score"] = 60
    warn_state["scorecard"] = compute_scorecard(warn_state, scenario)

    warn_result = run_turn(
        state=warn_state,
        scenario=scenario,
        intervention_ids=[],
        shock_ids=[],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )
    assert warn_result["turn_result"]["policy_outcome"] == "warn"
    assert warn_result["turn_result"]["committed"] is True

    approval_state = initialize_baseline_state(scenario, branch_id="approval")
    approval_result = run_turn(
        state=approval_state,
        scenario=scenario,
        intervention_ids=["intervention.centralized-transmission-buildout"],
        shock_ids=[],
        policy_evaluator=engine,
        policies=policies,
        approval_status="pending",
    )
    assert approval_result["turn_result"]["policy_outcome"] == "require_approval"
    assert approval_result["turn_result"]["committed"] is False

    deny_state = initialize_baseline_state(scenario, branch_id="deny")
    for region_id in deny_state["regions"]:
        deny_state["indicator_values"][region_id]["water_security"] = 5
    deny_state["scorecard"] = compute_scorecard(deny_state, scenario)

    deny_result = run_turn(
        state=deny_state,
        scenario=scenario,
        intervention_ids=[],
        shock_ids=[],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )
    assert deny_result["turn_result"]["policy_outcome"] == "deny"
    assert deny_result["turn_result"]["committed"] is False

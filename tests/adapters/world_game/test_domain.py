from pathlib import Path

from adapters.world_game.runtime import (
    initialize_baseline_state,
    load_world_game_scenario,
    run_turn,
)
from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[3]
SCENARIO_PATH = REPO_ROOT / "examples" / "scenarios" / "world-game-multi-region" / "scenario.json"
POLICY_PACK_PATH = REPO_ROOT / "adapters" / "world_game" / "policies" / "world_game_policy_pack.json"


def _policies():
    return load_json(POLICY_PACK_PATH)["policies"]


def test_world_game_scenario_loads_and_baseline_score_exists():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    state = initialize_baseline_state(scenario, branch_id="baseline")

    assert scenario["scenario_id"] == "world-game-multi-region"
    assert state["turn"] == 0
    assert state["scorecard"]["composite_score"] > 0
    assert "electricity_access" in state["scorecard"]["indicator_scores"]


def test_world_game_turn_execution_is_deterministic_for_same_input():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    base = initialize_baseline_state(scenario, branch_id="baseline")
    engine = DeterministicPolicyEngine()

    first = run_turn(
        state=base,
        scenario=scenario,
        intervention_ids=["intervention.basin-efficiency-program"],
        shock_ids=["shock.upstream-drought-severe"],
        policy_evaluator=engine,
        policies=_policies(),
        approval_status="approved",
    )
    second = run_turn(
        state=base,
        scenario=scenario,
        intervention_ids=["intervention.basin-efficiency-program"],
        shock_ids=["shock.upstream-drought-severe"],
        policy_evaluator=engine,
        policies=_policies(),
        approval_status="approved",
    )

    assert first["turn_result"]["committed"] is True
    assert second["turn_result"]["committed"] is True
    assert first["state"]["indicator_values"] == second["state"]["indicator_values"]
    assert first["state"]["scorecard"] == second["state"]["scorecard"]


def test_world_game_require_approval_blocks_canonical_commit_until_approved():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    base = initialize_baseline_state(scenario, branch_id="baseline")
    engine = DeterministicPolicyEngine()

    pending = run_turn(
        state=base,
        scenario=scenario,
        intervention_ids=["intervention.centralized-transmission-buildout"],
        shock_ids=[],
        policy_evaluator=engine,
        policies=_policies(),
        approval_status="pending",
    )
    approved = run_turn(
        state=base,
        scenario=scenario,
        intervention_ids=["intervention.centralized-transmission-buildout"],
        shock_ids=[],
        policy_evaluator=engine,
        policies=_policies(),
        approval_status="approved",
    )

    assert pending["turn_result"]["policy_outcome"] == "require_approval"
    assert pending["turn_result"]["committed"] is False
    assert pending["state"]["turn"] == 0

    assert approved["turn_result"]["policy_outcome"] == "require_approval"
    assert approved["turn_result"]["committed"] is True
    assert approved["state"]["turn"] == 1

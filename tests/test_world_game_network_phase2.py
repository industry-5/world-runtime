from pathlib import Path

import pytest

from core.domains.world_game import (
    build_equity_report,
    compare_branches,
    create_branch,
    initialize_baseline_state,
    inspect_network_state,
    load_world_game_scenario,
    normalize_scenario_definition,
    run_turn,
)
from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = REPO_ROOT / "examples" / "scenarios" / "world-game-multi-region" / "scenario.json"
POLICY_PACK_PATH = REPO_ROOT / "adapters" / "world_game" / "policies" / "world_game_policy_pack.json"


def _policies():
    return load_json(POLICY_PACK_PATH)["policies"]


def test_phase2_scenario_load_exposes_network_and_equity_contracts():
    scenario = load_world_game_scenario(SCENARIO_PATH)

    assert scenario["has_network_contract"] is True
    assert scenario["has_equity_contract"] is True
    assert len(scenario["dependency_graph"]["topological_order"]) == 3
    assert len(scenario["resource_stocks"]["items"]) == 3
    assert len(scenario["resource_flows"]["items"]) == 3
    assert len(scenario["spillover_rules"]["items"]) == 2


def test_phase2_turn_determinism_includes_network_and_equity_payloads():
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

    assert first["state"]["indicator_values"] == second["state"]["indicator_values"]
    assert first["turn_result"]["network_diagnostics"] == second["turn_result"]["network_diagnostics"]
    assert first["turn_result"]["equity_report"] == second["turn_result"]["equity_report"]


def test_phase2_flow_conservation_and_capacity_clipping_are_reported():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    base = initialize_baseline_state(scenario, branch_id="baseline")

    result = run_turn(
        state=base,
        scenario=scenario,
        intervention_ids=["intervention.distributed-microgrids"],
        shock_ids=[],
        policy_evaluator=DeterministicPolicyEngine(),
        policies=_policies(),
        approval_status="approved",
    )

    diagnostics = result["turn_result"]["network_diagnostics"]
    conservation = diagnostics["conservation_check"]

    assert diagnostics["mode"] == "networked_propagation"
    assert len(diagnostics["saturated_edges"]) >= 1
    assert abs(float(conservation["balance_error"])) <= 0.0001


def test_phase2_spillovers_apply_only_downstream_and_surface_in_diagnostics():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    state = initialize_baseline_state(scenario, branch_id="baseline")

    result = run_turn(
        state=state,
        scenario=scenario,
        intervention_ids=["intervention.port-dredging-upgrade"],
        shock_ids=["shock.coastal-port-disruption"],
        policy_evaluator=DeterministicPolicyEngine(),
        policies=_policies(),
        approval_status="approved",
    )

    spillovers = result["turn_result"]["network_diagnostics"]["spillover_contributions"]
    assert len(spillovers) >= 1
    assert all(item["from_node_id"] != item["to_node_id"] for item in spillovers)


def test_phase2_equity_report_branch_tradeoffs_surface():
    scenario = load_world_game_scenario(SCENARIO_PATH)
    base = initialize_baseline_state(scenario, branch_id="baseline")
    policies = _policies()
    engine = DeterministicPolicyEngine()

    centralized = create_branch(base, branch_id="branch.centralized", parent_branch_id="baseline")
    distributed = create_branch(base, branch_id="branch.distributed", parent_branch_id="baseline")

    centralized = run_turn(
        state=centralized,
        scenario=scenario,
        intervention_ids=["intervention.centralized-transmission-buildout"],
        shock_ids=[],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )["state"]
    distributed = run_turn(
        state=distributed,
        scenario=scenario,
        intervention_ids=["intervention.distributed-microgrids"],
        shock_ids=[],
        policy_evaluator=engine,
        policies=policies,
        approval_status="approved",
    )["state"]

    centralized_equity = build_equity_report(centralized, scenario)
    distributed_equity = build_equity_report(distributed, scenario)
    assert centralized_equity["disparity_index"] != distributed_equity["disparity_index"]

    report = compare_branches(scenario, [centralized, distributed])
    assert report["summary"]["best_equity_branch"] in {"branch.centralized", "branch.distributed"}
    assert len(report["summary"]["regional_tradeoffs"]) >= 1

    network_snapshot = inspect_network_state(scenario, centralized)
    assert network_snapshot["network_summary"]["enabled"] is True


def test_phase2_dependency_graph_cycle_fails_normalization():
    payload = load_json(SCENARIO_PATH)
    payload["dependency_graph"]["edges"].append(
        {
            "edge_id": "edge.invalid.backflow",
            "from_node_id": "node.manufacturing_belt",
            "to_node_id": "node.upstream_water_basin",
            "capacity": 2,
            "latency_turns": 0,
        }
    )

    with pytest.raises(ValueError, match="cycle"):
        normalize_scenario_definition(payload)


def test_phase2_unknown_node_reference_fails_normalization():
    payload = load_json(SCENARIO_PATH)
    payload["resource_flows"][0]["to_node_id"] = "node.unknown"

    with pytest.raises(ValueError, match="unknown to_node_id"):
        normalize_scenario_definition(payload)


def test_phase2_spillover_upstream_reference_fails_normalization():
    payload = load_json(SCENARIO_PATH)
    payload["spillover_rules"][0]["from_node_id"] = "node.manufacturing_belt"
    payload["spillover_rules"][0]["to_node_id"] = "node.upstream_water_basin"

    with pytest.raises(ValueError, match="downstream connected"):
        normalize_scenario_definition(payload)

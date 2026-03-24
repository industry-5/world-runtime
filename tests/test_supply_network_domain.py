from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_supply_network_policy_warns_on_cost_delta(supply_network_scenario_dir):
    policy = load_json(supply_network_scenario_dir / "policy.json")
    proposal = load_json(supply_network_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "warn"
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_supply_network_reroute_options_capture_tradeoffs(supply_network_scenario_dir):
    policy = load_json(supply_network_scenario_dir / "policy.json")
    proposals = load_json(supply_network_scenario_dir / "reroute_options.json")

    expedite = proposals[0]
    defer = proposals[1]
    engine = DeterministicPolicyEngine()

    expedite_report = engine.evaluate_policies([policy], expedite)
    defer_report = engine.evaluate_policies([policy], defer)

    assert expedite_report.final_outcome == "warn"
    assert defer_report.final_outcome == "allow"
    assert defer_report.denied is False


def test_supply_network_decision_tracks_simulation_recommendation(supply_network_scenario_dir):
    proposal = load_json(supply_network_scenario_dir / "proposal.json")
    decision = load_json(supply_network_scenario_dir / "decision.json")
    simulation = load_json(supply_network_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "warn"
    assert simulation["outcomes"]["recommended_proposal_id"] == proposal["proposal_id"]
    assert (
        simulation["outcomes"]["simulated_output_loss_percent"]
        < simulation["outcomes"]["baseline_output_loss_percent"]
    )

from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_power_grid_policy_warns_and_requires_approval(power_grid_scenario_dir):
    policy = load_json(power_grid_scenario_dir / "policy.json")
    proposal = load_json(power_grid_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_power_grid_contingency_options_cover_deny_and_allow_paths(power_grid_scenario_dir):
    policy = load_json(power_grid_scenario_dir / "policy.json")
    proposals = load_json(power_grid_scenario_dir / "contingency_options.json")

    unsafe = proposals[0]
    imports = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    imports_report = engine.evaluate_policies([policy], imports)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert imports_report.final_outcome == "allow"
    assert imports_report.requires_approval is False


def test_power_grid_decision_tracks_least_bad_choice(power_grid_scenario_dir):
    proposal = load_json(power_grid_scenario_dir / "proposal.json")
    decision = load_json(power_grid_scenario_dir / "decision.json")
    simulation = load_json(power_grid_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == "proposal.power-grid.imports.0003"
    assert simulation["outcomes"]["customer_interruptions_avoided"] == 12500

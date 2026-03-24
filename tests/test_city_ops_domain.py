from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_city_ops_policy_warns_and_requires_approval(city_ops_scenario_dir):
    policy = load_json(city_ops_scenario_dir / "policy.json")
    proposal = load_json(city_ops_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_city_ops_coordination_options_cover_deny_and_allow_paths(city_ops_scenario_dir):
    policy = load_json(city_ops_scenario_dir / "policy.json")
    proposals = load_json(city_ops_scenario_dir / "coordination_options.json")

    unsafe = proposals[0]
    targeted = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    targeted_report = engine.evaluate_policies([policy], targeted)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert targeted_report.final_outcome == "allow"
    assert targeted_report.requires_approval is False


def test_city_ops_decision_tracks_broader_protective_path(city_ops_scenario_dir):
    proposal = load_json(city_ops_scenario_dir / "proposal.json")
    decision = load_json(city_ops_scenario_dir / "decision.json")
    simulation = load_json(city_ops_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == "proposal.city-ops.targeted.0003"
    assert simulation["outcomes"]["hospital_access_maintained"] is True

from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_lab_science_policy_warns_and_requires_approval(lab_science_scenario_dir):
    policy = load_json(lab_science_scenario_dir / "policy.json")
    proposal = load_json(lab_science_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_lab_science_release_options_cover_deny_and_allow_paths(lab_science_scenario_dir):
    policy = load_json(lab_science_scenario_dir / "policy.json")
    proposals = load_json(lab_science_scenario_dir / "release_options.json")

    unsafe = proposals[0]
    retest = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    retest_report = engine.evaluate_policies([policy], retest)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert retest_report.final_outcome == "allow"
    assert retest_report.requires_approval is False


def test_lab_science_decision_tracks_reviewed_release_path(lab_science_scenario_dir):
    proposal = load_json(lab_science_scenario_dir / "proposal.json")
    decision = load_json(lab_science_scenario_dir / "decision.json")
    simulation = load_json(lab_science_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == "proposal.lab-science.retest.0003"
    assert simulation["outcomes"]["projected_data_reliability_score"] == 99

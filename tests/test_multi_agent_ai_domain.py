from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_multi_agent_ai_policy_warns_and_requires_approval(multi_agent_ai_scenario_dir):
    policy = load_json(multi_agent_ai_scenario_dir / "policy.json")
    proposal = load_json(multi_agent_ai_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_multi_agent_ai_branch_options_cover_deny_and_allow_paths(
    multi_agent_ai_scenario_dir,
):
    policy = load_json(multi_agent_ai_scenario_dir / "policy.json")
    proposals = load_json(multi_agent_ai_scenario_dir / "branch_options.json")

    unsafe = proposals[0]
    reviewed = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    reviewed_report = engine.evaluate_policies([policy], reviewed)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert reviewed_report.final_outcome == "allow"
    assert reviewed_report.requires_approval is False


def test_multi_agent_ai_decision_tracks_reviewed_coordination_path(
    multi_agent_ai_scenario_dir,
):
    proposal = load_json(multi_agent_ai_scenario_dir / "proposal.json")
    decision = load_json(multi_agent_ai_scenario_dir / "decision.json")
    simulation = load_json(multi_agent_ai_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == (
        "proposal.multi-agent-ai.reviewed.0003"
    )
    assert simulation["outcomes"]["projected_review_cycles_avoided"] == 2

from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_open_agent_world_policy_warns_and_requires_approval(
    open_agent_world_scenario_dir,
):
    policy = load_json(open_agent_world_scenario_dir / "policy.json")
    proposal = load_json(open_agent_world_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_open_agent_world_intervention_options_cover_deny_and_allow_paths(
    open_agent_world_scenario_dir,
):
    policy = load_json(open_agent_world_scenario_dir / "policy.json")
    proposals = load_json(open_agent_world_scenario_dir / "intervention_options.json")

    unsafe = proposals[0]
    bounded = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    bounded_report = engine.evaluate_policies([policy], bounded)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert bounded_report.final_outcome == "allow"
    assert bounded_report.requires_approval is False


def test_open_agent_world_decision_tracks_governed_intervention_path(
    open_agent_world_scenario_dir,
):
    proposal = load_json(open_agent_world_scenario_dir / "proposal.json")
    decision = load_json(open_agent_world_scenario_dir / "decision.json")
    simulation = load_json(open_agent_world_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == (
        "proposal.open-agent-world.bounded.0003"
    )
    assert simulation["outcomes"]["projected_conflicts_reduced_percent"] == 31

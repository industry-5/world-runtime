from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_semantic_system_policy_requires_approval_for_breaking_change(
    semantic_system_scenario_dir,
):
    policy = load_json(semantic_system_scenario_dir / "policy.json")
    proposal = load_json(semantic_system_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_semantic_system_conflicting_proposals_cover_deny_and_allow_paths(
    semantic_system_scenario_dir,
):
    policy = load_json(semantic_system_scenario_dir / "policy.json")
    proposals = load_json(semantic_system_scenario_dir / "conflicting_proposals.json")

    unsafe = proposals[0]
    alias_first = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    alias_report = engine.evaluate_policies([policy], alias_first)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert alias_report.final_outcome == "allow"
    assert alias_report.requires_approval is False


def test_semantic_system_default_policy_requires_governed_change_review(
    semantic_system_scenario_dir,
):
    default_policy = load_json(
        semantic_system_scenario_dir.parents[2]
        / "adapters"
        / "semantic_system"
        / "policies"
        / "default_policy.json"
    )
    proposal = load_json(semantic_system_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([default_policy], proposal)

    outcomes = {evaluation.outcome for evaluation in report.evaluations}
    assert report.final_outcome == "require_approval"
    assert "warn" in outcomes
    assert "require_approval" in outcomes

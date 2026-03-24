from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_air_traffic_policy_enforces_require_approval_and_warn(air_traffic_scenario_dir):
    policy = load_json(air_traffic_scenario_dir / "policy.json")
    proposal = load_json(air_traffic_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_air_traffic_conflicting_proposals_follow_constrained_paths(air_traffic_scenario_dir):
    policy = load_json(air_traffic_scenario_dir / "policy.json")
    proposals = load_json(air_traffic_scenario_dir / "conflicting_proposals.json")

    unsafe = proposals[0]
    safer = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    safer_report = engine.evaluate_policies([policy], safer)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True

    assert safer_report.final_outcome == "warn"
    assert safer_report.denied is False
    assert safer_report.requires_approval is False


def test_air_traffic_default_policy_requires_simulation_evidence(air_traffic_scenario_dir):
    default_policy = load_json(
        air_traffic_scenario_dir.parents[2]
        / "adapters"
        / "air_traffic"
        / "policies"
        / "default_policy.json"
    )
    proposal = load_json(air_traffic_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([default_policy], proposal)

    outcomes = {evaluation.outcome for evaluation in report.evaluations}
    assert report.final_outcome == "require_approval"
    assert "warn" in outcomes
    assert "require_approval" in outcomes

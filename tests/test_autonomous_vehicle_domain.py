from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_autonomous_vehicle_policy_warns_and_requires_approval(
    autonomous_vehicle_scenario_dir,
):
    policy = load_json(autonomous_vehicle_scenario_dir / "policy.json")
    proposal = load_json(autonomous_vehicle_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_autonomous_vehicle_maneuver_options_cover_deny_and_allow_paths(
    autonomous_vehicle_scenario_dir,
):
    policy = load_json(autonomous_vehicle_scenario_dir / "policy.json")
    proposals = load_json(autonomous_vehicle_scenario_dir / "maneuver_options.json")

    unsafe = proposals[0]
    yield_first = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    yield_report = engine.evaluate_policies([policy], yield_first)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert yield_report.final_outcome == "allow"
    assert yield_report.requires_approval is False


def test_autonomous_vehicle_decision_tracks_supervised_motion_path(
    autonomous_vehicle_scenario_dir,
):
    proposal = load_json(autonomous_vehicle_scenario_dir / "proposal.json")
    decision = load_json(autonomous_vehicle_scenario_dir / "decision.json")
    simulation = load_json(autonomous_vehicle_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == (
        "proposal.autonomous-vehicle.yield.0003"
    )
    assert simulation["outcomes"]["projected_near_miss_risk_reduction_percent"] == 24

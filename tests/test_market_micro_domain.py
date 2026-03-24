from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_market_micro_policy_warns_and_requires_approval(market_micro_scenario_dir):
    policy = load_json(market_micro_scenario_dir / "policy.json")
    proposal = load_json(market_micro_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_market_micro_risk_options_cover_deny_and_allow_paths(market_micro_scenario_dir):
    policy = load_json(market_micro_scenario_dir / "policy.json")
    proposals = load_json(market_micro_scenario_dir / "risk_options.json")

    unsafe = proposals[0]
    derisk = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    derisk_report = engine.evaluate_policies([policy], derisk)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert derisk_report.final_outcome == "allow"
    assert derisk_report.requires_approval is False


def test_market_micro_decision_tracks_supervised_rebalance(market_micro_scenario_dir):
    proposal = load_json(market_micro_scenario_dir / "proposal.json")
    decision = load_json(market_micro_scenario_dir / "decision.json")
    simulation = load_json(market_micro_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == "proposal.market-micro.derisk.0003"
    assert simulation["outcomes"]["projected_loss_avoided_bps"] == 17

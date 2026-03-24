from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_digital_twin_policy_warns_and_requires_approval(digital_twin_scenario_dir):
    policy = load_json(digital_twin_scenario_dir / "policy.json")
    proposal = load_json(digital_twin_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_digital_twin_overlay_options_cover_deny_and_allow_paths(digital_twin_scenario_dir):
    policy = load_json(digital_twin_scenario_dir / "policy.json")
    proposals = load_json(digital_twin_scenario_dir / "overlay_options.json")

    unsafe = proposals[0]
    power_grid_first = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    power_grid_first_report = engine.evaluate_policies([policy], power_grid_first)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert power_grid_first_report.final_outcome == "allow"
    assert power_grid_first_report.requires_approval is False


def test_digital_twin_host_bindings_attach_power_grid_then_city_ops(digital_twin_scenario_dir):
    proposal = load_json(digital_twin_scenario_dir / "proposal.json")
    decision = load_json(digital_twin_scenario_dir / "decision.json")
    simulation = load_json(digital_twin_scenario_dir / "simulation.json")
    host_bindings = load_json(digital_twin_scenario_dir / "host_bindings.json")

    assert [binding["host_adapter_id"] for binding in host_bindings] == [
        "adapter-power-grid",
        "adapter-city-ops",
    ]
    assert [binding["proof_sequence"] for binding in host_bindings] == [1, 2]
    assert all(binding["writeback_enabled"] is False for binding in host_bindings)
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == (
        "proposal.digital-twin.power-grid-first.0003"
    )
    assert simulation["outcomes"]["projected_cross_host_alerts_suppressed"] == 4

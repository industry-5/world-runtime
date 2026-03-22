from core.policy_engine import SimplePolicyEngine
from conftest import load_json


def test_supply_policy_warns_on_cost_threshold(supply_network_scenario_dir):
    policy = load_json(supply_network_scenario_dir / "policy.json")
    proposal = load_json(supply_network_scenario_dir / "proposal.json")

    engine = SimplePolicyEngine()
    results = engine.evaluate_policy(policy, proposal)

    assert len(results) >= 1
    assert any(r.outcome == "warn" for r in results)


def test_air_traffic_policy_can_deny_unsafe_branch(air_traffic_scenario_dir):
    policy = load_json(air_traffic_scenario_dir / "policy.json")
    proposal = load_json(air_traffic_scenario_dir / "proposal.json")
    proposal["proposed_action"]["action_type"] = "clear_conflict_takeoff_without_separation"

    engine = SimplePolicyEngine()
    results = engine.evaluate_policy(policy, proposal)

    assert len(results) >= 1
    assert any(r.outcome == "deny" for r in results)


def test_policy_defaults_to_allow_when_no_rule_matches(top_level_example_paths):
    policy = load_json(top_level_example_paths["policy"])
    proposal = load_json(top_level_example_paths["proposal"])

    proposal["proposed_action"]["parameters"]["cost_delta_percent"] = 2

    engine = SimplePolicyEngine()
    results = engine.evaluate_policy(policy, proposal)

    assert len(results) == 1
    assert results[0].outcome == "allow"

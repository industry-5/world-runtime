from copy import deepcopy

from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_invalid_action_is_denied(top_level_example_paths):
    proposal = load_json(top_level_example_paths["proposal"])
    proposal["proposed_action"].pop("action_type", None)

    engine = DeterministicPolicyEngine()
    report = engine.evaluate_policies([], proposal)

    assert report.denied is True
    assert report.final_outcome == "deny"
    assert report.evaluations[0].rule_id == "rule.system.action-type-required"


def test_require_approval_is_flagged(top_level_example_paths):
    proposal = load_json(top_level_example_paths["proposal"])

    policy = {
        "policy_id": "policy.schema-migration",
        "policy_name": "schema_migration_requires_approval",
        "default_outcome": "allow",
        "rules": [
            {
                "rule_id": "rule.schema-migration",
                "rule_name": "Schema migration approval required",
                "condition": {
                    "field": "proposed_action.action_type",
                    "operator": "equals",
                    "value": "reroute_shipment"
                },
                "outcome": "require_approval",
                "message_template": "Human approval required for this action."
            }
        ]
    }

    engine = DeterministicPolicyEngine()
    report = engine.evaluate_policies([policy], proposal)

    assert report.denied is False
    assert report.requires_approval is True
    assert report.final_outcome == "require_approval"
    assert any(e.outcome == "require_approval" for e in report.evaluations)


def test_deny_outcomes_override_warn_and_require_approval(supply_network_scenario_dir, air_traffic_scenario_dir):
    supply_policy = load_json(supply_network_scenario_dir / "policy.json")
    air_traffic_policy = load_json(air_traffic_scenario_dir / "policy.json")
    proposal = load_json(air_traffic_scenario_dir / "proposal.json")
    proposal["proposed_action"]["action_type"] = "clear_conflict_takeoff_without_separation"

    approval_policy = {
        "policy_id": "policy.manual-review",
        "policy_name": "manual_review_required",
        "default_outcome": "allow",
        "rules": [
            {
                "rule_id": "rule.manual-review",
                "rule_name": "Manual review required",
                "condition": {
                    "field": "proposed_action.action_type",
                    "operator": "equals",
                    "value": "clear_conflict_takeoff_without_separation"
                },
                "outcome": "require_approval"
            }
        ]
    }

    # Ensure we also have a warn policy in the set.
    warn_policy = deepcopy(supply_policy)
    warn_policy["rules"][0]["condition"]["field"] = "proposed_action.parameters.cost_delta_percent"
    warn_policy["rules"][0]["condition"]["value"] = 0
    proposal["proposed_action"]["parameters"]["cost_delta_percent"] = 2

    engine = DeterministicPolicyEngine()
    report = engine.evaluate_policies([warn_policy, approval_policy, air_traffic_policy], proposal)

    assert report.final_outcome == "deny"
    assert report.denied is True
    assert report.requires_approval is True


def test_policy_report_is_durable_and_inspectable(supply_network_scenario_dir):
    policy = load_json(supply_network_scenario_dir / "policy.json")
    proposal = load_json(supply_network_scenario_dir / "proposal.json")

    engine = DeterministicPolicyEngine()
    report = engine.evaluate_policies([policy], proposal)
    serialized = report.as_dict()

    assert serialized["proposal_id"] == proposal["proposal_id"]
    assert serialized["final_outcome"] == "warn"
    assert len(serialized["evaluations"]) >= 1
    assert serialized["evaluations"][0]["policy_id"] == policy["policy_id"]

from pathlib import Path

from jsonschema import Draft202012Validator

from adapters.registry import AdapterRegistry
from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_supply_ops_is_available_in_default_registry():
    adapter = AdapterRegistry.with_defaults().get("adapter-supply-ops")

    assert adapter.domain_name == "supply-ops"
    assert adapter.scenario_dir(REPO_ROOT).name == "supply-ops-mini"


def test_supply_ops_default_policy_matches_example_and_requires_review():
    registry = AdapterRegistry.with_defaults()
    adapter = registry.get("adapter-supply-ops")
    scenario_dir = adapter.scenario_dir(REPO_ROOT)

    default_policy = load_json(adapter.default_policy_path(REPO_ROOT))
    scenario_policy = load_json(scenario_dir / "policy.json")
    proposal = load_json(scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([default_policy], proposal)

    assert scenario_policy == default_policy
    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert {evaluation.outcome for evaluation in report.evaluations} == {"warn", "require_approval"}


def test_supply_ops_scenario_taxonomy_validates_against_adapter_schemas():
    adapter = AdapterRegistry.with_defaults().get("adapter-supply-ops")
    scenario_dir = adapter.scenario_dir(REPO_ROOT)
    schema_paths = {path.name: path for path in adapter.adapter_schema_paths(REPO_ROOT)}

    entities = load_json(scenario_dir / "entities.json")
    events = load_json(scenario_dir / "events.json")
    entity_validator = Draft202012Validator(load_json(schema_paths["entity_types.schema.json"]))
    event_validator = Draft202012Validator(load_json(schema_paths["event_types.schema.json"]))

    for entity in entities:
        assert list(entity_validator.iter_errors(entity)) == []

    for event in events:
        assert list(event_validator.iter_errors(event)) == []

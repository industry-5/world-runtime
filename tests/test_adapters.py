from pathlib import Path

from adapters.registry import AdapterRegistry
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.replay_engine import ReplayEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_default_registry_contains_domain_adapters():
    registry = AdapterRegistry.with_defaults()
    adapter_ids = [adapter.adapter_id for adapter in registry.list()]

    assert "adapter-supply-network" in adapter_ids
    assert "adapter-air-traffic" in adapter_ids
    assert "adapter-world-game" in adapter_ids
    assert len(adapter_ids) == 3


def test_adapter_level_assets_exist():
    registry = AdapterRegistry.with_defaults()

    for adapter in registry.list():
        assert adapter.default_policy_path(REPO_ROOT).exists()
        schema_paths = adapter.adapter_schema_paths(REPO_ROOT)
        assert len(schema_paths) >= 2
        for schema_path in schema_paths:
            assert schema_path.exists()


def test_adapters_validate_their_own_scenario_types():
    registry = AdapterRegistry.with_defaults()

    for adapter in registry.list():
        scenario = adapter.scenario_dir(REPO_ROOT)
        entities = load_json(scenario / "entities.json")
        events = load_json(scenario / "events.json")

        assert adapter.validate_entities(entities) == []
        assert adapter.validate_events(events) == []


def test_adapter_policies_evaluate_without_kernel_changes():
    registry = AdapterRegistry.with_defaults()
    policy_engine = DeterministicPolicyEngine()

    supply_adapter = registry.get("adapter-supply-network")
    air_traffic_adapter = registry.get("adapter-air-traffic")
    world_game_adapter = registry.get("adapter-world-game")

    supply_scenario = supply_adapter.scenario_dir(REPO_ROOT)
    air_traffic_scenario = air_traffic_adapter.scenario_dir(REPO_ROOT)
    supply_policy = load_json(supply_adapter.default_policy_path(REPO_ROOT))
    air_traffic_policy = load_json(air_traffic_adapter.default_policy_path(REPO_ROOT))
    world_game_policy = load_json(world_game_adapter.default_policy_path(REPO_ROOT))

    supply_proposal = load_json(supply_scenario / "proposal.json")
    air_traffic_proposal = load_json(air_traffic_scenario / "proposal.json")
    supply_report = policy_engine.evaluate_policies([supply_policy], supply_proposal)
    air_traffic_report = policy_engine.evaluate_policies([air_traffic_policy], air_traffic_proposal)
    world_game_report = policy_engine.evaluate_policies(
        [world_game_policy],
        {
            "proposal_id": "proposal.world-game-modern.seed",
            "proposed_action": {
                "action_type": "apply_world_game_intervention",
                "parameters": {
                    "projected_composite_score": 40,
                    "projected_water_security_floor": 24,
                    "projected_equity_gap": 20,
                },
            },
        },
    )

    assert supply_report.final_outcome == "warn"
    assert air_traffic_report.final_outcome == "require_approval"
    assert air_traffic_report.requires_approval is True
    assert world_game_report.final_outcome in {"allow", "warn", "require_approval", "deny"}
    assert world_game_report.final_outcome == "warn"


def test_adapter_examples_run_on_shared_kernel():
    registry = AdapterRegistry.with_defaults()

    for adapter in registry.list():
        store = InMemoryEventStore()
        scenario = adapter.scenario_dir(REPO_ROOT)
        events = load_json(scenario / "events.json")

        for index, event in enumerate(events):
            store.append("%s.stream.%d" % (adapter.adapter_id, index), event)

        replay = ReplayEngine(store, SimpleProjector)
        rebuilt = replay.rebuild("world_state", use_snapshot=False)

        assert rebuilt.source_event_offset == len(events) - 1
        assert rebuilt.state["events_processed"] == len(events)

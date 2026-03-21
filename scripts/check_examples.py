from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"
SCENARIOS_DIR = EXAMPLES_DIR / "scenarios"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.world_game.authoring import instantiate_world_game_template_bundle, load_world_game_template_bundle, validate_world_game_template_bundle


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_entity_ids(entities):
    return {e["entity_id"] for e in entities}


def check_supply_network():
    scenario = SCENARIOS_DIR / "supply-network-mini"
    entities = load_json(scenario / "entities.json")
    relationships = load_json(scenario / "relationships.json")
    proposal = load_json(scenario / "proposal.json")
    decision = load_json(scenario / "decision.json")

    entity_ids = collect_entity_ids(entities)

    for rel in relationships:
        assert rel["from_entity"]["entity_id"] in entity_ids
        assert rel["to_entity"]["entity_id"] in entity_ids

    for ref in proposal["target_entities"]:
        assert ref["entity_id"] in entity_ids

    assert decision["selected_proposal_id"] == proposal["proposal_id"]


def check_air_traffic():
    scenario = SCENARIOS_DIR / "air-traffic-mini"
    entities = load_json(scenario / "entities.json")
    relationships = load_json(scenario / "relationships.json")
    proposal = load_json(scenario / "proposal.json")
    conflicting = load_json(scenario / "conflicting_proposals.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    entity_ids = collect_entity_ids(entities)

    for rel in relationships:
        assert rel["from_entity"]["entity_id"] in entity_ids
        assert rel["to_entity"]["entity_id"] in entity_ids

    for ref in proposal["target_entities"]:
        assert ref["entity_id"] in entity_ids

    for candidate in conflicting:
        for ref in candidate["target_entities"]:
            assert ref["entity_id"] in entity_ids

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert simulation["outcomes"]["recommended_proposal_id"] == "proposal.air-traffic.safe.0002"


def check_world_game():
    scenario = SCENARIOS_DIR / "world-game-mini"
    entities = load_json(scenario / "entities.json")
    events = load_json(scenario / "events.json")

    entity_ids = collect_entity_ids(entities)
    assert any(entity["entity_type"] == "wg_region" for entity in entities)
    assert any(entity["entity_type"] == "wg_indicator_definition" for entity in entities)
    assert any(entity["entity_type"] == "wg_policy_instrument" for entity in entities)
    assert any(event["event_type"] == "wg_baseline_loaded" for event in events)
    assert any(event["event_type"] == "wg_goal_declared" for event in events)
    assert any(event["event_type"] == "wg_outcome_projected" for event in events)
    assert len(entity_ids) == len(entities)


def check_world_game_scenario_bundle(name: str):
    scenario_dir = SCENARIOS_DIR / name
    entities = load_json(scenario_dir / "entities.json")
    events = load_json(scenario_dir / "events.json")
    scenario = load_json(scenario_dir / "scenario.json")
    interventions = load_json(scenario_dir / "interventions.json")
    shocks = load_json(scenario_dir / "shocks.json")

    region_ids = {region["region_id"] for region in scenario["regions"]}
    indicator_ids = {indicator["indicator_id"] for indicator in scenario["indicator_definitions"]}
    intervention_ids = {item["intervention_id"] for item in scenario["interventions"]}
    shock_ids = {item["shock_id"] for item in scenario["shocks"]}

    assert any(entity["entity_type"] == "wg_region" for entity in entities)
    assert any(event["event_type"] == "wg_baseline_loaded" for event in events)
    assert any(event["event_type"] == "wg_outcome_projected" for event in events)
    assert set(scenario["baseline_indicators"].keys()) == region_ids

    for region_values in scenario["baseline_indicators"].values():
        assert set(region_values.keys()) == indicator_ids

    for intervention in scenario["interventions"]:
        assert set(intervention["applicable_regions"]).issubset(region_ids)
        for effect in intervention.get("direct_effects", []):
            assert effect["region_id"] in region_ids
            assert effect["indicator_id"] in indicator_ids
        for tradeoff in intervention.get("tradeoffs", []):
            assert tradeoff["region_id"] in region_ids
            assert tradeoff["indicator_id"] in indicator_ids

    for shock in scenario["shocks"]:
        assert set(shock["applicable_regions"]).issubset(region_ids)
        for effect in shock.get("effects", []):
            assert effect["region_id"] in region_ids
            assert effect["indicator_id"] in indicator_ids

    assert set(interventions["interventions"]).issubset(intervention_ids)
    assert set(shocks["shocks"]).issubset(shock_ids)


def check_world_game_authoring_template_bundle(bundle_path: Path):
    bundle = load_json(bundle_path)
    errors = validate_world_game_template_bundle(bundle)
    assert errors == []

    loaded = load_world_game_template_bundle(bundle)
    template_id = loaded["scenario_templates"][0]["template_id"]

    first = instantiate_world_game_template_bundle(
        loaded,
        template_id=template_id,
        parameter_values={
            "region_count": 2,
            "scenario_suffix": "coherence-check-two-region",
        },
    )
    second = instantiate_world_game_template_bundle(
        loaded,
        template_id=template_id,
        parameter_values={
            "region_count": 2,
            "scenario_suffix": "coherence-check-two-region",
        },
    )

    assert first["instantiation_id"] == second["instantiation_id"]
    assert first["scenario"] == second["scenario"]
    assert len(first["scenario"]["regions"]) == 2
    assert first["scenario"]["time_horizon"]["turn_count"] == len(first["scenario"]["shock_schedule"])


def main():
    bundle_paths = sorted((EXAMPLES_DIR / "world-game-authoring").glob("template_bundle*.json"))
    checks = [
        ("supply-network-mini", check_supply_network),
        ("air-traffic-mini", check_air_traffic),
        ("world-game-mini", check_world_game),
        ("world-game-multi-region", lambda: check_world_game_scenario_bundle("world-game-multi-region")),
    ]
    checks.extend(
        [
            ("world-game-authoring-%s" % path.stem, (lambda bundle_path=path: check_world_game_authoring_template_bundle(bundle_path)))
            for path in bundle_paths
        ]
    )

    failed = False

    for name, fn in checks:
        try:
            fn()
            print(f"[OK]   {name}")
        except Exception as e:
            failed = True
            print(f"[FAIL] {name}: {e}")

    if failed:
        sys.exit(1)

    print("\nExample coherence checks passed.")


if __name__ == "__main__":
    main()

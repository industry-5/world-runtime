from conftest import load_json


def collect_entity_ids(entities):
    return {e["entity_id"] for e in entities}


def test_supply_network_entities_are_referenced_coherently(supply_network_scenario_dir):
    entities = load_json(supply_network_scenario_dir / "entities.json")
    relationships = load_json(supply_network_scenario_dir / "relationships.json")
    proposal = load_json(supply_network_scenario_dir / "proposal.json")

    entity_ids = collect_entity_ids(entities)

    for rel in relationships:
        assert rel["from_entity"]["entity_id"] in entity_ids
        assert rel["to_entity"]["entity_id"] in entity_ids

    for ref in proposal["target_entities"]:
        assert ref["entity_id"] in entity_ids


def test_air_traffic_entities_are_referenced_coherently(air_traffic_scenario_dir):
    entities = load_json(air_traffic_scenario_dir / "entities.json")
    relationships = load_json(air_traffic_scenario_dir / "relationships.json")
    proposal = load_json(air_traffic_scenario_dir / "proposal.json")
    conflicting = load_json(air_traffic_scenario_dir / "conflicting_proposals.json")

    entity_ids = collect_entity_ids(entities)

    for rel in relationships:
        assert rel["from_entity"]["entity_id"] in entity_ids
        assert rel["to_entity"]["entity_id"] in entity_ids

    for ref in proposal["target_entities"]:
        assert ref["entity_id"] in entity_ids

    for candidate in conflicting:
        for ref in candidate["target_entities"]:
            assert ref["entity_id"] in entity_ids


def test_supply_network_decision_references_proposal(supply_network_scenario_dir):
    proposal = load_json(supply_network_scenario_dir / "proposal.json")
    decision = load_json(supply_network_scenario_dir / "decision.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]


def test_air_traffic_decision_tracks_constrained_path(air_traffic_scenario_dir):
    proposal = load_json(air_traffic_scenario_dir / "proposal.json")
    decision = load_json(air_traffic_scenario_dir / "decision.json")
    simulation = load_json(air_traffic_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == "proposal.air-traffic.safe.0002"


def test_world_game_multi_region_bundle_is_coherent(world_game_multi_region_scenario_dir):
    entities = load_json(world_game_multi_region_scenario_dir / "entities.json")
    events = load_json(world_game_multi_region_scenario_dir / "events.json")
    scenario = load_json(world_game_multi_region_scenario_dir / "scenario.json")

    region_ids = {region["region_id"] for region in scenario["regions"]}
    indicator_ids = {indicator["indicator_id"] for indicator in scenario["indicator_definitions"]}

    assert any(entity["entity_type"] == "wg_region" for entity in entities)
    assert any(event["event_type"] == "wg_baseline_loaded" for event in events)
    assert any(event["event_type"] == "wg_outcome_projected" for event in events)
    assert set(scenario["baseline_indicators"].keys()) == region_ids
    for intervention in scenario["interventions"]:
        for effect in intervention.get("direct_effects", []):
            assert effect["region_id"] in region_ids
            assert effect["indicator_id"] in indicator_ids

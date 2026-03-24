from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"
SCENARIOS_DIR = EXAMPLES_DIR / "scenarios"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.supply_ops import SupplyOpsExecutionEvidenceBuilder, SupplyOpsTranslator
from adapters.public_program import (
    implemented_public_adapter_tracks,
    validate_standard_public_scenario_bundle,
)
from core.policy_engine import DeterministicPolicyEngine


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_entity_ids(entities):
    return {e["entity_id"] for e in entities}


def load_world_game_authoring_support():
    try:
        from adapters.world_game.authoring import (
            instantiate_world_game_template_bundle,
            load_world_game_template_bundle,
            validate_world_game_template_bundle,
        )
    except ImportError:
        return None

    return {
        "instantiate_world_game_template_bundle": instantiate_world_game_template_bundle,
        "load_world_game_template_bundle": load_world_game_template_bundle,
        "validate_world_game_template_bundle": validate_world_game_template_bundle,
    }


def check_public_scenario_bundle(track):
    errors = validate_standard_public_scenario_bundle(track, REPO_ROOT)
    if errors:
        raise AssertionError("; ".join(errors))


def check_air_traffic_supplemental():
    scenario = SCENARIOS_DIR / "air-traffic-mini"
    proposal = load_json(scenario / "proposal.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert simulation["outcomes"]["recommended_proposal_id"] == "proposal.air-traffic.safe.0002"


def check_supply_network_supplemental():
    scenario = SCENARIOS_DIR / "supply-network-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    options = load_json(scenario / "reroute_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    engine = DeterministicPolicyEngine()
    proposal_report = engine.evaluate_policies([policy], proposal)
    expedite_report = engine.evaluate_policies([policy], options[0])
    defer_report = engine.evaluate_policies([policy], options[1])

    assert proposal_report.final_outcome == "warn"
    assert expedite_report.final_outcome == "warn"
    assert defer_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "warn"
    assert simulation["outcomes"]["recommended_proposal_id"] == proposal["proposal_id"]
    assert simulation["outcomes"]["simulated_output_loss_percent"] < simulation["outcomes"]["baseline_output_loss_percent"]


def check_semantic_system_supplemental():
    scenario = SCENARIOS_DIR / "semantic-system-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "conflicting_proposals.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    unsafe = proposals[0]
    alias_first = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    alias_report = engine.evaluate_policies([policy], alias_first)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert alias_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == alias_first["proposal_id"]


def check_power_grid_supplemental():
    scenario = SCENARIOS_DIR / "power-grid-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "contingency_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    unsafe = proposals[0]
    imports = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    imports_report = engine.evaluate_policies([policy], imports)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert imports_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == imports["proposal_id"]
    assert simulation["outcomes"]["customer_interruptions_avoided"] == 12500


def check_city_ops_supplemental():
    scenario = SCENARIOS_DIR / "city-ops-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "coordination_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    unsafe = proposals[0]
    targeted = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    targeted_report = engine.evaluate_policies([policy], targeted)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert targeted_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == targeted["proposal_id"]
    assert simulation["outcomes"]["hospital_access_maintained"] is True


def check_lab_science_supplemental():
    scenario = SCENARIOS_DIR / "lab-science-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "release_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    unsafe = proposals[0]
    retest = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    retest_report = engine.evaluate_policies([policy], retest)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert retest_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == retest["proposal_id"]
    assert simulation["outcomes"]["projected_data_reliability_score"] == 99


def check_market_micro_supplemental():
    scenario = SCENARIOS_DIR / "market-micro-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "risk_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    unsafe = proposals[0]
    derisk = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    derisk_report = engine.evaluate_policies([policy], derisk)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert derisk_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == derisk["proposal_id"]
    assert simulation["outcomes"]["projected_loss_avoided_bps"] == 17


def check_multiplayer_game_supplemental():
    scenario = SCENARIOS_DIR / "multiplayer-game-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "resolution_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    unsafe = proposals[0]
    serialized = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    serialized_report = engine.evaluate_policies([policy], serialized)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert serialized_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == serialized["proposal_id"]
    assert simulation["outcomes"]["projected_desync_players_avoided"] == 7


def check_autonomous_vehicle_supplemental():
    scenario = SCENARIOS_DIR / "autonomous-vehicle-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "maneuver_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    unsafe = proposals[0]
    yield_first = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    yield_report = engine.evaluate_policies([policy], yield_first)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert yield_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == yield_first["proposal_id"]
    assert simulation["outcomes"]["projected_near_miss_risk_reduction_percent"] == 24


def check_multi_agent_ai_supplemental():
    scenario = SCENARIOS_DIR / "multi-agent-ai-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "branch_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    unsafe = proposals[0]
    reviewed = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    reviewed_report = engine.evaluate_policies([policy], reviewed)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert reviewed_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == reviewed["proposal_id"]
    assert simulation["outcomes"]["projected_review_cycles_avoided"] == 2


def check_open_agent_world_supplemental():
    scenario = SCENARIOS_DIR / "open-agent-world-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "intervention_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")

    unsafe = proposals[0]
    bounded = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    bounded_report = engine.evaluate_policies([policy], bounded)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert bounded_report.final_outcome == "allow"
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == bounded["proposal_id"]
    assert simulation["outcomes"]["projected_conflicts_reduced_percent"] == 31


def check_digital_twin_supplemental():
    scenario = SCENARIOS_DIR / "digital-twin-mini"
    policy = load_json(scenario / "policy.json")
    proposal = load_json(scenario / "proposal.json")
    proposals = load_json(scenario / "overlay_options.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")
    host_bindings = load_json(scenario / "host_bindings.json")

    unsafe = proposals[0]
    power_grid_first = proposals[1]
    engine = DeterministicPolicyEngine()

    proposal_report = engine.evaluate_policies([policy], proposal)
    unsafe_report = engine.evaluate_policies([policy], unsafe)
    power_grid_first_report = engine.evaluate_policies([policy], power_grid_first)

    assert proposal_report.final_outcome == "require_approval"
    assert proposal_report.requires_approval is True
    assert any(e.outcome == "warn" for e in proposal_report.evaluations)
    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert power_grid_first_report.final_outcome == "allow"
    assert power_grid_first_report.requires_approval is False
    assert [binding["host_adapter_id"] for binding in host_bindings] == [
        "adapter-power-grid",
        "adapter-city-ops",
    ]
    assert [binding["proof_sequence"] for binding in host_bindings] == [1, 2]
    assert all(binding["writeback_enabled"] is False for binding in host_bindings)
    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == power_grid_first["proposal_id"]
    assert simulation["outcomes"]["projected_cross_host_alerts_suppressed"] == 4


def check_supply_ops():
    scenario = SCENARIOS_DIR / "supply-ops-mini"
    entities = load_json(scenario / "entities.json")
    relationships = load_json(scenario / "relationships.json")
    proposal = load_json(scenario / "proposal.json")
    decision = load_json(scenario / "decision.json")
    simulation = load_json(scenario / "simulation.json")
    execution_evidence = load_json(scenario / "execution_evidence.json")

    entity_ids = collect_entity_ids(entities)

    for rel in relationships:
        assert rel["from_entity"]["entity_id"] in entity_ids
        assert rel["to_entity"]["entity_id"] in entity_ids

    for ref in proposal["target_entities"]:
        assert ref["entity_id"] in entity_ids

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == proposal["proposal_id"]
    assert execution_evidence["selected_proposal_id"] == proposal["proposal_id"]
    assert execution_evidence["decision_id"] == decision["decision_id"]
    assert execution_evidence["simulation"]["simulation_id"] == simulation["simulation_id"]

    translator = SupplyOpsTranslator()
    ingress_envelope = translator.load_ingress_envelope_fixture(
        REPO_ROOT, "require_approval_high_expedite"
    )
    translated = translator.translate_ingress_envelope(ingress_envelope)
    policy = load_json(
        REPO_ROOT / "adapters" / "supply_ops" / "policies" / "default_policy.json"
    )
    report = DeterministicPolicyEngine().evaluate_policies([policy], translated)
    built_evidence = SupplyOpsExecutionEvidenceBuilder().build(
        ingress_envelope, translated, report, decision
    )

    assert translated == proposal
    assert built_evidence == execution_evidence


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
    support = load_world_game_authoring_support()
    if support is None:
        raise RuntimeError("world_game authoring support is not available")

    bundle = load_json(bundle_path)
    errors = support["validate_world_game_template_bundle"](bundle)
    assert errors == []

    loaded = support["load_world_game_template_bundle"](bundle)
    template_id = loaded["scenario_templates"][0]["template_id"]

    first = support["instantiate_world_game_template_bundle"](
        loaded,
        template_id=template_id,
        parameter_values={
            "region_count": 2,
            "scenario_suffix": "coherence-check-two-region",
        },
    )
    second = support["instantiate_world_game_template_bundle"](
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
    bundle_dir = EXAMPLES_DIR / "world-game-authoring"
    bundle_paths = sorted(bundle_dir.glob("template_bundle*.json")) if bundle_dir.exists() else []
    checks = [
        (
            track.scenario_slug,
            (lambda discovered_track=track: check_public_scenario_bundle(discovered_track)),
        )
        for track in implemented_public_adapter_tracks()
    ]
    checks.extend(
        [
            ("air-traffic-mini/supplemental", check_air_traffic_supplemental),
            ("supply-network-mini/supplemental", check_supply_network_supplemental),
            ("semantic-system-mini/supplemental", check_semantic_system_supplemental),
            ("power-grid-mini/supplemental", check_power_grid_supplemental),
            ("city-ops-mini/supplemental", check_city_ops_supplemental),
            ("lab-science-mini/supplemental", check_lab_science_supplemental),
            ("market-micro-mini/supplemental", check_market_micro_supplemental),
            ("multiplayer-game-mini/supplemental", check_multiplayer_game_supplemental),
            ("autonomous-vehicle-mini/supplemental", check_autonomous_vehicle_supplemental),
            ("multi-agent-ai-mini/supplemental", check_multi_agent_ai_supplemental),
            ("open-agent-world-mini/supplemental", check_open_agent_world_supplemental),
            ("digital-twin-mini/supplemental", check_digital_twin_supplemental),
            ("supply-ops-mini", check_supply_ops),
        ]
    )
    if (SCENARIOS_DIR / "world-game-mini").exists():
        checks.append(("world-game-mini", check_world_game))
    if (SCENARIOS_DIR / "world-game-multi-region").exists():
        checks.append(("world-game-multi-region", lambda: check_world_game_scenario_bundle("world-game-multi-region")))
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

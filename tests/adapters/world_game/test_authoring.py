from copy import deepcopy
from pathlib import Path

import pytest

from adapters.world_game.authoring import (
    instantiate_world_game_template_bundle,
    load_world_game_template_bundle,
    validate_world_game_template_bundle,
)
from adapters.world_game.runtime import initialize_baseline_state, run_turn
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[3]
BUNDLE_PATH = REPO_ROOT / "examples" / "world-game-authoring" / "template_bundle.multi-region.v1.json"
TEMPLATE_PACK_DIR = REPO_ROOT / "examples" / "world-game-authoring"
BUNDLE_PATHS = sorted(TEMPLATE_PACK_DIR.glob("template_bundle*.json"))


def test_template_bundle_schema_validation_passes_for_examples():
    assert BUNDLE_PATHS
    for bundle_path in BUNDLE_PATHS:
        bundle = load_json(bundle_path)

        errors = validate_world_game_template_bundle(bundle)
        assert errors == []


def test_template_bundle_hash_is_verified_on_load_for_examples():
    for bundle_path in BUNDLE_PATHS:
        bundle = load_json(bundle_path)

        loaded = load_world_game_template_bundle(bundle)
        assert loaded["bundle_metadata"]["deterministic_version_hash"].startswith("sha256:")


def test_template_bundle_instantiation_is_deterministic():
    bundle = load_world_game_template_bundle(BUNDLE_PATH)
    template_id = bundle["scenario_templates"][0]["template_id"]
    parameters = {
        "region_count": 2,
        "scenario_suffix": "deterministic-two-region",
        "policy_pack_ref": "adapters/world_game/policies/world_game_policy_pack.json",
    }

    first = instantiate_world_game_template_bundle(bundle, template_id=template_id, parameter_values=parameters)
    second = instantiate_world_game_template_bundle(bundle, template_id=template_id, parameter_values=parameters)

    assert first["instantiation_id"] == second["instantiation_id"]
    assert first["scenario"] == second["scenario"]
    assert len(first["scenario"]["regions"]) == 2
    assert first["scenario"]["policy_pack_ref"] == "adapters/world_game/policies/world_game_policy_pack.json"


def test_wg_m10_template_packs_are_available_and_reusable():
    expected_bundle_ids = {
        "wg.authoring.bundle.few-advanced-baseline.v1",
        "wg.authoring.bundle.multi-region-stress.v1",
        "wg.authoring.bundle.resilience-first-regional-planning.v1",
    }
    discovered_bundle_ids = set()
    for bundle_path in BUNDLE_PATHS:
        loaded = load_world_game_template_bundle(bundle_path)
        discovered_bundle_ids.add(loaded["bundle_metadata"]["bundle_id"])

        template = loaded["scenario_templates"][0]
        template_id = template["template_id"]
        for registry in loaded["indicator_registries"]:
            scenario = instantiate_world_game_template_bundle(
                loaded,
                template_id=template_id,
                parameter_values={
                    "region_count": 2,
                    "scenario_suffix": "m10-reuse-check",
                    "indicator_registry_ref": registry["registry_id"],
                },
            )["scenario"]
            assert len(scenario["regions"]) == 2
            assert scenario["indicator_definitions"]

    assert expected_bundle_ids.issubset(discovered_bundle_ids)


def test_instantiated_scenario_remains_runtime_compatible():
    bundle = load_world_game_template_bundle(BUNDLE_PATH)
    template_id = bundle["scenario_templates"][0]["template_id"]
    instantiated = instantiate_world_game_template_bundle(
        bundle,
        template_id=template_id,
        parameter_values={"scenario_suffix": "runtime-compatible"},
    )

    scenario = instantiated["scenario"]
    state = initialize_baseline_state(scenario, branch_id="baseline")

    intervention_id = scenario["interventions"][0]["intervention_id"]
    shock_id = scenario["shocks"][0]["shock_id"]
    executed = run_turn(
        state=state,
        scenario=scenario,
        intervention_ids=[intervention_id],
        shock_ids=[shock_id],
        policy_evaluator=None,
        policies=None,
        approval_status="approved",
    )

    assert executed["turn_result"]["committed"] is True
    assert executed["state"]["turn"] == 1


def test_template_bundle_validation_errors_are_path_specific():
    invalid_bundle = deepcopy(load_json(BUNDLE_PATH))
    invalid_bundle["scenario_templates"][0].pop("template_id", None)

    errors = validate_world_game_template_bundle(invalid_bundle)

    assert errors
    assert errors[0]["path"].startswith("$.scenario_templates[0]")


def test_template_bundle_hash_mismatch_raises_explicit_error():
    invalid_bundle = deepcopy(load_json(BUNDLE_PATH))
    invalid_bundle["bundle_metadata"]["deterministic_version_hash"] = (
        "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    )

    with pytest.raises(ValueError, match="deterministic_version_hash mismatch"):
        load_world_game_template_bundle(invalid_bundle)

from pathlib import Path

import pytest

from adapters.supply_ops import SupplyOpsTranslator
from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "adapters" / "supply_ops" / "fixtures"
EXPECTED_OUTCOMES = {
    "allow_recovery": "allow",
    "warn_low_inventory_cover": "warn",
    "require_approval_high_expedite": "require_approval",
    "deny_low_fill_rate": "deny",
}


@pytest.mark.parametrize("fixture_name", list(EXPECTED_OUTCOMES))
def test_supply_ops_translator_matches_expected_fixture_outputs(fixture_name):
    translator = SupplyOpsTranslator()
    translated = translator.translate_fixture_bundle(REPO_ROOT, fixture_name)
    expected = load_json(FIXTURES_DIR / "translated" / f"{fixture_name}.json")

    assert translated == expected


def test_supply_ops_translator_matches_m1_example_for_reviewed_recovery_flow(
    supply_ops_scenario_dir,
):
    translator = SupplyOpsTranslator()

    translated = translator.translate_fixture_bundle(
        REPO_ROOT, "require_approval_high_expedite"
    )

    assert translated == load_json(supply_ops_scenario_dir / "proposal.json")


@pytest.mark.parametrize("fixture_name", list(EXPECTED_OUTCOMES))
def test_supply_ops_translator_stays_proposal_only(fixture_name):
    translator = SupplyOpsTranslator()
    translated = translator.translate_fixture_bundle(REPO_ROOT, fixture_name)

    assert set(translated.keys()) == {
        "proposal_id",
        "proposal_type",
        "status",
        "proposer",
        "target_entities",
        "proposed_action",
        "justification",
        "created_at",
    }
    assert "decision_id" not in translated
    assert "events" not in translated
    assert "projection" not in translated


@pytest.mark.parametrize(
    ("fixture_name", "expected_outcome"),
    list(EXPECTED_OUTCOMES.items()),
)
def test_supply_ops_default_policy_covers_all_outcome_classes(
    fixture_name, expected_outcome
):
    translator = SupplyOpsTranslator()
    proposal = translator.translate_fixture_bundle(REPO_ROOT, fixture_name)
    default_policy = load_json(
        REPO_ROOT / "adapters" / "supply_ops" / "policies" / "default_policy.json"
    )

    report = DeterministicPolicyEngine().evaluate_policies([default_policy], proposal)

    assert report.final_outcome == expected_outcome
    assert report.denied is (expected_outcome == "deny")
    assert report.requires_approval is (expected_outcome == "require_approval")

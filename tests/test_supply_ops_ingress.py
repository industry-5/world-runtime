from copy import deepcopy
from pathlib import Path

import pytest

from adapters.supply_ops import SupplyOpsIngressPreparer, SupplyOpsTranslator
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "adapters" / "supply_ops" / "fixtures"
FIXTURE_NAMES = [
    "allow_recovery",
    "warn_low_inventory_cover",
    "require_approval_high_expedite",
    "deny_low_fill_rate",
]


@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_supply_ops_ingress_fixtures_translate_to_existing_golden_proposals(fixture_name):
    translator = SupplyOpsTranslator()
    translated = translator.translate_ingress_fixture(REPO_ROOT, fixture_name)
    expected = load_json(FIXTURES_DIR / "translated" / f"{fixture_name}.json")

    assert translated == expected


def test_supply_ops_ingress_metadata_stays_connector_shaped_but_translation_only():
    envelope = SupplyOpsIngressPreparer().load_fixture_envelope(
        REPO_ROOT, "require_approval_high_expedite"
    )
    metadata = SupplyOpsIngressPreparer().extract_metadata(envelope)

    assert metadata["connector_id"] == "connector.supply-ops.erp-wms-ingress"
    assert metadata["direction"] == "inbound"
    assert metadata["governance"] == {
        "translation_required": True,
        "mutates_runtime_state": False,
        "translation_boundary": "proposal_only",
    }


def test_supply_ops_ingress_rejects_direct_state_mutation_flags():
    envelope = deepcopy(
        SupplyOpsIngressPreparer().load_fixture_envelope(
            REPO_ROOT, "require_approval_high_expedite"
        )
    )
    envelope["governance"]["mutates_runtime_state"] = True

    with pytest.raises(
        ValueError, match="governance.mutates_runtime_state must be false"
    ):
        SupplyOpsTranslator().translate_ingress_envelope(envelope)


def test_supply_ops_ingress_requires_inbound_direction():
    envelope = deepcopy(
        SupplyOpsIngressPreparer().load_fixture_envelope(
            REPO_ROOT, "require_approval_high_expedite"
        )
    )
    envelope["connector"]["direction"] = "outbound"

    with pytest.raises(ValueError, match="connector.direction must be 'inbound'"):
        SupplyOpsTranslator().translate_ingress_envelope(envelope)

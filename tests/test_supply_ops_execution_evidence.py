from copy import deepcopy
from pathlib import Path

import pytest

from adapters.supply_ops import SupplyOpsExecutionEvidenceBuilder, SupplyOpsTranslator
from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_supply_ops_execution_evidence_matches_reviewed_example(
    supply_ops_scenario_dir,
):
    translator = SupplyOpsTranslator()
    proposal = translator.translate_ingress_fixture(
        REPO_ROOT, "require_approval_high_expedite"
    )
    ingress_envelope = translator.load_ingress_envelope_fixture(
        REPO_ROOT, "require_approval_high_expedite"
    )
    default_policy = load_json(
        REPO_ROOT / "adapters" / "supply_ops" / "policies" / "default_policy.json"
    )
    decision = load_json(supply_ops_scenario_dir / "decision.json")
    expected = load_json(supply_ops_scenario_dir / "execution_evidence.json")

    report = DeterministicPolicyEngine().evaluate_policies([default_policy], proposal)
    evidence = SupplyOpsExecutionEvidenceBuilder().build(
        ingress_envelope, proposal, report, decision
    )

    assert evidence == expected


def test_supply_ops_execution_evidence_requires_approved_decision(
    supply_ops_scenario_dir,
):
    translator = SupplyOpsTranslator()
    proposal = translator.translate_ingress_fixture(
        REPO_ROOT, "require_approval_high_expedite"
    )
    ingress_envelope = translator.load_ingress_envelope_fixture(
        REPO_ROOT, "require_approval_high_expedite"
    )
    default_policy = load_json(
        REPO_ROOT / "adapters" / "supply_ops" / "policies" / "default_policy.json"
    )
    decision = deepcopy(load_json(supply_ops_scenario_dir / "decision.json"))
    decision["status"] = "rejected"
    report = DeterministicPolicyEngine().evaluate_policies([default_policy], proposal)

    with pytest.raises(ValueError, match="decision.status must be approved"):
        SupplyOpsExecutionEvidenceBuilder().build(
            ingress_envelope, proposal, report, decision
        )

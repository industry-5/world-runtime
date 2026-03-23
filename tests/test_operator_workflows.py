from pathlib import Path

import pytest

from adapters.registry import AdapterRegistry
from core.operator_workflows import OperatorWorkflowRunner


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_quickstart_workflow_runs_without_internal_changes():
    runner = OperatorWorkflowRunner(REPO_ROOT)
    result = runner.run_quickstart(adapter_id="adapter-supply-network")

    assert result["workflow"] == "quickstart"
    assert result["reasoning"]["query_type"] in {"summary", "shipment_delay", "incident_summary"}
    assert result["proposal"]["status"] == "draft"
    assert len(result["events"]) >= 3
    assert result["diagnostics"]["cards"]["events"] >= 1


def test_failure_recovery_workflow_returns_recommendation():
    runner = OperatorWorkflowRunner(REPO_ROOT)
    result = runner.run_failure_recovery(adapter_id="adapter-supply-network")

    assert result["workflow"] == "failure-recovery"
    assert result["simulation"]["status"] == "completed"
    assert result["recommendation"]["action"] == "reroute_shipment"
    assert len(result["recommendation"]["changed_paths"]) >= 1
    assert result["diagnostics"]["cards"]["traces"] >= 1


def test_proposal_review_workflow_produces_decision_record():
    runner = OperatorWorkflowRunner(REPO_ROOT)
    result = runner.run_proposal_review(adapter_id="adapter-supply-network", auto_approve=True)

    assert result["workflow"] == "proposal-review"
    assert result["decision"]["decision_id"].startswith("decision.")
    assert result["decision"]["selected_proposal_id"] is not None
    assert result["decision"]["status"] in {"approved", "rejected"}
    assert result["diagnostics"]["cards"]["events"] >= 1


def test_simulation_analysis_workflow_returns_changed_paths():
    runner = OperatorWorkflowRunner(REPO_ROOT)
    result = runner.run_simulation_analysis(adapter_id="adapter-supply-network")

    assert result["workflow"] == "simulation-analysis"
    assert result["analysis"]["status"] == "completed"
    assert result["analysis"]["changed_path_count"] >= 1
    assert result["diagnostics"]["cards"]["events"] >= 1


def test_quickstart_supports_air_traffic_adapter():
    runner = OperatorWorkflowRunner(REPO_ROOT)
    result = runner.run_quickstart(adapter_id="adapter-air-traffic")

    assert result["workflow"] == "quickstart"
    assert result["adapter_id"] == "adapter-air-traffic"
    assert result["scenario"].endswith("examples/scenarios/air-traffic-mini")


def test_quickstart_supports_world_game_adapter():
    if AdapterRegistry.with_defaults().maybe_get("adapter-world-game") is None:
        pytest.skip("world_game adapter not present in this repo build")

    runner = OperatorWorkflowRunner(REPO_ROOT)
    result = runner.run_quickstart(adapter_id="adapter-world-game")
    expected_scenario = str(runner.registry.get("adapter-world-game").scenario_dir(REPO_ROOT))

    assert result["workflow"] == "quickstart"
    assert result["adapter_id"] == "adapter-world-game"
    assert result["scenario"] == expected_scenario

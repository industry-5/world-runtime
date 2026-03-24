from pathlib import Path

from core.deployment import DeploymentLoader


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_local_profile_loads_and_has_required_configs():
    loader = DeploymentLoader(REPO_ROOT)
    profile = loader.load_profile("local")

    assert profile.profile_id == "profile.local"
    assert profile.environment == "local"
    assert profile.persistence_config.exists()
    assert profile.llm_config.exists()
    assert "adapter-supply-network" in profile.adapters


def test_dev_profile_loads_and_has_required_configs():
    loader = DeploymentLoader(REPO_ROOT)
    profile = loader.load_profile("dev")

    assert profile.profile_id == "profile.dev"
    assert profile.environment == "dev"
    assert profile.persistence_config.exists()
    assert profile.llm_config.exists()
    assert "adapter-air-traffic" in profile.adapters


def test_local_deployment_smoke_check_runs():
    loader = DeploymentLoader(REPO_ROOT)
    result = loader.smoke_check("local")

    assert result["environment"] == "local"
    assert result["task_status"] == "completed"
    assert result["query_type"] == "shipment_delay"
    assert result["eval_status"] == "passed"
    assert result["pass_rate"] == 1.0
    assert result["diagnostics"]["cards"]["events"] >= 1


def test_dev_deployment_smoke_check_runs():
    loader = DeploymentLoader(REPO_ROOT)
    result = loader.smoke_check("dev")

    assert result["environment"] == "dev"
    assert result["task_status"] == "completed"
    assert result["eval_status"] == "passed"
    assert result["events_loaded"] >= 2
    assert result["diagnostics"]["cards"]["traces"] >= 1


def test_reference_adapter_deployments_exist():
    supply = REPO_ROOT / "infra" / "deployments" / "supply-network.local.json"

    assert supply.exists()

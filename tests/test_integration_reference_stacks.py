from pathlib import Path

from core.integration_stacks import IntegrationStackLoader


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_integration_stack_manifests_exist():
    stack_dir = REPO_ROOT / "infra" / "integration_stacks"
    assert stack_dir.exists()
    assert (stack_dir / "supply-network.erp-sync.local.json").exists()
    assert (stack_dir / "local_ai_structured_extraction.json").exists()


def test_integration_stack_manifests_validate():
    loader = IntegrationStackLoader(REPO_ROOT)

    stack_names = loader.list_stack_names()
    assert len(stack_names) >= 1

    for stack_name in stack_names:
        stack = loader.load_stack(stack_name)
        assert loader.validate_stack(stack) == []


def test_integration_stack_smoke_checks_run_without_evals():
    loader = IntegrationStackLoader(REPO_ROOT)

    for stack_name in loader.list_stack_names():
        result = loader.smoke_check(stack_name, run_eval=False)
        assert result["task_status"] == "completed"
        assert result["eval_status"] == "not_run"

        if result.get("stack_kind") == "local_ai_structured_extraction":
            assert result["managed_services"] >= 1
            assert result["providers"] >= 2
            assert result["task_profiles"] >= 1
            assert result["preferred_provider_id"] == "reference-local-structured-extraction-high"
            assert result["fallback_provider_id"] == "reference-local-structured-extraction-balanced"
            assert result["diagnostics_status"] == "passed"
            continue

        assert result["ingress_mappings"] >= 1
        assert result["egress_mappings"] >= 1
        assert result["events_loaded"] >= 2
        assert result["connector_results"]["inbound"] == "completed"
        assert result["connector_results"]["outbound"] == "completed"
        assert result["connector_results"]["inbound_duplicate_status"] == "duplicate"
        assert result["connector_results"]["outbound_duplicate_status"] == "duplicate"
        assert result["connector_results"]["dead_letters"] == 0


def test_integration_stack_retry_policy_validation():
    loader = IntegrationStackLoader(REPO_ROOT)
    stack = loader.load_stack("supply-network.erp-sync.local")
    stack.ingress["retry"] = {"max_attempts": 0}

    errors = loader.validate_stack(stack)
    assert "ingress.retry.max_attempts must be an integer >= 1" in errors

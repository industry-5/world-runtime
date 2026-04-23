from pathlib import Path

from core.provider_registry import ProviderRegistryLoader
from core.routing_policy import RoutingPolicyInput
from core.task_profiles import TaskProfileLoader
from core.task_router import TaskRouter


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_provider_and_task_catalogs_load_reference_inventory():
    provider_registry = ProviderRegistryLoader(REPO_ROOT).load_all()
    task_catalog = TaskProfileLoader(REPO_ROOT).load_all()

    assert provider_registry.list_provider_ids() == [
        "reference-local-chat-economy",
        "reference-local-structured-balanced",
        "reference-local-structured-extraction-balanced",
        "reference-local-structured-extraction-high",
        "reference-network-structured-premium",
    ]
    assert task_catalog.list_profile_ids() == [
        "assistant-chat.default",
        "structured-extraction.local-reference",
        "structured-extraction.strict",
    ]


def test_task_router_selects_local_structured_provider_with_bounded_fallback():
    provider_registry = ProviderRegistryLoader(REPO_ROOT).load_all()
    task_catalog = TaskProfileLoader(REPO_ROOT).load_all()
    router = TaskRouter(provider_registry, task_catalog)

    decision = router.route(
        "structured-extraction.strict",
        service_states={"reference-http": {"lifecycle_state": "ready"}},
    )

    assert decision.status == "selected"
    assert decision.selected_provider_id == "reference-local-structured-balanced"
    assert decision.selected_stage == "fallback"
    assert decision.fallback.invoked is True

    remote_candidate = next(
        candidate for candidate in decision.candidates if candidate.provider_id == "reference-network-structured-premium"
    )
    assert remote_candidate.status == "rejected"
    assert "missing required policy scope tags" in " ".join(remote_candidate.reasons)


def test_task_router_returns_no_route_when_managed_dependency_is_not_ready():
    provider_registry = ProviderRegistryLoader(REPO_ROOT).load_all()
    task_catalog = TaskProfileLoader(REPO_ROOT).load_all()
    router = TaskRouter(provider_registry, task_catalog)

    decision = router.route(
        "structured-extraction.strict",
        service_states={"reference-http": {"lifecycle_state": "failed"}},
    )

    assert decision.status == "no_route"
    assert decision.selected_provider_id is None
    assert decision.fallback.invoked is True

    local_candidate = next(
        candidate for candidate in decision.candidates if candidate.provider_id == "reference-local-structured-balanced"
    )
    assert local_candidate.status == "rejected"
    assert "service dependencies not ready" in " ".join(local_candidate.reasons)


def test_task_router_selects_local_reference_primary_and_bounded_fallback():
    provider_registry = ProviderRegistryLoader(REPO_ROOT).load_all()
    task_catalog = TaskProfileLoader(REPO_ROOT).load_all()
    router = TaskRouter(provider_registry, task_catalog)

    preferred = router.route(
        "structured-extraction.local-reference",
        service_states={"reference-local-ai-extraction": {"lifecycle_state": "ready"}},
    )
    assert preferred.status == "selected"
    assert preferred.selected_provider_id == "reference-local-structured-extraction-high"
    assert preferred.selected_stage == "preferred"
    assert preferred.fallback.invoked is False

    fallback = router.route(
        "structured-extraction.local-reference",
        service_states={"reference-local-ai-extraction": {"lifecycle_state": "ready"}},
        policy_input=RoutingPolicyInput.from_dict(
            {"denied_provider_ids": ["reference-local-structured-extraction-high"]}
        ),
    )
    assert fallback.status == "selected"
    assert fallback.selected_provider_id == "reference-local-structured-extraction-balanced"
    assert fallback.selected_stage == "fallback"
    assert fallback.fallback.invoked is True

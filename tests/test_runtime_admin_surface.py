from api.runtime_api import PublicRuntimeAPI
from api.runtime_factory import build_server_from_examples


RUNTIME_ADMIN_ACTOR = {
    "actor_id": "human.runtime-admin-01",
    "actor_type": "human",
    "roles": ["operator"],
    "capabilities": ["runtime.service.reconcile"],
}


def test_app_server_runtime_admin_surfaces_cover_inventory_reconcile_and_audit(examples_dir):
    server = build_server_from_examples(examples_dir)

    try:
        inventory = server.handle_request("runtime.inventory.summary")
        assert inventory["ok"] is True
        assert inventory["result"]["services"]["count"] >= 2
        assert inventory["result"]["providers"]["count"] >= 3
        assert inventory["result"]["task_profiles"]["count"] >= 2

        listed_services = server.handle_request("runtime.service.list")
        assert listed_services["ok"] is True
        service_ids = {item["service_id"] for item in listed_services["result"]["services"]}
        assert "reference-http" in service_ids

        provider = server.handle_request(
            "runtime.provider.get",
            {"provider_id": "reference-local-structured-balanced"},
        )
        assert provider["ok"] is True
        assert provider["result"]["provider"]["provider_id"] == "reference-local-structured-balanced"

        session_id = server.session_create()["session_id"]
        reconciled = server.handle_request(
            "runtime.service.reconcile",
            {
                "session_id": session_id,
                "service_ids": ["reference-http"],
                "actor": RUNTIME_ADMIN_ACTOR,
            },
        )
        assert reconciled["ok"] is True
        assert reconciled["result"]["services"][0]["service_id"] == "reference-http"
        assert reconciled["result"]["services"][0]["lifecycle_state"] == "ready"
        assert reconciled["result"]["decision"]["selected_action"]["action_type"] == "runtime_service_reconcile"

        resolved = server.handle_request(
            "runtime.task.resolve",
            {"task_profile_id": "structured-extraction.strict"},
        )
        assert resolved["ok"] is True
        assert (
            resolved["result"]["decision"]["selected_provider_id"]
            == "reference-local-structured-balanced"
        )

        audit = server.handle_request("audit.export", {"session_id": session_id})
        assert audit["ok"] is True
        decision_actions = {
            item["selected_action"]["action_type"]
            for item in audit["result"]["artifacts"]["decisions"]
        }
        assert "runtime_service_reconcile" in decision_actions

        telemetry = server.handle_request("telemetry.events", {"component": "runtime_admin", "limit": 20})
        assert telemetry["ok"] is True
        event_types = {item["event_type"] for item in telemetry["result"]["events"]}
        assert "runtime_admin.reconcile.requested" in event_types
        assert "runtime_admin.reconcile.completed" in event_types
    finally:
        server.runtime_admin.close()


def test_public_runtime_api_runtime_admin_methods(examples_dir):
    runtime_api = PublicRuntimeAPI(build_server_from_examples(examples_dir))

    try:
        inventory = runtime_api.runtime_inventory()
        assert inventory["providers"]["count"] >= 3

        services = runtime_api.list_runtime_services()
        assert services["count"] >= 2

        reference_service = runtime_api.get_runtime_service("reference-http")
        assert reference_service["service"]["service_id"] == "reference-http"

        providers = runtime_api.list_runtime_providers()
        assert providers["count"] >= 3

        provider = runtime_api.get_runtime_provider("reference-local-chat-economy")
        assert provider["provider"]["provider_id"] == "reference-local-chat-economy"

        session = runtime_api.create_session()
        reconciled = runtime_api.reconcile_runtime_services(
            actor=RUNTIME_ADMIN_ACTOR,
            service_ids=["reference-http"],
            session_id=session["session_id"],
        )
        assert reconciled["services"][0]["lifecycle_state"] == "ready"

        resolved = runtime_api.resolve_runtime_task(
            task_profile_id="structured-extraction.strict",
        )
        assert resolved["decision"]["selected_provider_id"] == "reference-local-structured-balanced"
    finally:
        runtime_api.app_server.runtime_admin.close()

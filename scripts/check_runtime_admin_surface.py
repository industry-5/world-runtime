import argparse
import json
import socket
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import request

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from api.http_server import build_http_server
from api.runtime_api import PublicRuntimeAPI
from api.runtime_factory import build_server_from_examples
from world_runtime.sdk import WorldRuntimeSDKClient


DEFAULT_OUTPUT = REPO_ROOT / "tmp" / "diagnostics" / "m29_runtime_admin.latest.json"
RUNTIME_ADMIN_ACTOR = {
    "actor_id": "human.runtime-admin-smoke",
    "actor_type": "human",
    "roles": ["operator"],
    "capabilities": ["runtime.service.reconcile"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _http_get_json(url: str) -> dict:
    with request.urlopen(url, timeout=10.0) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def _http_post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with request.urlopen(req, timeout=10.0) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run M29 runtime-admin surface validation")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started_at = utc_now()
    errors: list[str] = []
    scenarios: dict[str, dict] = {}
    port = _free_port()
    base_url = "http://127.0.0.1:%s" % port

    app_server = build_server_from_examples(REPO_ROOT / "examples")
    runtime_api = PublicRuntimeAPI(app_server)
    http_server = build_http_server("127.0.0.1", port, runtime_api)
    http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    http_thread.start()
    time.sleep(0.2)

    try:
        session_id = app_server.session_create()["session_id"]

        scenarios["app_server_inventory"] = app_server.handle_request("runtime.inventory.summary")
        scenarios["app_server_services"] = app_server.handle_request("runtime.service.list")
        scenarios["app_server_provider"] = app_server.handle_request(
            "runtime.provider.get",
            {"provider_id": "reference-local-structured-balanced"},
        )
        scenarios["app_server_reconcile"] = app_server.handle_request(
            "runtime.service.reconcile",
            {
                "session_id": session_id,
                "service_ids": ["reference-http"],
                "actor": RUNTIME_ADMIN_ACTOR,
            },
        )
        scenarios["app_server_resolve"] = app_server.handle_request(
            "runtime.task.resolve",
            {"task_profile_id": "structured-extraction.strict"},
        )
        scenarios["app_server_audit"] = app_server.handle_request(
            "audit.export",
            {"session_id": session_id},
        )

        scenarios["public_api_inventory"] = _http_get_json(base_url + "/v1/runtime/inventory")
        scenarios["public_api_services"] = _http_get_json(base_url + "/v1/runtime/services")
        scenarios["public_api_service_get"] = _http_get_json(
            base_url + "/v1/runtime/services/reference-http"
        )
        scenarios["public_api_providers"] = _http_get_json(base_url + "/v1/runtime/providers")
        scenarios["public_api_provider_get"] = _http_get_json(
            base_url + "/v1/runtime/providers/reference-local-chat-economy"
        )
        scenarios["public_api_resolve"] = _http_post_json(
            base_url + "/v1/runtime/tasks/resolve",
            {"task_profile_id": "structured-extraction.strict"},
        )
        scenarios["public_api_reconcile"] = _http_post_json(
            base_url + "/v1/runtime/services/reconcile",
            {
                "session_id": session_id,
                "service_ids": ["reference-http"],
                "actor": RUNTIME_ADMIN_ACTOR,
            },
        )

        sdk = WorldRuntimeSDKClient(base_url=base_url)
        scenarios["sdk_inventory"] = sdk.runtime_inventory()
        scenarios["sdk_services"] = sdk.list_runtime_services()
        scenarios["sdk_service_get"] = sdk.get_runtime_service("reference-http")
        scenarios["sdk_providers"] = sdk.list_runtime_providers()
        scenarios["sdk_provider_get"] = sdk.get_runtime_provider("reference-local-chat-economy")
        scenarios["sdk_resolve"] = sdk.resolve_runtime_task(
            task_profile_id="structured-extraction.strict"
        )
        scenarios["sdk_reconcile"] = sdk.reconcile_runtime_services(
            actor=RUNTIME_ADMIN_ACTOR,
            service_ids=["reference-http"],
            session_id=session_id,
        )
    except Exception as exc:  # pragma: no cover - exercised in smoke runs
        errors.append(str(exc))
    finally:
        http_server.shutdown()
        http_server.server_close()
        http_thread.join(timeout=5.0)
        app_server.runtime_admin.close()

    inventory = scenarios.get("app_server_inventory", {})
    if inventory.get("ok") is not True:
        errors.append("App Server runtime inventory call failed")
    elif inventory["result"]["providers"]["count"] < 3:
        errors.append("runtime inventory did not expose the expected provider count")

    reconcile = scenarios.get("app_server_reconcile", {})
    if reconcile.get("ok") is not True:
        errors.append("App Server reconcile call failed")
    elif reconcile["result"]["services"][0].get("lifecycle_state") != "ready":
        errors.append("App Server reconcile did not drive reference-http to ready")

    resolved = scenarios.get("app_server_resolve", {})
    if resolved.get("ok") is not True:
        errors.append("App Server task resolve call failed")
    elif (
        resolved["result"]["decision"].get("selected_provider_id")
        != "reference-local-structured-balanced"
    ):
        errors.append("App Server task resolution did not select the expected provider")

    audit = scenarios.get("app_server_audit", {})
    if audit.get("ok") is not True:
        errors.append("Audit export failed after runtime-admin reconcile")
    else:
        decision_actions = {
            item.get("selected_action", {}).get("action_type")
            for item in audit["result"]["artifacts"]["decisions"]
        }
        if "runtime_service_reconcile" not in decision_actions:
            errors.append("runtime-admin reconcile decision was not captured in audit export")

    public_api_inventory = scenarios.get("public_api_inventory", {})
    if public_api_inventory.get("ok") is not True:
        errors.append("Public API inventory endpoint failed")

    public_api_resolve = scenarios.get("public_api_resolve", {})
    if (
        public_api_resolve.get("result", {}).get("decision", {}).get("selected_provider_id")
        != "reference-local-structured-balanced"
    ):
        errors.append("Public API runtime task resolve endpoint did not select the expected provider")

    sdk_resolve = scenarios.get("sdk_resolve", {})
    if sdk_resolve.get("decision", {}).get("selected_provider_id") != "reference-local-structured-balanced":
        errors.append("SDK runtime task resolve did not select the expected provider")

    observability = app_server.observability
    runtime_admin_events = observability.list_events(component="runtime_admin", limit=200)["events"]
    runtime_admin_event_types = {event["event_type"] for event in runtime_admin_events}
    required_event_types = {
        "runtime_admin.reconcile.requested",
        "runtime_admin.reconcile.completed",
    }
    missing_event_types = sorted(required_event_types - runtime_admin_event_types)
    if missing_event_types:
        errors.append("missing runtime-admin observability events: %s" % ", ".join(missing_event_types))

    payload = {
        "milestone": "M29",
        "gate": "runtime-admin-smoke",
        "started_at": started_at,
        "completed_at": utc_now(),
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "base_url": base_url,
        "scenarios": scenarios,
        "observability": {
            "summary": observability.summary(),
            "runtime_admin_events": runtime_admin_events,
            "traces": observability.list_traces(limit=50),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.observability import ObservabilityStore
from core.provider_registry import ProviderRegistryLoader
from core.runtime_host import RuntimeHost
from core.task_profiles import TaskProfileLoader
from core.task_router import TaskRouter


DEFAULT_OUTPUT = REPO_ROOT / "tmp" / "diagnostics" / "m28_task_routing.latest.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run M28 provider registry and task-routing validation")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started_at = utc_now()
    provider_registry = ProviderRegistryLoader(REPO_ROOT).load_all()
    task_catalog = TaskProfileLoader(REPO_ROOT).load_all()
    observability = ObservabilityStore()
    router = TaskRouter(provider_registry, task_catalog, observability=observability)
    errors: list[str] = []
    scenarios: dict[str, dict] = {}

    environment = {
        "PYTHON": sys.executable,
        "REFERENCE_SERVICE_HOST": "127.0.0.1",
        "REFERENCE_SERVICE_PORT": str(_free_port()),
    }

    try:
        with RuntimeHost(REPO_ROOT, observability=observability, environment=environment) as host:
            manifest = host.load_manifest(REPO_ROOT / "infra" / "service_manifests" / "reference-http.json")
            host.reconcile([manifest])
            ready_service_states = host.inspect()

            structured_ready = router.route(
                "structured-extraction.strict",
                service_states=ready_service_states,
            )
            scenarios["structured_extraction_ready"] = structured_ready.as_dict()

            assistant_chat_ready = router.route(
                "assistant-chat.default",
                service_states=ready_service_states,
            )
            scenarios["assistant_chat_ready"] = assistant_chat_ready.as_dict()

            degraded_service_states = json.loads(json.dumps(ready_service_states))
            degraded_service_states["reference-http"]["lifecycle_state"] = "failed"
            degraded_service_states["reference-http"]["readiness"] = "not_ready"
            degraded_service_states["reference-http"]["health"] = "failed"
            structured_dependency_down = router.route(
                "structured-extraction.strict",
                service_states=degraded_service_states,
            )
            scenarios["structured_extraction_dependency_down"] = structured_dependency_down.as_dict()
    except Exception as exc:  # pragma: no cover - exercised in smoke runs
        errors.append(str(exc))

    ready = scenarios.get("structured_extraction_ready", {})
    if ready.get("selected_provider_id") != "reference-local-structured-balanced":
        errors.append("structured extraction did not resolve to the expected local balanced provider")
    if not ready.get("fallback", {}).get("invoked"):
        errors.append("structured extraction did not record the expected bounded fallback")

    chat = scenarios.get("assistant_chat_ready", {})
    if chat.get("selected_provider_id") != "reference-local-chat-economy":
        errors.append("assistant chat did not resolve to the expected local chat provider")

    dependency_down = scenarios.get("structured_extraction_dependency_down", {})
    if dependency_down.get("status") != "no_route":
        errors.append("dependency-down scenario did not produce a no-route result")
    else:
        candidate_reasons = {
            item["provider_id"]: item["reasons"] for item in dependency_down.get("candidates", [])
        }
        balanced_reasons = " ".join(candidate_reasons.get("reference-local-structured-balanced", []))
        if "service dependencies not ready" not in balanced_reasons:
            errors.append("dependency-down trace did not explain the rejected managed provider clearly")

    payload = {
        "milestone": "M28",
        "gate": "task-routing",
        "started_at": started_at,
        "completed_at": utc_now(),
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "provider_inventory": {
            "providers": provider_registry.list_provider_ids(),
            "task_profiles": task_catalog.list_profile_ids(),
        },
        "scenarios": scenarios,
        "observability": {
            "summary": observability.summary(),
            "events": observability.list_events(limit=500)["events"],
            "traces": observability.list_traces(limit=50),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import socket
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib import request

from jsonschema import Draft202012Validator

from api.http_server import build_http_server
from api.runtime_api import PublicRuntimeAPI
from api.runtime_factory import build_server_from_examples
from world_runtime.sdk import WorldRuntimeSDKClient


RUNTIME_ADMIN_ACTOR = {
    "actor_id": "human.runtime-admin-m30",
    "actor_type": "human",
    "roles": ["operator"],
    "capabilities": ["runtime.service.reconcile"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_local_ai_reference_stack(
    repo_root: Path,
    *,
    stack_path: Path,
    include_eval: bool = True,
) -> Dict[str, Any]:
    repo_root = Path(repo_root)
    stack_payload = _load_json(stack_path)
    started_at = utc_now()
    errors: List[str] = []
    supported_surfaces: Dict[str, Any] = {}
    routing: Dict[str, Any] = {}
    eval_report: Dict[str, Any] = {}

    port = _free_port()
    base_url = "http://127.0.0.1:%s" % port

    manifest_path = repo_root / str(stack_payload["smoke_test"]["fixture_manifest_path"])
    fixture_manifest = _load_json(manifest_path)
    schema_path = repo_root / str(stack_payload["smoke_test"]["schema_path"])
    schema = _load_json(schema_path)
    stack_service_id = str(stack_payload["smoke_test"]["service_id"])
    task_profile_id = str(stack_payload["smoke_test"]["task_profile_id"])
    preferred_provider_id = str(stack_payload["smoke_test"]["preferred_provider_id"])
    fallback_policy_input = dict(stack_payload["smoke_test"].get("fallback_policy_input", {}))

    app_server = build_server_from_examples(repo_root / "examples")
    runtime_api = PublicRuntimeAPI(app_server)
    http_server = build_http_server("127.0.0.1", port, runtime_api)
    http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    http_thread.start()
    time.sleep(0.2)

    try:
        session_id = app_server.session_create()["session_id"]

        supported_surfaces["inventory"] = app_server.handle_request("runtime.inventory.summary")
        supported_surfaces["app_server_reconcile"] = app_server.handle_request(
            "runtime.service.reconcile",
            {
                "session_id": session_id,
                "service_ids": [stack_service_id],
                "actor": RUNTIME_ADMIN_ACTOR,
            },
        )
        supported_surfaces["public_api_service_get"] = _http_get_json(
            base_url + "/v1/runtime/services/%s" % stack_service_id
        )
        supported_surfaces["sdk_service_get"] = WorldRuntimeSDKClient(base_url=base_url).get_runtime_service(
            stack_service_id
        )
        supported_surfaces["public_api_resolve_preferred"] = _http_post_json(
            base_url + "/v1/runtime/tasks/resolve",
            {"task_profile_id": task_profile_id},
        )
        sdk = WorldRuntimeSDKClient(base_url=base_url)
        supported_surfaces["sdk_resolve_fallback"] = sdk.resolve_runtime_task(
            task_profile_id=task_profile_id,
            policy_input=fallback_policy_input,
        )
        supported_surfaces["audit_export"] = app_server.handle_request(
            "audit.export",
            {"session_id": session_id},
        )

        service_endpoint = _service_output_url(
            supported_surfaces["sdk_service_get"],
            output_name="extract",
        )
        service_state_url = _service_output_url(
            supported_surfaces["sdk_service_get"],
            output_name="state",
        )
        preferred_route = supported_surfaces["public_api_resolve_preferred"].get("result", {})
        fallback_route = supported_surfaces["sdk_resolve_fallback"]
        routing = {
            "preferred": preferred_route,
            "fallback": fallback_route,
        }

        if include_eval:
            eval_report = _run_eval_cases(
                repo_root=repo_root,
                fixture_manifest=fixture_manifest,
                schema=schema,
                endpoint=service_endpoint,
                task_profile_id=task_profile_id,
                preferred_provider_id=preferred_provider_id,
                fallback_provider_id=fallback_route["decision"]["selected_provider_id"],
            )
            if eval_report["status"] != "passed":
                errors.extend(eval_report["errors"])

        service_state = _http_get_json(service_state_url)

        preferred_selected = preferred_route.get("decision", {}).get("selected_provider_id")
        if preferred_selected != preferred_provider_id:
            errors.append(
                "preferred route selected %s instead of %s"
                % (preferred_selected, preferred_provider_id)
            )

        fallback_selected = fallback_route.get("decision", {}).get("selected_provider_id")
        if fallback_selected == preferred_provider_id:
            errors.append("fallback route did not downgrade away from the preferred provider")

        if supported_surfaces["app_server_reconcile"].get("ok") is not True:
            errors.append("runtime-admin reconcile failed for the reference local AI service")

        audit_actions = {
            item.get("selected_action", {}).get("action_type")
            for item in supported_surfaces["audit_export"].get("result", {}).get("artifacts", {}).get("decisions", [])
        }
        if "runtime_service_reconcile" not in audit_actions:
            errors.append("runtime-admin reconcile did not appear in audit export")

        payload = {
            "milestone": "M30",
            "gate": "structured-extraction-smoke",
            "stack_id": stack_payload["stack_id"],
            "stack_kind": stack_payload["stack_kind"],
            "started_at": started_at,
            "completed_at": utc_now(),
            "status": "passed" if not errors else "failed",
            "errors": errors,
            "base_url": base_url,
            "supported_surfaces": supported_surfaces,
            "routing": routing,
            "eval": eval_report,
            "service_state": service_state,
            "observability": {
                "summary": app_server.observability.summary(),
                "events": app_server.observability.list_events(limit=200)["events"],
                "traces": app_server.observability.list_traces(limit=50),
            },
        }
    finally:
        http_server.shutdown()
        http_server.server_close()
        http_thread.join(timeout=5.0)
        app_server.runtime_admin.close()

    return payload


def _run_eval_cases(
    *,
    repo_root: Path,
    fixture_manifest: Dict[str, Any],
    schema: Dict[str, Any],
    endpoint: str,
    task_profile_id: str,
    preferred_provider_id: str,
    fallback_provider_id: str | None,
) -> Dict[str, Any]:
    cases = list(fixture_manifest.get("cases", []))
    results = []
    errors: List[str] = []
    validator = Draft202012Validator(schema)

    for index, case in enumerate(cases):
        input_path = repo_root / str(case["input_path"])
        expected_path = repo_root / str(case["expected_output_path"])
        document_text = input_path.read_text(encoding="utf-8")
        expected_output = _load_json(expected_path)
        provider_id = preferred_provider_id if index == 0 else (fallback_provider_id or preferred_provider_id)
        response = _http_post_json(
            endpoint,
            {
                "provider_id": provider_id,
                "model_id": "%s.model" % provider_id,
                "task_profile_id": task_profile_id,
                "schema": schema,
                "input": {
                    "source_id": expected_output["source_id"],
                    "document_text": document_text,
                },
            },
        )
        repeated = _http_post_json(
            endpoint,
            {
                "provider_id": provider_id,
                "model_id": "%s.model" % provider_id,
                "task_profile_id": task_profile_id,
                "schema": schema,
                "input": {
                    "source_id": expected_output["source_id"],
                    "document_text": document_text,
                },
            },
        )

        output = response.get("output", {})
        validation_errors = sorted(validator.iter_errors(output), key=lambda item: list(item.path))
        schema_valid = not validation_errors
        matches_expected = output == expected_output
        deterministic_output = repeated.get("output", {}) == output
        completeness = float(response.get("diagnostics", {}).get("field_completeness", 0.0))
        minimum = float(case.get("minimum_field_completeness", 0.0))

        case_errors = []
        if not schema_valid:
            case_errors.append("schema validation failed")
        if not matches_expected:
            case_errors.append("output did not match expected fixture")
        if not deterministic_output:
            case_errors.append("repeated extraction changed the output structure")
        if completeness < minimum:
            case_errors.append(
                "field completeness %.4f fell below minimum %.4f" % (completeness, minimum)
            )

        if case_errors:
            errors.append("%s: %s" % (case["case_id"], "; ".join(case_errors)))

        results.append(
            {
                "case_id": case["case_id"],
                "description": case.get("description"),
                "provider_id": provider_id,
                "schema_valid": schema_valid,
                "schema_errors": [error.message for error in validation_errors],
                "matches_expected": matches_expected,
                "deterministic_output": deterministic_output,
                "field_completeness": completeness,
                "minimum_field_completeness": minimum,
                "response": response,
            }
        )

    return {
        "suite_id": fixture_manifest.get("suite_id", "structured-extraction"),
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "results": results,
    }


def _service_output_url(service_result: Dict[str, Any], *, output_name: str) -> str:
    outputs = (
        service_result.get("service", {})
        .get("manifest", {})
        .get("outputs", [])
    )
    for item in outputs:
        if item.get("name") == output_name:
            return str(item["value"])
    raise ValueError("service output not found: %s" % output_name)


def _http_get_json(url: str) -> Dict[str, Any]:
    with request.urlopen(url, timeout=10.0) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def _http_post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
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


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _load_json(path: Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)

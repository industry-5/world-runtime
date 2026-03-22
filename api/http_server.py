import argparse
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

from api.runtime_api import API_VERSION, PUBLIC_ENDPOINTS, PublicRuntimeAPI
from api.runtime_factory import build_server_from_examples


def _json_bytes(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True).encode("utf-8")


class _RuntimeHTTPHandler(BaseHTTPRequestHandler):
    runtime_api: Optional[PublicRuntimeAPI] = None
    auth_token: Optional[str] = None

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "status": "healthy",
                    "api_version": API_VERSION,
                },
            )
            return

        if not self._authorize():
            return

        if self.path == PUBLIC_ENDPOINTS["telemetry_summary"]:
            assert self.runtime_api is not None
            try:
                result = self.runtime_api.telemetry_summary()
                self._send_ok(result)
                return
            except Exception as exc:  # pragma: no cover - defensive
                self._send_error_payload("runtime_error", str(exc), status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return

        if self.path == "/v1/meta":
            assert self.runtime_api is not None
            self._send_ok(self.runtime_api.metadata())
            return

        self._send_error_payload("not_found", "unknown endpoint", status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if not self._authorize():
            return

        body = self._read_json_body()
        if isinstance(body, dict) and body.get("_error"):
            self._send_error_payload("invalid_json", body["_error"], status=HTTPStatus.BAD_REQUEST)
            return

        try:
            result = self._dispatch_post(self.path, body or {})
        except ValueError as exc:
            self._send_error_payload("bad_request", str(exc), status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:  # pragma: no cover - defensive
            self._send_error_payload("runtime_error", str(exc), status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if result is None:
            self._send_error_payload("not_found", "unknown endpoint", status=HTTPStatus.NOT_FOUND)
            return

        self._send_ok(result)

    def _dispatch_post(self, path: str, body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        assert self.runtime_api is not None

        if path == PUBLIC_ENDPOINTS["runtime_call"]:
            method = body.get("method")
            if not isinstance(method, str) or not method:
                raise ValueError("method is required")
            params = body.get("params")
            if params is not None and not isinstance(params, dict):
                raise ValueError("params must be an object")
            response = self.runtime_api.call_runtime(method=method, params=params)
            if not response.get("ok"):
                raise ValueError(response.get("error", "runtime call failed"))
            return response["result"]

        if path == PUBLIC_ENDPOINTS["session_create"]:
            return self.runtime_api.create_session()

        if path == PUBLIC_ENDPOINTS["proposal_submit"]:
            return self.runtime_api.submit_proposal(
                session_id=body["session_id"],
                proposal=body["proposal"],
                policies=body.get("policies"),
            )

        if path == PUBLIC_ENDPOINTS["simulation_run"]:
            return self.runtime_api.run_simulation(
                session_id=body["session_id"],
                simulation_id=body["simulation_id"],
                projection_name=body["projection_name"],
                hypothetical_events=body.get("hypothetical_events"),
                scenario_name=body.get("scenario_name"),
                assumptions=body.get("assumptions"),
                inputs=body.get("inputs"),
            )

        if path == PUBLIC_ENDPOINTS["approval_respond"]:
            return self.runtime_api.respond_approval(
                approval_id=body["approval_id"],
                decision=body["decision"],
                actor=body["actor"],
                comment=body.get("comment"),
            )

        if path == PUBLIC_ENDPOINTS["connector_inbound_run"]:
            return self.runtime_api.run_connector_inbound(
                session_id=body["session_id"],
                connector_id=body["connector_id"],
                event_type_map=body["event_type_map"],
                external_event=body["external_event"],
                idempotency_key=body.get("idempotency_key"),
                retry=body.get("retry"),
                fail_until_attempt=int(body.get("fail_until_attempt", 0)),
                policies=body.get("policies"),
                approval_id=body.get("approval_id"),
            )

        if path == PUBLIC_ENDPOINTS["connector_outbound_run"]:
            return self.runtime_api.run_connector_outbound(
                session_id=body["session_id"],
                connector_id=body["connector_id"],
                action_type_map=body["action_type_map"],
                action=body["action"],
                idempotency_key=body.get("idempotency_key"),
                retry=body.get("retry"),
                fail_until_attempt=int(body.get("fail_until_attempt", 0)),
                fail_permanently=bool(body.get("fail_permanently", False)),
                transport_plugin=body.get("transport_plugin"),
                policies=body.get("policies"),
                approval_id=body.get("approval_id"),
            )

        return None

    def _authorize(self) -> bool:
        token = self.auth_token
        if not token:
            return True

        auth_header = self.headers.get("Authorization", "")
        expected = "Bearer %s" % token
        if auth_header == expected:
            return True

        self._send_error_payload(
            code="unauthorized",
            message="missing or invalid bearer token",
            status=HTTPStatus.UNAUTHORIZED,
        )
        return False

    def _read_json_body(self) -> Dict[str, Any]:
        if self.command != "POST":
            return {}
        raw_length = self.headers.get("Content-Length", "0")
        try:
            content_length = int(raw_length)
        except ValueError:
            return {"_error": "invalid content length"}

        if content_length <= 0:
            return {}

        payload = self.rfile.read(content_length)
        try:
            decoded = json.loads(payload.decode("utf-8"))
        except Exception as exc:
            return {"_error": str(exc)}

        if not isinstance(decoded, dict):
            return {"_error": "request body must be an object"}
        return decoded

    def _send_ok(self, result: Dict[str, Any]) -> None:
        self._send(
            HTTPStatus.OK,
            {
                "ok": True,
                "api_version": API_VERSION,
                "result": result,
            },
        )

    def _send_error_payload(self, code: str, message: str, status: HTTPStatus) -> None:
        self._send(
            status,
            {
                "ok": False,
                "api_version": API_VERSION,
                "error": {
                    "code": code,
                    "message": message,
                },
            },
        )

    def _send(self, status: HTTPStatus, payload: Dict[str, Any]) -> None:
        blob = _json_bytes(payload)
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
        return


def build_http_server(
    host: str,
    port: int,
    runtime_api: PublicRuntimeAPI,
    auth_token: Optional[str] = None,
) -> ThreadingHTTPServer:
    handler = type("RuntimeHTTPHandler", (_RuntimeHTTPHandler,), {})
    handler.runtime_api = runtime_api
    handler.auth_token = auth_token
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="World Runtime Public API HTTP server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--examples-dir", default="examples")
    parser.add_argument(
        "--api-token",
        default=os.getenv("WORLD_RUNTIME_API_TOKEN"),
        help="Optional bearer token. Falls back to WORLD_RUNTIME_API_TOKEN.",
    )
    args = parser.parse_args()

    app_server = build_server_from_examples(Path(args.examples_dir))
    runtime_api = PublicRuntimeAPI(app_server)
    server = build_http_server(host=args.host, port=args.port, runtime_api=runtime_api, auth_token=args.api_token)

    print(
        "Serving World Runtime Public API %s at http://%s:%s" % (API_VERSION, args.host, args.port),
        flush=True,
    )
    if args.api_token:
        print("Bearer auth enabled via WORLD_RUNTIME_API_TOKEN/--api-token", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

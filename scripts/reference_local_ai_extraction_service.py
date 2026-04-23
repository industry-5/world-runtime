import argparse
import json
import os
from pathlib import Path
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List
from urllib import parse

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.reference_local_ai_extraction import evaluate_extraction, extract_character_card


class ReferenceLocalAIState:
    def __init__(self, started_at: float, startup_delay_seconds: float) -> None:
        self.started_at = started_at
        self.startup_delay_seconds = startup_delay_seconds
        self.healthy = True
        self.requests: List[Dict[str, Any]] = []

    def ready(self) -> bool:
        return time.time() - self.started_at >= self.startup_delay_seconds

    def payload(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self.healthy else "unhealthy",
            "ready": self.ready(),
            "pid": os.getpid(),
            "started_at_epoch": self.started_at,
            "requests_served": len(self.requests),
        }

    def record_request(self, payload: Dict[str, Any]) -> None:
        self.requests.append(payload)
        self.requests = self.requests[-20:]


def build_handler(state: ReferenceLocalAIState):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def do_GET(self) -> None:  # noqa: N802
            parsed = parse.urlparse(self.path)
            if parsed.path == "/ready":
                self._json(200 if state.ready() else 503, state.payload())
                return
            if parsed.path == "/health":
                self._json(200 if state.healthy else 503, state.payload())
                return
            if parsed.path == "/state":
                self._json(
                    200,
                    {
                        **state.payload(),
                        "recent_requests": list(state.requests),
                    },
                )
                return

            self._json(404, {"error": "not_found", "path": parsed.path})

        def do_POST(self) -> None:  # noqa: N802
            parsed = parse.urlparse(self.path)
            if parsed.path != "/v1/extract":
                self._json(404, {"error": "not_found", "path": parsed.path})
                return

            body = self.rfile.read(int(self.headers.get("Content-Length", "0") or "0"))
            try:
                request_payload = json.loads(body.decode("utf-8"))
            except Exception:
                self._json(400, {"ok": False, "error": "invalid_json"})
                return

            started = time.perf_counter()
            schema = request_payload.get("schema") or {}
            input_payload = request_payload.get("input") or {}
            source_id = str(input_payload.get("source_id", "")).strip() or "unknown-source"
            document_text = str(input_payload.get("document_text", ""))
            output = extract_character_card(document_text, source_id=source_id)
            validation = evaluate_extraction(output, schema)
            latency_ms = round((time.perf_counter() - started) * 1000, 3)

            response = {
                "ok": validation["schema_valid"],
                "provider_id": request_payload.get("provider_id"),
                "model_id": request_payload.get("model_id"),
                "task_profile_id": request_payload.get("task_profile_id"),
                "output": output,
                "diagnostics": {
                    "schema_valid": validation["schema_valid"],
                    "schema_errors": list(validation["schema_errors"]),
                    "field_completeness": validation["field_completeness"],
                    "missing_required_fields": list(validation["missing_required_fields"]),
                    "ambiguous_fields": list(validation["ambiguous_fields"]),
                    "latency_ms": latency_ms,
                    "engine": "reference_local_structured_extraction_v1",
                },
            }
            state.record_request(
                {
                    "source_id": source_id,
                    "provider_id": request_payload.get("provider_id"),
                    "task_profile_id": request_payload.get("task_profile_id"),
                    "schema_valid": validation["schema_valid"],
                    "latency_ms": latency_ms,
                }
            )
            self._json(200 if validation["schema_valid"] else 422, response)

        def _json(self, status_code: int, payload: Dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reference local AI extraction service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--startup-delay-seconds", type=float, default=0.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = ReferenceLocalAIState(time.time(), args.startup_delay_seconds)
    server = ThreadingHTTPServer((args.host, args.port), build_handler(state))
    print(
        json.dumps(
            {
                "event": "reference_local_ai_service_started",
                "host": args.host,
                "port": args.port,
                "pid": os.getpid(),
            }
        ),
        flush=True,
    )
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

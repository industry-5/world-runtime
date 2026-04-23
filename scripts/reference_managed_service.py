import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict
from urllib import parse


class ReferenceServiceState:
    def __init__(self, started_at: float, startup_delay_seconds: float) -> None:
        self.started_at = started_at
        self.startup_delay_seconds = startup_delay_seconds
        self.healthy = True
        self.exit_code = None

    def ready(self) -> bool:
        return time.time() - self.started_at >= self.startup_delay_seconds

    def payload(self) -> Dict[str, object]:
        return {
            "status": "healthy" if self.healthy else "unhealthy",
            "ready": self.ready(),
            "pid": os.getpid(),
            "started_at_epoch": self.started_at,
        }


def build_handler(state: ReferenceServiceState):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def do_GET(self) -> None:  # noqa: N802
            parsed = parse.urlparse(self.path)
            params = parse.parse_qs(parsed.query)
            if parsed.path == "/ready":
                self._json(200 if state.ready() else 503, state.payload())
                return
            if parsed.path == "/health":
                self._json(200 if state.healthy else 503, state.payload())
                return
            if parsed.path == "/control/health":
                desired = params.get("status", ["healthy"])[0]
                state.healthy = desired != "unhealthy"
                self._json(200, {"healthy": state.healthy})
                return
            if parsed.path == "/control/exit":
                code = int(params.get("code", ["0"])[0])
                self._json(200, {"exiting": True, "code": code})

                def _exit_later() -> None:
                    time.sleep(0.1)
                    os._exit(code)  # noqa: WPS437

                threading.Thread(target=_exit_later, daemon=True).start()
                return
            if parsed.path == "/state":
                self._json(200, state.payload())
                return

            self._json(404, {"error": "not_found", "path": parsed.path})

        def _json(self, status_code: int, payload: Dict[str, object]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reference managed service for runtime-host smoke tests")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--startup-delay-seconds", type=float, default=0.0)
    parser.add_argument("--fail-before-ready", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.fail_before_ready:
        raise SystemExit(2)

    state = ReferenceServiceState(time.time(), args.startup_delay_seconds)
    server = ThreadingHTTPServer((args.host, args.port), build_handler(state))
    print(
        json.dumps(
            {
                "event": "reference_service_started",
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

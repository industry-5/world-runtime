from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent


class LabHandler(BaseHTTPRequestHandler):
    upstream_base: str = "http://127.0.0.1:8080"

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/api/"):
            self._proxy("GET")
            return

        if self.path in {"/", "/index.html"}:
            self._serve_static("index.html", "text/html; charset=utf-8")
            return

        if self.path == "/styles.css":
            self._serve_static("styles.css", "text/css; charset=utf-8")
            return

        if self.path == "/app.js":
            self._serve_static("app.js", "application/javascript; charset=utf-8")
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.startswith("/api/"):
            self._proxy("POST")
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

    def _serve_static(self, filename: str, content_type: str) -> None:
        asset = ROOT / filename
        if not asset.exists():
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "asset_not_found"})
            return
        blob = asset.read_bytes()
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def _proxy(self, method: str) -> None:
        path = self.path[len("/api"):]
        target_url = self.upstream_base.rstrip("/") + path

        body: Optional[bytes] = None
        if method == "POST":
            length_raw = self.headers.get("Content-Length", "0")
            try:
                length = int(length_raw)
            except ValueError:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "bad_length"})
                return
            body = self.rfile.read(max(length, 0)) if length > 0 else b""

        headers = {"Accept": "application/json"}
        auth = self.headers.get("Authorization")
        if auth:
            headers["Authorization"] = auth
        if body is not None:
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(target_url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type", "application/json")
                self.send_response(response.status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            payload = exc.read() or json.dumps({"ok": False, "error": "upstream_http_error"}).encode("utf-8")
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except urllib.error.URLError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {"ok": False, "error": {"code": "upstream_unreachable", "message": str(exc.reason)}},
            )

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        blob = json.dumps(payload).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def log_message(self, fmt: str, *args: object) -> None:  # noqa: A003
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="World Run Lab standalone server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--upstream", default="http://127.0.0.1:8080")
    args = parser.parse_args()

    handler = type("WorldRunLabHandler", (LabHandler,), {})
    handler.upstream_base = args.upstream

    server = ThreadingHTTPServer((args.host, args.port), handler)
    print("World Run Lab serving at http://%s:%s (upstream=%s)" % (args.host, args.port, args.upstream), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

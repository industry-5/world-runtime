from __future__ import annotations

import argparse
import json
import mimetypes
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


class StudioNextHandler(BaseHTTPRequestHandler):
    upstream_base: str = "http://127.0.0.1:8080"

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/api/"):
            self._proxy("GET")
            return

        # Hash-based routing means we only need to serve shell + assets.
        requested = self.path.split("?", 1)[0]
        if requested in {"/", ""}:
            self._serve_index()
            return

        if self._serve_static(requested):
            return

        # Keep a stable shell for client-side route entry points.
        self._serve_index()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.startswith("/api/"):
            self._proxy("POST")
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

    def _asset_root(self) -> Path:
        return DIST if DIST.exists() else ROOT

    def _serve_index(self) -> None:
        index_path = self._asset_root() / "index.html"
        if not index_path.exists():
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "index_not_found"})
            return
        self._serve_file(index_path, "text/html; charset=utf-8")

    def _serve_static(self, requested_path: str) -> bool:
        if requested_path.startswith("/"):
            requested_path = requested_path[1:]
        if not requested_path:
            return False

        candidate = (self._asset_root() / requested_path).resolve()
        root = self._asset_root().resolve()
        if root not in candidate.parents and candidate != root:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_path"})
            return True

        if not candidate.exists() or not candidate.is_file():
            return False

        guessed, _ = mimetypes.guess_type(candidate.name)
        content_type = guessed or "application/octet-stream"
        if content_type.startswith("text/"):
            content_type = f"{content_type}; charset=utf-8"
        self._serve_file(candidate, content_type)
        return True

    def _serve_file(self, path: Path, content_type: str) -> None:
        payload = path.read_bytes()
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _proxy(self, method: str) -> None:
        path = self.path[len("/api") :]
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
    parser = argparse.ArgumentParser(description="World Game Studio Next standalone server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8093)
    parser.add_argument("--upstream", default="http://127.0.0.1:8080")
    args = parser.parse_args()

    handler = type("WorldGameStudioNextHandler", (StudioNextHandler,), {})
    handler.upstream_base = args.upstream

    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(
        "World Game Studio Next serving at http://%s:%s (upstream=%s, assets=%s)"
        % (args.host, args.port, args.upstream, DIST if DIST.exists() else ROOT),
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()

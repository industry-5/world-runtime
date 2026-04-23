import argparse
import json
import shutil
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import request

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.observability import ObservabilityStore
from core.runtime_host import RuntimeHost


DEFAULT_OUTPUT = REPO_ROOT / "tmp" / "diagnostics" / "m27_service_host.latest.json"
DEFAULT_WORK_DIR = REPO_ROOT / "tmp" / "service_host_smoke"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _fetch_json(url: str) -> dict:
    with request.urlopen(url, timeout=5.0) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def _wait_for_json(url: str, timeout_seconds: float) -> dict:
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            return _fetch_json(url)
        except Exception as exc:  # pragma: no cover - exercised in smoke runs
            last_error = str(exc)
            time.sleep(0.2)
    raise RuntimeError("timed out waiting for %s (%s)" % (url, last_error or "no response"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run M27 managed service-host smoke validation")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR)
    parser.add_argument("--fast", action="store_true", help="Skip the local world-runtime manifest scenario")
    return parser.parse_args()


def _build_failed_start_manifest(source: Path, destination: Path) -> Path:
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["process"]["arguments"].append("--fail-before-ready")
    payload["restart_policy"]["max_attempts"] = 1
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


def main() -> int:
    args = parse_args()
    started_at = utc_now()
    errors: list[str] = []
    scenarios: dict[str, dict] = {}
    observability = ObservabilityStore()

    if args.work_dir.exists():
        shutil.rmtree(args.work_dir)
    args.work_dir.mkdir(parents=True, exist_ok=True)

    reference_port = _free_port()
    runtime_port = _free_port()

    reference_env = {
        "PYTHON": sys.executable,
        "REFERENCE_SERVICE_HOST": "127.0.0.1",
        "REFERENCE_SERVICE_PORT": str(reference_port),
    }
    runtime_env = {
        "PYTHON": sys.executable,
        "WORLD_RUNTIME_SERVICE_HOST": "127.0.0.1",
        "WORLD_RUNTIME_SERVICE_PORT": str(runtime_port),
    }

    try:
        with RuntimeHost(REPO_ROOT, observability=observability, environment=reference_env) as host:
            manifest = host.load_manifest(REPO_ROOT / "infra" / "service_manifests" / "reference-http.json")
            host.reconcile([manifest])
            scenarios["reference_ready"] = host.inspect("reference-http")

            _fetch_json("http://127.0.0.1:%s/control/exit?code=7" % reference_port)
            time.sleep(0.3)
            host.reconcile([manifest])
            scenarios["restart_after_exit"] = host.inspect("reference-http")

            _fetch_json("http://127.0.0.1:%s/control/health?status=unhealthy" % reference_port)
            time.sleep(0.1)
            host.check_health("reference-http")
            scenarios["restart_after_health_failure"] = host.inspect("reference-http")

            failed_manifest_path = _build_failed_start_manifest(
                REPO_ROOT / "infra" / "service_manifests" / "reference-http.json",
                args.work_dir / "reference-http-fail.json",
            )
            failed_manifest = host.load_manifest(failed_manifest_path)
            host.reconcile([failed_manifest])
            scenarios["failed_start"] = host.inspect("reference-http")

        if not args.fast:
            with RuntimeHost(REPO_ROOT, observability=observability, environment=runtime_env) as host:
                runtime_manifest = host.load_manifest(
                    REPO_ROOT / "infra" / "service_manifests" / "world-runtime.local.json"
                )
                host.reconcile([runtime_manifest])
                health_payload = _wait_for_json(
                    "http://127.0.0.1:%s/health" % runtime_port,
                    timeout_seconds=10.0,
                )
                meta_payload = _wait_for_json(
                    "http://127.0.0.1:%s/v1/meta" % runtime_port,
                    timeout_seconds=10.0,
                )
                snapshot = host.inspect("world-runtime-local")
                snapshot["health_payload"] = health_payload
                snapshot["meta_payload"] = meta_payload
                scenarios["world_runtime_local"] = snapshot
    except Exception as exc:  # pragma: no cover - exercised in smoke runs
        errors.append(str(exc))

    lifecycle_events = observability.list_events(component="runtime_host", limit=500)["events"]
    required_events = {
        "service_start_requested",
        "service_started",
        "service_ready",
        "service_failed",
        "service_restarted",
        "service_stopped",
    }
    seen_event_types = {event["event_type"] for event in lifecycle_events}
    missing_event_types = sorted(required_events - seen_event_types)
    if missing_event_types:
        errors.append("missing lifecycle events: %s" % ", ".join(missing_event_types))

    reference_ready = scenarios.get("reference_ready", {})
    if reference_ready.get("lifecycle_state") != "ready":
        errors.append("reference service did not reach ready state")

    restart_exit = scenarios.get("restart_after_exit", {})
    if restart_exit.get("restart_count", 0) < 1:
        errors.append("reference service did not restart after controlled exit")

    restart_health = scenarios.get("restart_after_health_failure", {})
    if "health probe failed" not in str(restart_health.get("last_failure_reason")):
        errors.append("health failure diagnostics were not recorded")

    failed_start = scenarios.get("failed_start", {})
    if failed_start.get("lifecycle_state") != "failed":
        errors.append("failed-start scenario did not terminate in failed state")
    if "before readiness" not in str(failed_start.get("last_failure_reason")):
        errors.append("failed-start diagnostics were not recorded clearly")

    payload = {
        "milestone": "M27",
        "gate": "service-host-smoke",
        "mode": "fast" if args.fast else "full",
        "started_at": started_at,
        "completed_at": utc_now(),
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "scenarios": scenarios,
        "observability": {
            "summary": observability.summary(),
            "lifecycle_events": lifecycle_events,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

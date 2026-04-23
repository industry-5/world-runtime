import json
import socket
import time
from pathlib import Path
from urllib import request

from core.observability import ObservabilityStore
from core.runtime_host import RuntimeHost


REPO_ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _read_json(url: str) -> dict:
    with request.urlopen(url, timeout=3.0) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def test_runtime_host_loads_reference_manifest_with_env_expansion():
    host = RuntimeHost(
        repo_root=REPO_ROOT,
        environment={
            "REFERENCE_SERVICE_HOST": "127.0.0.1",
            "REFERENCE_SERVICE_PORT": str(_free_port()),
        },
    )

    manifest = host.load_manifest(REPO_ROOT / "infra" / "service_manifests" / "reference-http.json")

    assert manifest.service_id == "reference-http"
    assert manifest.process.working_directory == str(REPO_ROOT)
    assert manifest.readiness_probe is not None
    assert manifest.readiness_probe.url.startswith("http://127.0.0.1:")
    assert manifest.outputs[0].value.startswith("http://127.0.0.1:")


def test_runtime_host_starts_reference_service_and_emits_lifecycle_events():
    port = _free_port()
    observability = ObservabilityStore()

    with RuntimeHost(
        repo_root=REPO_ROOT,
        observability=observability,
        environment={
            "REFERENCE_SERVICE_HOST": "127.0.0.1",
            "REFERENCE_SERVICE_PORT": str(port),
        },
    ) as host:
        manifest = host.load_manifest(REPO_ROOT / "infra" / "service_manifests" / "reference-http.json")

        snapshots = host.reconcile([manifest])
        state = snapshots["reference-http"]

        assert state["lifecycle_state"] == "ready"
        assert state["readiness"] == "ready"
        assert state["pid"] is not None

        summary = observability.summary()
        assert summary["events"]["by_type"]["service_start_requested"] >= 1
        assert summary["events"]["by_type"]["service_started"] >= 1
        assert summary["events"]["by_type"]["service_ready"] >= 1


def test_runtime_host_restarts_after_process_exit():
    port = _free_port()

    with RuntimeHost(
        repo_root=REPO_ROOT,
        environment={
            "REFERENCE_SERVICE_HOST": "127.0.0.1",
            "REFERENCE_SERVICE_PORT": str(port),
        },
    ) as host:
        manifest = host.load_manifest(REPO_ROOT / "infra" / "service_manifests" / "reference-http.json")
        host.reconcile([manifest])
        first_pid = host.inspect("reference-http")["pid"]

        _read_json("http://127.0.0.1:%s/control/exit?code=7" % port)
        time.sleep(0.25)
        host.reconcile([manifest])
        restarted = host.inspect("reference-http")

        assert restarted["lifecycle_state"] == "ready"
        assert restarted["restart_count"] >= 1
        assert restarted["last_failure_reason"] == "process exited with code 7"
        assert restarted["pid"] != first_pid


def test_runtime_host_restarts_after_health_failure():
    port = _free_port()

    with RuntimeHost(
        repo_root=REPO_ROOT,
        environment={
            "REFERENCE_SERVICE_HOST": "127.0.0.1",
            "REFERENCE_SERVICE_PORT": str(port),
        },
    ) as host:
        manifest = host.load_manifest(REPO_ROOT / "infra" / "service_manifests" / "reference-http.json")
        host.reconcile([manifest])

        _read_json("http://127.0.0.1:%s/control/health?status=unhealthy" % port)
        time.sleep(0.1)
        host.check_health("reference-http")
        recovered = host.inspect("reference-http")

        assert recovered["lifecycle_state"] == "ready"
        assert recovered["restart_count"] >= 1
        assert "health probe failed" in recovered["last_failure_reason"]


def test_runtime_host_reports_failed_start_when_attempts_are_exhausted(tmp_path):
    port = _free_port()
    manifest_path = tmp_path / "reference-http-fail.json"
    payload = json.loads(
        (REPO_ROOT / "infra" / "service_manifests" / "reference-http.json").read_text(encoding="utf-8")
    )
    payload["process"]["arguments"].append("--fail-before-ready")
    payload["restart_policy"]["max_attempts"] = 1
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with RuntimeHost(
        repo_root=REPO_ROOT,
        environment={
            "REFERENCE_SERVICE_HOST": "127.0.0.1",
            "REFERENCE_SERVICE_PORT": str(port),
        },
    ) as host:
        manifest = host.load_manifest(manifest_path)
        host.reconcile([manifest])
        state = host.inspect("reference-http")

        assert state["lifecycle_state"] == "failed"
        assert state["restart_count"] == 1
        assert "before readiness" in state["last_failure_reason"]

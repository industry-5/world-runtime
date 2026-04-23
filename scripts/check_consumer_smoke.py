import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib import error, request

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "tmp" / "diagnostics" / "m26_consumer_boundary.latest.json"
DEFAULT_WORK_DIR = REPO_ROOT / "tmp" / "consumer_smoke"
EXAMPLE_SCRIPT = REPO_ROOT / "examples" / "consumers" / "python_package_smoke.py"
VERSION_FILE = REPO_ROOT / "VERSION"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _python_path(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _world_runtime_path(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "world-runtime.exe"
    return venv_dir / "bin" / "world-runtime"


def _run_command(command: list[str], cwd: Path, env: dict[str, str], label: str) -> dict:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return {
            "label": label,
            "command": command,
            "returncode": 1,
            "stdout_tail": "",
            "stderr_tail": str(exc),
            "status": "failed",
        }
    return {
        "label": label,
        "command": command,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
        "status": "passed" if result.returncode == 0 else "failed",
    }


def _fetch_json(url: str) -> dict:
    with request.urlopen(url, timeout=5.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _wait_for_json(url: str, timeout_seconds: float) -> dict:
    deadline = time.time() + timeout_seconds
    last_error: Optional[str] = None
    while time.time() < deadline:
        try:
            return _fetch_json(url)
        except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            time.sleep(0.25)
    raise RuntimeError("timed out waiting for %s (%s)" % (url, last_error or "no response"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate installed-package consumer smoke flow")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR)
    parser.add_argument("--package-source", type=Path, default=REPO_ROOT)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18080)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started_at = utc_now()
    expected_version = VERSION_FILE.read_text(encoding="utf-8").strip()
    base_url = "http://%s:%s" % (args.host, args.port)
    errors: list[str] = []
    command_results: list[dict] = []

    if args.work_dir.exists():
        shutil.rmtree(args.work_dir)
    args.work_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    command_results.append(
        _run_command(
            [sys.executable, "-m", "venv", "--system-site-packages", str(args.work_dir / "venv")],
            cwd=args.work_dir,
            env=env,
            label="create-venv",
        )
    )
    if command_results[-1]["returncode"] != 0:
        errors.append("failed to create consumer smoke virtualenv")

    venv_dir = args.work_dir / "venv"
    venv_python = _python_path(venv_dir)
    world_runtime_bin = _world_runtime_path(venv_dir)

    if not errors:
        command_results.append(
            _run_command(
                [
                    str(venv_python),
                    "-m",
                    "pip",
                    "install",
                    "--no-build-isolation",
                    "--no-deps",
                    str(args.package_source),
                ],
                cwd=args.work_dir,
                env=env,
                label="install-package",
            )
        )
        if command_results[-1]["returncode"] != 0:
            errors.append("failed to install world-runtime into isolated consumer environment")

    if not errors:
        command_results.append(
            _run_command(
                [str(venv_python), "-m", "world_runtime", "serve", "--help"],
                cwd=args.work_dir,
                env=env,
                label="module-entrypoint-help",
            )
        )
        if command_results[-1]["returncode"] != 0:
            errors.append("python -m world_runtime serve --help failed")

    if not errors:
        command_results.append(
            _run_command(
                [str(world_runtime_bin), "serve", "--help"],
                cwd=args.work_dir,
                env=env,
                label="console-entrypoint-help",
            )
        )
        if command_results[-1]["returncode"] != 0:
            errors.append("world-runtime serve --help failed")

    installed_version = None
    if not errors:
        version_result = _run_command(
            [
                str(venv_python),
                "-c",
                "import importlib.metadata; print(importlib.metadata.version('world-runtime'))",
            ],
            cwd=args.work_dir,
            env=env,
            label="installed-version",
        )
        command_results.append(version_result)
        if version_result["returncode"] != 0:
            errors.append("failed to read installed package version")
        else:
            installed_version = version_result["stdout_tail"].strip()
            if installed_version != expected_version:
                errors.append(
                    "installed package version mismatch: expected %s got %s"
                    % (expected_version, installed_version)
                )

    server_process: Optional[subprocess.Popen[str]] = None
    health_payload = None
    meta_payload = None
    example_result = None
    server_stdout_tail = ""
    server_stderr_tail = ""
    try:
        if not errors:
            server_process = subprocess.Popen(
                [
                    str(world_runtime_bin),
                    "serve",
                    "--profile",
                    "local",
                    "--host",
                    args.host,
                    "--port",
                    str(args.port),
                ],
                cwd=args.work_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            health_payload = _wait_for_json(base_url + "/health", args.timeout_seconds)
            meta_payload = _fetch_json(base_url + "/v1/meta")
            example_result = _run_command(
                [str(venv_python), str(EXAMPLE_SCRIPT)],
                cwd=args.work_dir,
                env={
                    **env,
                    "WORLD_RUNTIME_API_BASE_URL": base_url,
                },
                label="consumer-example",
            )
            command_results.append(example_result)
            if example_result["returncode"] != 0:
                errors.append("consumer example script failed")
    except Exception as exc:  # pragma: no cover - exercised in smoke runs
        errors.append(str(exc))
    finally:
        if server_process is not None:
            server_process.terminate()
            try:
                stdout, stderr = server_process.communicate(timeout=10.0)
            except subprocess.TimeoutExpired:
                server_process.kill()
                stdout, stderr = server_process.communicate(timeout=10.0)
            server_stdout_tail = stdout[-2000:]
            server_stderr_tail = stderr[-2000:]

    payload = {
        "milestone": "M26",
        "gate": "consumer-boundary",
        "started_at": started_at,
        "completed_at": utc_now(),
        "package_source": str(args.package_source),
        "expected_version": expected_version,
        "installed_version": installed_version,
        "base_url": base_url,
        "health": health_payload,
        "meta": meta_payload,
        "server_stdout_tail": server_stdout_tail,
        "server_stderr_tail": server_stderr_tail,
        "command_results": command_results,
        "errors": errors,
        "status": "passed" if not errors else "failed",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

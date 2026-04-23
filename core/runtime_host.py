from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
from urllib import error, request

from core.observability import ObservabilityStore
from core.runtime_host_state import (
    LogCapturePolicy,
    ProbeResult,
    ProbeSpec,
    ProcessSpec,
    RestartPolicy,
    RuntimeHostStateStore,
    ServiceManifest,
    ServiceOutput,
    utc_now,
)


PLACEHOLDER_RE = re.compile(r"\$\{([A-Z0-9_]+)\}")


@dataclass
class _ManagedProcess:
    manifest: ServiceManifest
    process: subprocess.Popen[str]
    stdout_handle: Optional[Any]
    stderr_handle: Optional[Any]


class RuntimeHost:
    def __init__(
        self,
        repo_root: Path,
        observability: Optional[ObservabilityStore] = None,
        environment: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.observability = observability or ObservabilityStore()
        self.environment = dict(environment or {})
        self.state_store = RuntimeHostStateStore()
        self._manifests: Dict[str, ServiceManifest] = {}
        self._processes: Dict[str, _ManagedProcess] = {}

    def __enter__(self) -> "RuntimeHost":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop_all(reason="context_exit")

    def load_manifest(self, manifest_path: Path, environment: Optional[Mapping[str, str]] = None) -> ServiceManifest:
        path = Path(manifest_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        resolved_payload = self._expand_payload(
            payload,
            {
                **os.environ,
                **self.environment,
                **(environment or {}),
                "REPO_ROOT": str(self.repo_root),
                "PYTHON": (
                    dict(environment or {}).get("PYTHON")
                    or self.environment.get("PYTHON")
                    or os.environ.get("PYTHON")
                    or os.environ.get("PYTHON3")
                    or "python3"
                ),
            },
        )

        manifest = _parse_manifest(path=path, payload=resolved_payload)
        self._manifests[manifest.service_id] = manifest
        return manifest

    def load_manifests(
        self,
        manifest_paths: Iterable[Path],
        environment: Optional[Mapping[str, str]] = None,
    ) -> Dict[str, ServiceManifest]:
        manifests = {}
        for manifest_path in manifest_paths:
            manifest = self.load_manifest(manifest_path, environment=environment)
            manifests[manifest.service_id] = manifest
        return manifests

    def reconcile(
        self,
        manifests: Optional[Iterable[ServiceManifest]] = None,
        *,
        prune: bool = True,
    ) -> Dict[str, Dict[str, Any]]:
        desired_manifests = self._desired_manifest_map(manifests)
        desired_ids = set(desired_manifests)

        if prune:
            for service_id in list(self._processes):
                if service_id not in desired_ids:
                    self.stop(service_id, reason="removed_from_desired_state")

        ordered_ids = _topological_sort(desired_manifests)
        for service_id in ordered_ids:
            manifest = desired_manifests[service_id]
            self._manifests[service_id] = manifest
            previous_state = self.state_store.get(service_id)
            previous_digest = previous_state.manifest_digest if previous_state is not None else None
            state = self.state_store.bind_manifest(manifest)
            dependency_errors = [
                dependency_id
                for dependency_id in manifest.dependencies
                if self.state_store.require(dependency_id).lifecycle_state != "ready"
            ]
            if dependency_errors:
                message = "dependencies not ready: %s" % ", ".join(dependency_errors)
                self._mark_failure(manifest, state, reason=message, restartable=False)
                continue

            process_entry = self._processes.get(service_id)
            if process_entry is not None:
                if previous_digest is not None and previous_digest != manifest.manifest_digest:
                    self.restart(service_id, reason="manifest_changed")
                    continue
                if process_entry.process.poll() is not None:
                    exit_code = process_entry.process.returncode
                    self._handle_runtime_failure(
                        manifest,
                        state,
                        reason="process exited with code %s" % exit_code,
                        exit_code=exit_code,
                    )
                    continue
                self.check_health(service_id)
                continue

            self._start_with_restart_policy(manifest)

        return self.inspect()

    def start(self, service_id: str) -> Dict[str, Any]:
        manifest = self._require_manifest(service_id)
        self._start_with_restart_policy(manifest)
        return self.inspect(service_id)

    def stop(self, service_id: str, reason: str = "requested") -> Dict[str, Any]:
        state = self.state_store.require(service_id)
        state.record_transition("stopping", {"reason": reason})
        process_entry = self._processes.pop(service_id, None)
        if process_entry is None:
            state.record_transition("stopped", {"reason": reason, "already_stopped": True})
            state.readiness = "not_ready"
            state.health = "stopped"
            state.pid = None
            state.stopped_at = utc_now()
            self._emit_event("service_stopped", service_id, {"reason": reason, "already_stopped": True})
            return state.as_dict()

        process = process_entry.process
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5.0)

        exit_code = process.returncode
        state.pid = None
        state.readiness = "not_ready"
        state.health = "stopped"
        state.last_exit_code = exit_code
        state.stopped_at = utc_now()
        state.record_transition("stopped", {"reason": reason, "exit_code": exit_code})
        self._close_log_handles(process_entry)
        self._emit_event("service_stopped", service_id, {"reason": reason, "exit_code": exit_code})
        return state.as_dict()

    def restart(self, service_id: str, reason: str = "requested") -> Dict[str, Any]:
        manifest = self._require_manifest(service_id)
        self.stop(service_id, reason="restart_requested:%s" % reason)
        state = self.state_store.require(service_id)
        state.restart_count += 1
        self._emit_event(
            "service_restarted",
            service_id,
            {"reason": reason, "restart_count": state.restart_count},
        )
        self._start_with_restart_policy(manifest, is_restart=True)
        return self.inspect(service_id)

    def check_health(self, service_id: str) -> Dict[str, Any]:
        manifest = self._require_manifest(service_id)
        state = self.state_store.require(service_id)
        process_entry = self._processes.get(service_id)
        if process_entry is None:
            return state.as_dict()

        process = process_entry.process
        if process.poll() is not None:
            exit_code = process.returncode
            self._handle_runtime_failure(
                manifest,
                state,
                reason="process exited with code %s" % exit_code,
                exit_code=exit_code,
            )
            return state.as_dict()

        if manifest.health_probe is None:
            state.health = "healthy"
            return state.as_dict()

        result = self._run_probe(manifest, "health", manifest.health_probe)
        state.record_probe_result(result)
        if result.ok:
            state.health = "healthy"
            return state.as_dict()

        self._handle_runtime_failure(
            manifest,
            state,
            reason="health probe failed: %s" % result.message,
            exit_code=None,
        )
        return state.as_dict()

    def inspect(self, service_id: Optional[str] = None) -> Dict[str, Any]:
        if service_id is not None:
            return self.state_store.require(service_id).as_dict()
        return self.state_store.snapshots()

    def stop_all(self, reason: str = "requested") -> Dict[str, Dict[str, Any]]:
        for service_id in list(self._processes):
            self.stop(service_id, reason=reason)
        return self.inspect()

    def _desired_manifest_map(
        self,
        manifests: Optional[Iterable[ServiceManifest]],
    ) -> Dict[str, ServiceManifest]:
        if manifests is None:
            return dict(self._manifests)
        desired = {}
        for manifest in manifests:
            desired[manifest.service_id] = manifest
        return desired

    def _require_manifest(self, service_id: str) -> ServiceManifest:
        manifest = self._manifests.get(service_id)
        if manifest is None:
            raise KeyError("unknown service manifest: %s" % service_id)
        return manifest

    def _expand_payload(self, value: Any, environment: Mapping[str, str]) -> Any:
        if isinstance(value, dict):
            return {key: self._expand_payload(item, environment) for key, item in value.items()}
        if isinstance(value, list):
            return [self._expand_payload(item, environment) for item in value]
        if not isinstance(value, str):
            return value

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in environment:
                raise ValueError("missing manifest environment variable: %s" % key)
            return str(environment[key])

        return PLACEHOLDER_RE.sub(replace, value)

    def _start_with_restart_policy(self, manifest: ServiceManifest, is_restart: bool = False) -> None:
        state = self.state_store.bind_manifest(manifest)
        attempts_remaining = max(manifest.restart_policy.max_attempts - state.restart_count, 0)

        while True:
            launch_reason = "restart" if is_restart or state.restart_count else "initial"
            self._emit_event(
                "service_start_requested",
                manifest.service_id,
                {
                    "launch_reason": launch_reason,
                    "manifest_path": manifest.manifest_path,
                },
            )
            self._spawn_process(manifest, state)
            readiness_result = self._wait_for_readiness(manifest, state)
            if readiness_result.ok:
                state.record_probe_result(readiness_result)
                state.readiness = "ready"
                state.health = "healthy" if manifest.health_probe is not None else "unknown"
                state.record_transition("ready", {"pid": state.pid})
                self._emit_event("service_ready", manifest.service_id, {"pid": state.pid})
                return

            self._teardown_process(manifest.service_id)
            state.record_probe_result(readiness_result)
            restartable = self._can_restart(manifest, attempts_remaining, failure_reason=readiness_result.message)
            self._mark_failure(manifest, state, reason=readiness_result.message, restartable=restartable)
            if not restartable:
                return

            attempts_remaining -= 1
            state.restart_count += 1
            self._emit_event(
                "service_restarted",
                manifest.service_id,
                {
                    "reason": readiness_result.message,
                    "restart_count": state.restart_count,
                },
            )
            if manifest.restart_policy.backoff_seconds > 0:
                time.sleep(manifest.restart_policy.backoff_seconds)
            is_restart = True

    def _spawn_process(self, manifest: ServiceManifest, state) -> None:
        stdout_handle, stderr_handle, capture_details = self._prepare_log_capture(manifest)
        env = os.environ.copy()
        env.update(manifest.process.environment)

        process = subprocess.Popen(
            manifest.process.argv(),
            cwd=manifest.process.working_directory or str(self.repo_root),
            env=env,
            text=True,
            stdout=stdout_handle,
            stderr=stderr_handle,
        )

        self._processes[manifest.service_id] = _ManagedProcess(
            manifest=manifest,
            process=process,
            stdout_handle=stdout_handle,
            stderr_handle=stderr_handle,
        )
        state.pid = process.pid
        state.started_at = utc_now()
        state.readiness = "starting"
        state.health = "starting"
        state.last_error = None
        state.log_capture = capture_details
        state.record_transition("starting", {"pid": process.pid})
        self._emit_event(
            "service_started",
            manifest.service_id,
            {"pid": process.pid, "argv": manifest.process.argv()},
        )

    def _prepare_log_capture(self, manifest: ServiceManifest) -> tuple[Optional[Any], Optional[Any], Dict[str, Any]]:
        mode = manifest.log_capture.mode
        if mode == "inherit":
            return None, None, {"mode": mode}
        if mode == "discard":
            return subprocess.DEVNULL, subprocess.DEVNULL, {"mode": mode}

        log_dir = Path(manifest.log_capture.directory or (self.repo_root / "tmp" / "service_logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = log_dir / ("%s.stdout.log" % manifest.service_id)
        stderr_path = log_dir / ("%s.stderr.log" % manifest.service_id)
        stdout_handle = stdout_path.open("a", encoding="utf-8")
        stderr_handle = stderr_path.open("a", encoding="utf-8")
        return (
            stdout_handle,
            stderr_handle,
            {
                "mode": mode,
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
                "tail_lines": manifest.log_capture.tail_lines,
            },
        )

    def _teardown_process(self, service_id: str) -> None:
        process_entry = self._processes.pop(service_id, None)
        if process_entry is None:
            return

        if process_entry.process.poll() is None:
            process_entry.process.terminate()
            try:
                process_entry.process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process_entry.process.kill()
                process_entry.process.wait(timeout=5.0)
        self._close_log_handles(process_entry)

    def _wait_for_readiness(self, manifest: ServiceManifest, state) -> ProbeResult:
        if manifest.readiness_probe is None:
            return ProbeResult(
                probe_name="readiness",
                ok=True,
                checked_at=utc_now(),
                message="no readiness probe configured",
            )

        probe = manifest.readiness_probe
        if probe.initial_delay_seconds > 0:
            time.sleep(probe.initial_delay_seconds)

        deadline = time.monotonic() + max(probe.timeout_seconds, probe.interval_seconds)
        last_message = "readiness probe did not run"
        while time.monotonic() < deadline:
            process_entry = self._processes.get(manifest.service_id)
            if process_entry is None:
                return ProbeResult(
                    probe_name="readiness",
                    ok=False,
                    checked_at=utc_now(),
                    message="service process missing during readiness wait",
                )

            process = process_entry.process
            if process.poll() is not None:
                state.last_exit_code = process.returncode
                self._close_log_handles(self._processes.pop(manifest.service_id))
                return ProbeResult(
                    probe_name="readiness",
                    ok=False,
                    checked_at=utc_now(),
                    message="process exited with code %s before readiness" % process.returncode,
                    details={"exit_code": process.returncode},
                )

            result = self._run_probe(manifest, "readiness", probe)
            if result.ok:
                return result

            last_message = result.message
            state.record_probe_result(result)
            time.sleep(probe.interval_seconds)

        return ProbeResult(
            probe_name="readiness",
            ok=False,
            checked_at=utc_now(),
            message="readiness timeout after %.2fs (%s)" % (probe.timeout_seconds, last_message),
        )

    def _run_probe(self, manifest: ServiceManifest, probe_name: str, probe: ProbeSpec) -> ProbeResult:
        checked_at = utc_now()
        try:
            if probe.probe_type == "http":
                return self._run_http_probe(probe_name, probe, checked_at)
            if probe.probe_type == "command":
                env = os.environ.copy()
                env.update(manifest.process.environment)
                return self._run_command_probe(probe_name, probe, checked_at, env, manifest)
            if probe.probe_type == "tcp":
                return self._run_tcp_probe(probe_name, probe, checked_at)
        except Exception as exc:  # pragma: no cover - defensive fallback
            return ProbeResult(
                probe_name=probe_name,
                ok=False,
                checked_at=checked_at,
                message=str(exc),
            )

        return ProbeResult(
            probe_name=probe_name,
            ok=False,
            checked_at=checked_at,
            message="unsupported probe type: %s" % probe.probe_type,
        )

    def _run_http_probe(self, probe_name: str, probe: ProbeSpec, checked_at: str) -> ProbeResult:
        if not probe.url:
            return ProbeResult(probe_name=probe_name, ok=False, checked_at=checked_at, message="missing probe url")
        try:
            with request.urlopen(probe.url, timeout=probe.timeout_seconds) as response:  # noqa: S310
                body = response.read().decode("utf-8", errors="replace")
                if response.status != probe.expected_status:
                    return ProbeResult(
                        probe_name=probe_name,
                        ok=False,
                        checked_at=checked_at,
                        message="expected HTTP %s, got %s" % (probe.expected_status, response.status),
                        details={"status": response.status},
                    )
                if probe.success_contains and probe.success_contains not in body:
                    return ProbeResult(
                        probe_name=probe_name,
                        ok=False,
                        checked_at=checked_at,
                        message='response missing "%s"' % probe.success_contains,
                    )
                return ProbeResult(
                    probe_name=probe_name,
                    ok=True,
                    checked_at=checked_at,
                    message="HTTP probe succeeded",
                    details={"status": response.status},
                )
        except error.HTTPError as exc:
            return ProbeResult(
                probe_name=probe_name,
                ok=False,
                checked_at=checked_at,
                message="HTTP error %s" % exc.code,
                details={"status": exc.code},
            )
        except OSError as exc:
            return ProbeResult(
                probe_name=probe_name,
                ok=False,
                checked_at=checked_at,
                message=str(exc),
            )

    def _run_command_probe(
        self,
        probe_name: str,
        probe: ProbeSpec,
        checked_at: str,
        environment: Dict[str, str],
        manifest: ServiceManifest,
    ) -> ProbeResult:
        if not probe.command:
            return ProbeResult(probe_name=probe_name, ok=False, checked_at=checked_at, message="missing command")
        result = subprocess.run(
            probe.command,
            cwd=manifest.process.working_directory or str(self.repo_root),
            env=environment,
            text=True,
            capture_output=True,
            check=False,
            timeout=probe.timeout_seconds,
        )
        if result.returncode != 0:
            return ProbeResult(
                probe_name=probe_name,
                ok=False,
                checked_at=checked_at,
                message="command returned %s" % result.returncode,
                details={"returncode": result.returncode, "stderr_tail": result.stderr[-500:]},
            )
        if probe.success_contains and probe.success_contains not in result.stdout:
            return ProbeResult(
                probe_name=probe_name,
                ok=False,
                checked_at=checked_at,
                message='command output missing "%s"' % probe.success_contains,
            )
        return ProbeResult(
            probe_name=probe_name,
            ok=True,
            checked_at=checked_at,
            message="command probe succeeded",
            details={"stdout_tail": result.stdout[-500:]},
        )

    def _run_tcp_probe(self, probe_name: str, probe: ProbeSpec, checked_at: str) -> ProbeResult:
        if not probe.host or probe.port is None:
            return ProbeResult(
                probe_name=probe_name,
                ok=False,
                checked_at=checked_at,
                message="missing TCP host/port",
            )
        try:
            with socket.create_connection((probe.host, probe.port), timeout=probe.timeout_seconds):
                return ProbeResult(
                    probe_name=probe_name,
                    ok=True,
                    checked_at=checked_at,
                    message="TCP probe succeeded",
                    details={"host": probe.host, "port": probe.port},
                )
        except OSError as exc:
            return ProbeResult(
                probe_name=probe_name,
                ok=False,
                checked_at=checked_at,
                message=str(exc),
            )

    def _handle_runtime_failure(
        self,
        manifest: ServiceManifest,
        state,
        reason: str,
        exit_code: Optional[int],
    ) -> None:
        process_entry = self._processes.pop(manifest.service_id, None)
        if process_entry is not None:
            if process_entry.process.poll() is None:
                process_entry.process.terminate()
                try:
                    process_entry.process.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    process_entry.process.kill()
                    process_entry.process.wait(timeout=5.0)
            self._close_log_handles(process_entry)

        if exit_code is not None:
            state.last_exit_code = exit_code
        restartable = self._can_restart(
            manifest,
            manifest.restart_policy.max_attempts - state.restart_count,
            failure_reason=reason,
        )
        self._mark_failure(manifest, state, reason=reason, restartable=restartable)
        if not restartable:
            return

        state.restart_count += 1
        self._emit_event(
            "service_restarted",
            manifest.service_id,
            {"reason": reason, "restart_count": state.restart_count},
        )
        if manifest.restart_policy.backoff_seconds > 0:
            time.sleep(manifest.restart_policy.backoff_seconds)
        self._start_with_restart_policy(manifest, is_restart=True)

    def _mark_failure(self, manifest: ServiceManifest, state, reason: str, restartable: bool) -> None:
        state.last_error = reason
        state.last_failure_reason = reason
        state.readiness = "not_ready"
        state.health = "failed"
        state.pid = None
        state.stopped_at = utc_now()
        state.record_transition(
            "failed",
            {
                "reason": reason,
                "restartable": restartable,
            },
        )
        self._emit_event(
            "service_failed",
            manifest.service_id,
            {"reason": reason, "restartable": restartable},
            severity="error",
        )

    def _can_restart(
        self,
        manifest: ServiceManifest,
        attempts_remaining: int,
        failure_reason: Optional[str],
    ) -> bool:
        if failure_reason is None:
            return False
        if manifest.restart_policy.condition == "never":
            return False
        if manifest.restart_policy.condition == "always":
            return attempts_remaining > 0
        return attempts_remaining > 0

    def _close_log_handles(self, process_entry: _ManagedProcess) -> None:
        for handle in (process_entry.stdout_handle, process_entry.stderr_handle):
            if handle in (None, subprocess.DEVNULL):
                continue
            try:
                handle.flush()
                handle.close()
            except Exception:  # pragma: no cover - defensive cleanup
                pass

    def _emit_event(
        self,
        event_type: str,
        service_id: str,
        attributes: Optional[Dict[str, Any]] = None,
        severity: str = "info",
    ) -> None:
        self.observability.emit(
            component="runtime_host",
            event_type=event_type,
            severity=severity,
            attributes={"service_id": service_id, **dict(attributes or {})},
        )


def load_service_manifest(
    manifest_path: Path,
    repo_root: Path,
    environment: Optional[Mapping[str, str]] = None,
) -> ServiceManifest:
    with RuntimeHost(repo_root=repo_root, environment=environment) as host:
        return host.load_manifest(manifest_path)


def _parse_manifest(path: Path, payload: Dict[str, Any]) -> ServiceManifest:
    service_id = _require_string(payload, "service_id")
    process_payload = _require_mapping(payload, "process")
    process = ProcessSpec(
        executable=_require_string(process_payload, "executable"),
        arguments=_string_list(process_payload.get("arguments", []), "process.arguments"),
        working_directory=_optional_string(process_payload.get("working_directory")),
        environment=_string_mapping(process_payload.get("environment", {}), "process.environment"),
    )

    outputs = []
    for index, item in enumerate(payload.get("outputs", [])):
        if not isinstance(item, dict):
            raise ValueError("outputs[%d] must be an object" % index)
        outputs.append(
            ServiceOutput(
                name=_require_string(item, "name"),
                output_type=_require_string(item, "type"),
                value=_require_string(item, "value"),
            )
        )

    restart_payload = _require_mapping(payload, "restart_policy")
    manifest_dict = {
        "service_id": service_id,
        "display_name": _optional_string(payload.get("display_name")),
        "description": _optional_string(payload.get("description")),
        "process": {
            "executable": process.executable,
            "arguments": list(process.arguments),
            "working_directory": process.working_directory,
            "environment": dict(process.environment),
        },
        "dependencies": _string_list(payload.get("dependencies", []), "dependencies"),
        "readiness_probe": payload.get("readiness_probe"),
        "health_probe": payload.get("health_probe"),
        "restart_policy": {
            "condition": _require_string(restart_payload, "condition"),
            "max_attempts": _require_int(restart_payload, "max_attempts", minimum=0),
            "backoff_seconds": _require_number(restart_payload, "backoff_seconds", minimum=0.0),
        },
        "outputs": [output.as_dict() for output in outputs],
        "log_capture": payload.get("log_capture", {}),
    }

    digest = hashlib.sha256(json.dumps(manifest_dict, sort_keys=True).encode("utf-8")).hexdigest()
    log_capture_payload = _require_mapping(payload, "log_capture")
    return ServiceManifest(
        service_id=service_id,
        manifest_path=str(path),
        manifest_digest=digest,
        display_name=_optional_string(payload.get("display_name")),
        description=_optional_string(payload.get("description")),
        process=process,
        dependencies=_string_list(payload.get("dependencies", []), "dependencies"),
        readiness_probe=_parse_probe(payload.get("readiness_probe"), "readiness_probe"),
        health_probe=_parse_probe(payload.get("health_probe"), "health_probe"),
        restart_policy=RestartPolicy(
            condition=_require_string(restart_payload, "condition"),
            max_attempts=_require_int(restart_payload, "max_attempts", minimum=0),
            backoff_seconds=_require_number(restart_payload, "backoff_seconds", minimum=0.0),
        ),
        outputs=outputs,
        log_capture=LogCapturePolicy(
            mode=_require_string(log_capture_payload, "mode"),
            directory=_optional_string(log_capture_payload.get("directory")),
            tail_lines=_require_int(log_capture_payload, "tail_lines", minimum=1),
        ),
    )


def _parse_probe(value: Any, field_name: str) -> Optional[ProbeSpec]:
    if value is None:
        return None
    payload = _require_mapping_obj(value, field_name)
    probe_type = _require_string(payload, "type")
    return ProbeSpec(
        probe_type=probe_type,
        interval_seconds=_require_number(payload, "interval_seconds", minimum=0.05),
        timeout_seconds=_require_number(payload, "timeout_seconds", minimum=0.1),
        initial_delay_seconds=_require_number(payload, "initial_delay_seconds", minimum=0.0),
        expected_status=_require_optional_int(payload.get("expected_status"), default=200, minimum=100),
        url=_optional_string(payload.get("url")),
        command=_string_list(payload.get("command", []), "%s.command" % field_name),
        host=_optional_string(payload.get("host")),
        port=_optional_int(payload.get("port"), minimum=1, maximum=65535),
        success_contains=_optional_string(payload.get("success_contains")),
    )


def _topological_sort(manifests: Mapping[str, ServiceManifest]) -> List[str]:
    ordered: List[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(service_id: str) -> None:
        if service_id in visited:
            return
        if service_id in visiting:
            raise ValueError("service dependency cycle detected at %s" % service_id)
        if service_id not in manifests:
            raise ValueError("service dependency missing manifest: %s" % service_id)

        visiting.add(service_id)
        manifest = manifests[service_id]
        for dependency_id in manifest.dependencies:
            visit(dependency_id)
        visiting.remove(service_id)
        visited.add(service_id)
        ordered.append(service_id)

    for service_id in sorted(manifests):
        visit(service_id)
    return ordered


def _require_mapping(payload: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError("%s must be an object" % key)
    return value


def _require_mapping_obj(value: Any, key: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("%s must be an object" % key)
    return value


def _require_string(payload: Dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError("%s must be a non-empty string" % key)
    return value


def _optional_string(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("expected string value")
    return value


def _string_list(value: Any, key: str) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("%s must be an array of strings" % key)
    items = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            raise ValueError("%s[%d] must be a non-empty string" % (key, index))
        items.append(item)
    return items


def _string_mapping(value: Any, key: str) -> Dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("%s must be an object of string values" % key)
    items = {}
    for item_key, item_value in value.items():
        if not isinstance(item_key, str) or not isinstance(item_value, str):
            raise ValueError("%s entries must map strings to strings" % key)
        items[item_key] = item_value
    return items


def _require_int(payload: Dict[str, Any], key: str, minimum: int = 0) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError("%s must be an integer" % key)
    if value < minimum:
        raise ValueError("%s must be >= %s" % (key, minimum))
    return value


def _optional_int(value: Any, minimum: int = 0, maximum: Optional[int] = None) -> Optional[int]:
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError("expected integer value")
    if value < minimum:
        raise ValueError("integer value must be >= %s" % minimum)
    if maximum is not None and value > maximum:
        raise ValueError("integer value must be <= %s" % maximum)
    return value


def _require_optional_int(value: Any, default: int, minimum: int = 0) -> int:
    if value is None:
        return default
    if not isinstance(value, int):
        raise ValueError("expected integer value")
    if value < minimum:
        raise ValueError("integer value must be >= %s" % minimum)
    return value


def _require_number(payload: Dict[str, Any], key: str, minimum: float = 0.0) -> float:
    value = payload.get(key)
    if not isinstance(value, (int, float)):
        raise ValueError("%s must be a number" % key)
    number = float(value)
    if number < minimum:
        raise ValueError("%s must be >= %s" % (key, minimum))
    return number

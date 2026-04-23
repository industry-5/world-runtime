from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ProcessSpec:
    executable: str
    arguments: List[str] = field(default_factory=list)
    working_directory: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)

    def argv(self) -> List[str]:
        return [self.executable, *self.arguments]


@dataclass(frozen=True)
class ProbeSpec:
    probe_type: str
    interval_seconds: float = 0.5
    timeout_seconds: float = 5.0
    initial_delay_seconds: float = 0.0
    expected_status: int = 200
    url: Optional[str] = None
    command: List[str] = field(default_factory=list)
    host: Optional[str] = None
    port: Optional[int] = None
    success_contains: Optional[str] = None


@dataclass(frozen=True)
class RestartPolicy:
    condition: str = "on_failure"
    max_attempts: int = 0
    backoff_seconds: float = 0.0


@dataclass(frozen=True)
class LogCapturePolicy:
    mode: str = "file"
    directory: Optional[str] = None
    tail_lines: int = 80


@dataclass(frozen=True)
class ServiceOutput:
    name: str
    output_type: str
    value: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.output_type,
            "value": self.value,
        }


@dataclass(frozen=True)
class ServiceManifest:
    service_id: str
    manifest_path: str
    manifest_digest: str
    display_name: Optional[str]
    description: Optional[str]
    process: ProcessSpec
    dependencies: List[str] = field(default_factory=list)
    readiness_probe: Optional[ProbeSpec] = None
    health_probe: Optional[ProbeSpec] = None
    restart_policy: RestartPolicy = field(default_factory=RestartPolicy)
    outputs: List[ServiceOutput] = field(default_factory=list)
    log_capture: LogCapturePolicy = field(default_factory=LogCapturePolicy)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "manifest_path": self.manifest_path,
            "manifest_digest": self.manifest_digest,
            "display_name": self.display_name,
            "description": self.description,
            "process": {
                "executable": self.process.executable,
                "arguments": list(self.process.arguments),
                "working_directory": self.process.working_directory,
                "environment": dict(self.process.environment),
            },
            "dependencies": list(self.dependencies),
            "readiness_probe": _probe_to_dict(self.readiness_probe),
            "health_probe": _probe_to_dict(self.health_probe),
            "restart_policy": {
                "condition": self.restart_policy.condition,
                "max_attempts": self.restart_policy.max_attempts,
                "backoff_seconds": self.restart_policy.backoff_seconds,
            },
            "outputs": [output.as_dict() for output in self.outputs],
            "log_capture": {
                "mode": self.log_capture.mode,
                "directory": self.log_capture.directory,
                "tail_lines": self.log_capture.tail_lines,
            },
        }


@dataclass
class ProbeResult:
    probe_name: str
    ok: bool
    checked_at: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "probe_name": self.probe_name,
            "ok": self.ok,
            "checked_at": self.checked_at,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass
class ServiceRuntimeState:
    service_id: str
    manifest_path: str
    manifest_digest: str
    lifecycle_state: str = "stopped"
    pid: Optional[int] = None
    restart_count: int = 0
    readiness: str = "unknown"
    health: str = "unknown"
    started_at: Optional[str] = None
    stopped_at: Optional[str] = None
    last_transition_at: Optional[str] = None
    last_error: Optional[str] = None
    last_failure_reason: Optional[str] = None
    last_exit_code: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    log_capture: Dict[str, Any] = field(default_factory=dict)
    last_probe_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def record_transition(self, lifecycle_state: str, details: Optional[Dict[str, Any]] = None) -> None:
        at = utc_now()
        self.lifecycle_state = lifecycle_state
        self.last_transition_at = at
        self.history.append(
            {
                "kind": "transition",
                "at": at,
                "state": lifecycle_state,
                "details": dict(details or {}),
            }
        )

    def record_probe_result(self, result: ProbeResult) -> None:
        self.last_probe_results[result.probe_name] = result.as_dict()
        self.history.append(
            {
                "kind": "probe",
                "at": result.checked_at,
                "probe_name": result.probe_name,
                "ok": result.ok,
                "message": result.message,
                "details": dict(result.details),
            }
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "manifest_path": self.manifest_path,
            "manifest_digest": self.manifest_digest,
            "lifecycle_state": self.lifecycle_state,
            "pid": self.pid,
            "restart_count": self.restart_count,
            "readiness": self.readiness,
            "health": self.health,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "last_transition_at": self.last_transition_at,
            "last_error": self.last_error,
            "last_failure_reason": self.last_failure_reason,
            "last_exit_code": self.last_exit_code,
            "dependencies": list(self.dependencies),
            "outputs": [dict(output) for output in self.outputs],
            "log_capture": dict(self.log_capture),
            "last_probe_results": {key: dict(value) for key, value in self.last_probe_results.items()},
            "history": [dict(item) for item in self.history],
        }


class RuntimeHostStateStore:
    def __init__(self) -> None:
        self._states: Dict[str, ServiceRuntimeState] = {}

    def bind_manifest(self, manifest: ServiceManifest) -> ServiceRuntimeState:
        state = self._states.get(manifest.service_id)
        if state is None:
            state = ServiceRuntimeState(
                service_id=manifest.service_id,
                manifest_path=manifest.manifest_path,
                manifest_digest=manifest.manifest_digest,
            )
            self._states[manifest.service_id] = state
        state.manifest_path = manifest.manifest_path
        state.manifest_digest = manifest.manifest_digest
        state.dependencies = list(manifest.dependencies)
        state.outputs = [output.as_dict() for output in manifest.outputs]
        return state

    def get(self, service_id: str) -> Optional[ServiceRuntimeState]:
        return self._states.get(service_id)

    def require(self, service_id: str) -> ServiceRuntimeState:
        state = self.get(service_id)
        if state is None:
            raise KeyError("unknown service: %s" % service_id)
        return state

    def delete(self, service_id: str) -> None:
        self._states.pop(service_id, None)

    def list_states(self) -> List[ServiceRuntimeState]:
        return [self._states[key] for key in sorted(self._states)]

    def snapshots(self) -> Dict[str, Dict[str, Any]]:
        return {service_id: state.as_dict() for service_id, state in sorted(self._states.items())}


def _probe_to_dict(probe: Optional[ProbeSpec]) -> Optional[Dict[str, Any]]:
    if probe is None:
        return None
    return {
        "type": probe.probe_type,
        "interval_seconds": probe.interval_seconds,
        "timeout_seconds": probe.timeout_seconds,
        "initial_delay_seconds": probe.initial_delay_seconds,
        "expected_status": probe.expected_status,
        "url": probe.url,
        "command": list(probe.command),
        "host": probe.host,
        "port": probe.port,
        "success_contains": probe.success_contains,
    }

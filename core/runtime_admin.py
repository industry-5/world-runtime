from __future__ import annotations

import hashlib
import json
import re
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4

from core.observability import ObservabilityStore
from core.policy_engine import DeterministicPolicyEngine
from core.provider_registry import ProviderBinding, ProviderRegistry, ProviderRegistryLoader
from core.routing_policy import RoutingPolicyInput
from core.runtime_host import RuntimeHost
from core.task_profiles import TaskProfileCatalog, TaskProfileLoader
from core.task_router import TaskRouter


PLACEHOLDER_RE = re.compile(r"\$\{([A-Z0-9_]+)\}")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _manifest_digest(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class RuntimeAdminSurface:
    def __init__(
        self,
        repo_root: Path,
        *,
        observability: Optional[ObservabilityStore] = None,
        policy_engine: Optional[DeterministicPolicyEngine] = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.observability = observability or ObservabilityStore()
        self.policy_engine = policy_engine or DeterministicPolicyEngine()
        self.runtime_host = RuntimeHost(
            self.repo_root,
            observability=self.observability,
            environment={"PYTHON": sys.executable},
        )
        self.provider_registry = self._load_provider_registry()
        self.task_catalog = self._load_task_catalog()
        self.task_router = TaskRouter(
            self.provider_registry,
            self.task_catalog,
            observability=self.observability,
        )
        self._service_inventory = self._load_service_inventory()
        self._environment_cache: Dict[str, Dict[str, str]] = {}
        self._port_cache: Dict[str, int] = {}

    def inventory_summary(self) -> Dict[str, Any]:
        services = self.list_services()["services"]
        providers = self.list_providers()["providers"]
        task_profile_ids = self.task_catalog.list_profile_ids()

        state_totals: Dict[str, int] = {}
        for service in services:
            lifecycle_state = service["lifecycle_state"]
            state_totals[lifecycle_state] = state_totals.get(lifecycle_state, 0) + 1

        return {
            "generated_at": _utc_now(),
            "services": {
                "count": len(services),
                "service_ids": [service["service_id"] for service in services],
                "by_state": state_totals,
            },
            "providers": {
                "count": len(providers),
                "provider_ids": [provider["provider_id"] for provider in providers],
            },
            "task_profiles": {
                "count": len(task_profile_ids),
                "task_profile_ids": task_profile_ids,
            },
        }

    def list_services(self) -> Dict[str, Any]:
        services = [
            self._service_snapshot(service_id)
            for service_id in sorted(self._service_inventory)
        ]
        return {
            "services": services,
            "count": len(services),
        }

    def get_service(self, service_id: str) -> Dict[str, Any]:
        entry = self._require_service_inventory(service_id)
        manifest = self._load_manifest(service_id)
        return {
            "service": {
                **self._service_snapshot(service_id),
                "manifest": manifest.as_dict(),
                "manifest_placeholders": sorted(entry["placeholders"]),
            }
        }

    def reconcile_services(
        self,
        *,
        actor: Dict[str, Any],
        service_ids: Optional[Iterable[str]] = None,
        session_id: Optional[str] = None,
        prune: bool = False,
    ) -> Dict[str, Any]:
        normalized_service_ids = sorted(
            set(service_ids or self._service_inventory.keys())
        )
        self._validate_actor(actor)
        for service_id in normalized_service_ids:
            self._require_service_inventory(service_id)

        action_id = "runtime_admin.%s" % uuid4().hex[:12]
        proposal = {
            "proposal_id": "proposal.%s" % action_id,
            "proposer": actor["actor_id"],
            "proposed_action": {
                "action_type": "runtime_service_reconcile",
                "target_ref": "runtime.services",
                "payload": {
                    "service_ids": normalized_service_ids,
                    "prune": prune,
                },
            },
            "rationale": "Runtime-admin reconcile requested through supported surface.",
        }
        policy_report = self.policy_engine.evaluate_policies(
            [
                {
                    "policy_id": "policy.runtime-admin.reconcile",
                    "policy_name": "runtime_admin_reconcile_default_allow",
                    "default_outcome": "allow",
                    "rules": [],
                }
            ],
            proposal,
        ).as_dict()

        trace_id = self.observability.start_trace(
            name="runtime_admin.reconcile",
            component="runtime_admin",
            context={
                "action_id": action_id,
                "service_ids": normalized_service_ids,
                "session_id": session_id,
                "actor_id": actor["actor_id"],
                "prune": prune,
            },
        )
        self.observability.emit(
            component="runtime_admin",
            event_type="runtime_admin.reconcile.requested",
            trace_id=trace_id,
            session_id=session_id,
            attributes={
                "action_id": action_id,
                "service_ids": normalized_service_ids,
                "actor_id": actor["actor_id"],
                "prune": prune,
            },
        )

        try:
            manifests = [self._load_manifest(service_id) for service_id in normalized_service_ids]
            snapshots = self.runtime_host.reconcile(manifests, prune=prune)
            reconciled = [snapshots[service_id] for service_id in normalized_service_ids]
            self.observability.emit(
                component="runtime_admin",
                event_type="runtime_admin.reconcile.completed",
                trace_id=trace_id,
                session_id=session_id,
                attributes={
                    "action_id": action_id,
                    "service_ids": normalized_service_ids,
                    "actor_id": actor["actor_id"],
                    "prune": prune,
                },
            )
            self.observability.finish_trace(
                trace_id,
                status="completed",
                extra={
                    "action_id": action_id,
                    "service_ids": normalized_service_ids,
                },
            )
            return {
                "action_id": action_id,
                "requested_at": _utc_now(),
                "session_id": session_id,
                "actor": json.loads(json.dumps(actor)),
                "service_ids": normalized_service_ids,
                "prune": prune,
                "policy_report": policy_report,
                "services": reconciled,
                "proposal": proposal,
            }
        except Exception as exc:
            self.observability.emit(
                component="runtime_admin",
                event_type="runtime_admin.reconcile.failed",
                severity="error",
                trace_id=trace_id,
                session_id=session_id,
                attributes={
                    "action_id": action_id,
                    "service_ids": normalized_service_ids,
                    "actor_id": actor["actor_id"],
                    "error": str(exc),
                },
            )
            self.observability.finish_trace(trace_id, status="failed", error=str(exc))
            raise

    def list_providers(self) -> Dict[str, Any]:
        service_states = self.runtime_host.inspect()
        providers = [
            self._provider_snapshot(binding, service_states)
            for binding in self.provider_registry.bindings()
        ]
        return {
            "providers": providers,
            "count": len(providers),
        }

    def get_provider(self, provider_id: str) -> Dict[str, Any]:
        service_states = self.runtime_host.inspect()
        binding = self.provider_registry.get(provider_id)
        return {
            "provider": self._provider_snapshot(binding, service_states)
        }

    def resolve_task(
        self,
        *,
        task_profile_id: str,
        policy_input: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        profile = self.task_catalog.get(task_profile_id)
        service_states = self.runtime_host.inspect()
        decision = self.task_router.route(
            profile,
            service_states=service_states,
            policy_input=RoutingPolicyInput.from_dict(policy_input),
        )
        return {
            "task_profile": profile.as_dict(),
            "service_states": service_states,
            "decision": decision.as_dict(),
        }

    def close(self) -> None:
        self.runtime_host.stop_all(reason="runtime_admin_shutdown")

    def _load_provider_registry(self) -> ProviderRegistry:
        provider_dir = self.repo_root / "infra" / "provider_bindings"
        if not provider_dir.exists():
            return ProviderRegistry([])
        return ProviderRegistryLoader(self.repo_root).load_all()

    def _load_task_catalog(self) -> TaskProfileCatalog:
        task_dir = self.repo_root / "infra" / "task_profiles"
        if not task_dir.exists():
            return TaskProfileCatalog([])
        return TaskProfileLoader(self.repo_root).load_all()

    def _load_service_inventory(self) -> Dict[str, Dict[str, Any]]:
        service_dir = self.repo_root / "infra" / "service_manifests"
        if not service_dir.exists():
            return {}

        inventory: Dict[str, Dict[str, Any]] = {}
        for path in sorted(service_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            service_id = str(payload["service_id"])
            placeholders = set(PLACEHOLDER_RE.findall(json.dumps(payload, sort_keys=True)))
            inventory[service_id] = {
                "service_id": service_id,
                "display_name": payload.get("display_name"),
                "description": payload.get("description"),
                "manifest_path": str(path),
                "manifest_digest": _manifest_digest(payload),
                "dependencies": list(payload.get("dependencies", [])),
                "payload": payload,
                "placeholders": placeholders,
            }
        return inventory

    def _service_snapshot(self, service_id: str) -> Dict[str, Any]:
        entry = self._require_service_inventory(service_id)
        state = self.runtime_host.inspect().get(service_id, {})
        return {
            "service_id": service_id,
            "display_name": entry["display_name"],
            "description": entry["description"],
            "manifest_path": entry["manifest_path"],
            "manifest_digest": entry["manifest_digest"],
            "dependencies": list(entry["dependencies"]),
            "lifecycle_state": state.get("lifecycle_state", "registered"),
            "pid": state.get("pid"),
            "restart_count": state.get("restart_count", 0),
            "readiness": state.get("readiness", "unknown"),
            "health": state.get("health", "unknown"),
            "started_at": state.get("started_at"),
            "stopped_at": state.get("stopped_at"),
            "last_transition_at": state.get("last_transition_at"),
            "last_error": state.get("last_error"),
            "last_failure_reason": state.get("last_failure_reason"),
            "last_exit_code": state.get("last_exit_code"),
        }

    def _provider_snapshot(
        self,
        binding: ProviderBinding,
        service_states: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        dependency_states = {}
        for service_id in binding.service_dependency_ids:
            dependency_states[service_id] = service_states.get(service_id, {}).get(
                "lifecycle_state",
                "missing",
            )
        return {
            **binding.as_dict(),
            "service_dependency_states": dependency_states,
        }

    def _require_service_inventory(self, service_id: str) -> Dict[str, Any]:
        entry = self._service_inventory.get(service_id)
        if entry is None:
            raise ValueError("service manifest not found: %s" % service_id)
        return entry

    def _load_manifest(self, service_id: str):
        entry = self._require_service_inventory(service_id)
        environment = self._environment_for_service(service_id, entry["placeholders"])
        return self.runtime_host.load_manifest(
            Path(entry["manifest_path"]),
            environment=environment,
        )

    def _environment_for_service(
        self,
        service_id: str,
        placeholders: Iterable[str],
    ) -> Dict[str, str]:
        cached = self._environment_cache.get(service_id)
        if cached is not None:
            return dict(cached)

        environment: Dict[str, str] = {}
        for placeholder in sorted(set(placeholders)):
            if placeholder.endswith("_HOST"):
                environment[placeholder] = "127.0.0.1"
            elif placeholder.endswith("_PORT"):
                environment[placeholder] = str(self._allocate_port(placeholder))

        self._environment_cache[service_id] = dict(environment)
        return environment

    def _allocate_port(self, key: str) -> int:
        port = self._port_cache.get(key)
        if port is None:
            port = _free_port()
            self._port_cache[key] = port
        return port

    def _validate_actor(self, actor: Dict[str, Any]) -> None:
        actor_id = str(actor.get("actor_id", "")).strip()
        if not actor_id:
            raise ValueError("actor.actor_id is required")

        capabilities = {
            str(value).strip()
            for value in actor.get("capabilities", [])
            if str(value).strip()
        }
        if "runtime.service.reconcile" not in capabilities:
            raise ValueError("actor missing required capability: runtime.service.reconcile")

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def _manifest_digest(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sorted_unique_strings(values: Iterable[Any]) -> List[str]:
    items = {str(value).strip() for value in values if str(value).strip()}
    return sorted(items)


@dataclass(frozen=True)
class StructuredOutputSupport:
    mode: str = "none"
    schema_guarantee: str = "none"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "schema_guarantee": self.schema_guarantee,
        }


@dataclass(frozen=True)
class ProviderBinding:
    provider_id: str
    manifest_path: str
    manifest_digest: str
    display_name: Optional[str]
    description: Optional[str]
    provider_kind: str
    service_dependency_ids: List[str] = field(default_factory=list)
    capability_tags: List[str] = field(default_factory=list)
    model_identifiers: List[str] = field(default_factory=list)
    tool_identifiers: List[str] = field(default_factory=list)
    quality_tier: str = "balanced"
    latency_tier: str = "interactive"
    cost_tier: str = "medium"
    determinism_tier: str = "bounded"
    structured_output: StructuredOutputSupport = field(default_factory=StructuredOutputSupport)
    policy_scope_tags: List[str] = field(default_factory=list)
    health_dependency_mode: str = "all_ready"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "manifest_path": self.manifest_path,
            "manifest_digest": self.manifest_digest,
            "display_name": self.display_name,
            "description": self.description,
            "provider_kind": self.provider_kind,
            "service_dependency_ids": list(self.service_dependency_ids),
            "capability_tags": list(self.capability_tags),
            "model_identifiers": list(self.model_identifiers),
            "tool_identifiers": list(self.tool_identifiers),
            "quality_tier": self.quality_tier,
            "latency_tier": self.latency_tier,
            "cost_tier": self.cost_tier,
            "determinism_tier": self.determinism_tier,
            "structured_output": self.structured_output.as_dict(),
            "policy_scope_tags": list(self.policy_scope_tags),
            "health_dependency_mode": self.health_dependency_mode,
        }


class ProviderRegistry:
    def __init__(self, bindings: Iterable[ProviderBinding]) -> None:
        self._bindings = {binding.provider_id: binding for binding in bindings}

    def list_provider_ids(self) -> List[str]:
        return sorted(self._bindings)

    def bindings(self) -> List[ProviderBinding]:
        return [self._bindings[provider_id] for provider_id in self.list_provider_ids()]

    def get(self, provider_id: str) -> ProviderBinding:
        binding = self._bindings.get(provider_id)
        if binding is None:
            raise ValueError("provider binding not found: %s" % provider_id)
        return binding

    def as_dict(self) -> Dict[str, Any]:
        return {
            "providers": [binding.as_dict() for binding in self.bindings()],
        }


class ProviderRegistryLoader:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.binding_dir = self.repo_root / "infra" / "provider_bindings"

    def list_binding_names(self) -> List[str]:
        if not self.binding_dir.exists():
            return []
        return sorted(path.name for path in self.binding_dir.glob("*.json"))

    def load_binding(self, binding_name: str) -> ProviderBinding:
        file_name = binding_name if binding_name.endswith(".json") else "%s.json" % binding_name
        binding_path = self.binding_dir / file_name
        if not binding_path.exists():
            raise ValueError("provider binding not found: %s" % binding_name)
        payload = self._load_json(binding_path)
        return _parse_binding(binding_path, payload)

    def load_all(self) -> ProviderRegistry:
        return ProviderRegistry(self.load_binding(name) for name in self.list_binding_names())

    def _load_json(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def _parse_binding(path: Path, payload: Dict[str, Any]) -> ProviderBinding:
    model_identifiers = list(payload.get("model_identifiers", []))
    if not model_identifiers and payload.get("model_identifier"):
        model_identifiers = [payload["model_identifier"]]

    return ProviderBinding(
        provider_id=str(payload["provider_id"]),
        manifest_path=str(path),
        manifest_digest=_manifest_digest(payload),
        display_name=payload.get("display_name"),
        description=payload.get("description"),
        provider_kind=str(payload["provider_kind"]),
        service_dependency_ids=_sorted_unique_strings(payload.get("service_dependency_ids", [])),
        capability_tags=_sorted_unique_strings(payload.get("capability_tags", [])),
        model_identifiers=_sorted_unique_strings(model_identifiers),
        tool_identifiers=_sorted_unique_strings(payload.get("tool_identifiers", [])),
        quality_tier=str(payload.get("quality_tier", "balanced")),
        latency_tier=str(payload.get("latency_tier", "interactive")),
        cost_tier=str(payload.get("cost_tier", "medium")),
        determinism_tier=str(payload.get("determinism_tier", "bounded")),
        structured_output=StructuredOutputSupport(
            mode=str(payload.get("structured_output", {}).get("mode", "none")),
            schema_guarantee=str(payload.get("structured_output", {}).get("schema_guarantee", "none")),
        ),
        policy_scope_tags=_sorted_unique_strings(payload.get("policy_scope_tags", [])),
        health_dependency_mode=str(payload.get("health_dependency_mode", "all_ready")),
    )

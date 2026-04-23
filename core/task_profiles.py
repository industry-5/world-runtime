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
class OutputContract:
    response_format: str = "text"
    schema_id: Optional[str] = None
    structured_output_required: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "response_format": self.response_format,
            "schema_id": self.schema_id,
            "structured_output_required": self.structured_output_required,
        }


@dataclass(frozen=True)
class RoutingPreferences:
    preferred_quality_tier: str = "balanced"
    minimum_quality_tier: str = "economy"
    preferred_latency_tier: str = "interactive"
    preferred_cost_tier: str = "medium"
    minimum_determinism_tier: str = "bounded"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "preferred_quality_tier": self.preferred_quality_tier,
            "minimum_quality_tier": self.minimum_quality_tier,
            "preferred_latency_tier": self.preferred_latency_tier,
            "preferred_cost_tier": self.preferred_cost_tier,
            "minimum_determinism_tier": self.minimum_determinism_tier,
        }


@dataclass(frozen=True)
class FallbackPolicy:
    mode: str = "none"
    max_quality_tier_downgrade: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "max_quality_tier_downgrade": self.max_quality_tier_downgrade,
        }


@dataclass(frozen=True)
class TaskProfile:
    task_profile_id: str
    manifest_path: str
    manifest_digest: str
    display_name: Optional[str]
    description: Optional[str]
    task_category: str
    required_capability_tags: List[str] = field(default_factory=list)
    preferred_capability_tags: List[str] = field(default_factory=list)
    forbidden_capability_tags: List[str] = field(default_factory=list)
    required_policy_scope_tags: List[str] = field(default_factory=list)
    output_contract: OutputContract = field(default_factory=OutputContract)
    routing_preferences: RoutingPreferences = field(default_factory=RoutingPreferences)
    fallback_policy: FallbackPolicy = field(default_factory=FallbackPolicy)
    approval_sensitivity: str = "none"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "task_profile_id": self.task_profile_id,
            "manifest_path": self.manifest_path,
            "manifest_digest": self.manifest_digest,
            "display_name": self.display_name,
            "description": self.description,
            "task_category": self.task_category,
            "required_capability_tags": list(self.required_capability_tags),
            "preferred_capability_tags": list(self.preferred_capability_tags),
            "forbidden_capability_tags": list(self.forbidden_capability_tags),
            "required_policy_scope_tags": list(self.required_policy_scope_tags),
            "output_contract": self.output_contract.as_dict(),
            "routing_preferences": self.routing_preferences.as_dict(),
            "fallback_policy": self.fallback_policy.as_dict(),
            "approval_sensitivity": self.approval_sensitivity,
        }


class TaskProfileCatalog:
    def __init__(self, profiles: Iterable[TaskProfile]) -> None:
        self._profiles = {profile.task_profile_id: profile for profile in profiles}

    def list_profile_ids(self) -> List[str]:
        return sorted(self._profiles)

    def profiles(self) -> List[TaskProfile]:
        return [self._profiles[profile_id] for profile_id in self.list_profile_ids()]

    def get(self, task_profile_id: str) -> TaskProfile:
        profile = self._profiles.get(task_profile_id)
        if profile is None:
            raise ValueError("task profile not found: %s" % task_profile_id)
        return profile

    def as_dict(self) -> Dict[str, Any]:
        return {
            "task_profiles": [profile.as_dict() for profile in self.profiles()],
        }


class TaskProfileLoader:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.profile_dir = self.repo_root / "infra" / "task_profiles"

    def list_profile_names(self) -> List[str]:
        if not self.profile_dir.exists():
            return []
        return sorted(path.name for path in self.profile_dir.glob("*.json"))

    def load_profile(self, profile_name: str) -> TaskProfile:
        file_name = profile_name if profile_name.endswith(".json") else "%s.json" % profile_name
        profile_path = self.profile_dir / file_name
        if not profile_path.exists():
            raise ValueError("task profile not found: %s" % profile_name)
        payload = self._load_json(profile_path)
        return _parse_profile(profile_path, payload)

    def load_all(self) -> TaskProfileCatalog:
        return TaskProfileCatalog(self.load_profile(name) for name in self.list_profile_names())

    def _load_json(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def _parse_profile(path: Path, payload: Dict[str, Any]) -> TaskProfile:
    return TaskProfile(
        task_profile_id=str(payload["task_profile_id"]),
        manifest_path=str(path),
        manifest_digest=_manifest_digest(payload),
        display_name=payload.get("display_name"),
        description=payload.get("description"),
        task_category=str(payload["task_category"]),
        required_capability_tags=_sorted_unique_strings(payload.get("required_capability_tags", [])),
        preferred_capability_tags=_sorted_unique_strings(payload.get("preferred_capability_tags", [])),
        forbidden_capability_tags=_sorted_unique_strings(payload.get("forbidden_capability_tags", [])),
        required_policy_scope_tags=_sorted_unique_strings(payload.get("required_policy_scope_tags", [])),
        output_contract=OutputContract(
            response_format=str(payload.get("output_contract", {}).get("response_format", "text")),
            schema_id=payload.get("output_contract", {}).get("schema_id"),
            structured_output_required=bool(
                payload.get("output_contract", {}).get("structured_output_required", False)
            ),
        ),
        routing_preferences=RoutingPreferences(
            preferred_quality_tier=str(
                payload.get("routing_preferences", {}).get("preferred_quality_tier", "balanced")
            ),
            minimum_quality_tier=str(payload.get("routing_preferences", {}).get("minimum_quality_tier", "economy")),
            preferred_latency_tier=str(
                payload.get("routing_preferences", {}).get("preferred_latency_tier", "interactive")
            ),
            preferred_cost_tier=str(payload.get("routing_preferences", {}).get("preferred_cost_tier", "medium")),
            minimum_determinism_tier=str(
                payload.get("routing_preferences", {}).get("minimum_determinism_tier", "bounded")
            ),
        ),
        fallback_policy=FallbackPolicy(
            mode=str(payload.get("fallback_policy", {}).get("mode", "none")),
            max_quality_tier_downgrade=int(payload.get("fallback_policy", {}).get("max_quality_tier_downgrade", 0)),
        ),
        approval_sensitivity=str(payload.get("approval_sensitivity", "none")),
    )

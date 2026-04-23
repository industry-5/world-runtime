from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


def _sorted_unique_strings(values: Iterable[Any]) -> List[str]:
    items = {str(value).strip() for value in values if str(value).strip()}
    return sorted(items)


@dataclass(frozen=True)
class RoutingPolicyInput:
    allowed_provider_ids: List[str] = field(default_factory=list)
    denied_provider_ids: List[str] = field(default_factory=list)
    preferred_provider_ids: List[str] = field(default_factory=list)
    required_policy_scope_tags: List[str] = field(default_factory=list)
    required_provider_kinds: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any] | None) -> "RoutingPolicyInput":
        payload = dict(payload or {})
        return cls(
            allowed_provider_ids=_sorted_unique_strings(payload.get("allowed_provider_ids", [])),
            denied_provider_ids=_sorted_unique_strings(payload.get("denied_provider_ids", [])),
            preferred_provider_ids=_sorted_unique_strings(payload.get("preferred_provider_ids", [])),
            required_policy_scope_tags=_sorted_unique_strings(payload.get("required_policy_scope_tags", [])),
            required_provider_kinds=_sorted_unique_strings(payload.get("required_provider_kinds", [])),
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "allowed_provider_ids": list(self.allowed_provider_ids),
            "denied_provider_ids": list(self.denied_provider_ids),
            "preferred_provider_ids": list(self.preferred_provider_ids),
            "required_policy_scope_tags": list(self.required_policy_scope_tags),
            "required_provider_kinds": list(self.required_provider_kinds),
        }

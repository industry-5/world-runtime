from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class CandidateRoutingTrace:
    provider_id: str
    provider_kind: str
    status: str
    considered_stage: str
    selected: bool = False
    reasons: List[str] = field(default_factory=list)
    score: Dict[str, Any] = field(default_factory=dict)
    matched_capability_tags: List[str] = field(default_factory=list)
    missing_capability_tags: List[str] = field(default_factory=list)
    matched_policy_scope_tags: List[str] = field(default_factory=list)
    missing_policy_scope_tags: List[str] = field(default_factory=list)
    service_dependency_states: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_kind": self.provider_kind,
            "status": self.status,
            "considered_stage": self.considered_stage,
            "selected": self.selected,
            "reasons": list(self.reasons),
            "score": dict(self.score),
            "matched_capability_tags": list(self.matched_capability_tags),
            "missing_capability_tags": list(self.missing_capability_tags),
            "matched_policy_scope_tags": list(self.matched_policy_scope_tags),
            "missing_policy_scope_tags": list(self.missing_policy_scope_tags),
            "service_dependency_states": dict(self.service_dependency_states),
        }


@dataclass
class FallbackTrace:
    invoked: bool = False
    reason: Optional[str] = None
    from_stage: Optional[str] = None
    to_stage: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "invoked": self.invoked,
            "reason": self.reason,
            "from_stage": self.from_stage,
            "to_stage": self.to_stage,
        }


@dataclass
class RoutingDecisionTrace:
    task_profile_id: str
    task_category: str
    status: str
    selected_provider_id: Optional[str] = None
    selected_stage: Optional[str] = None
    no_route_reason: Optional[str] = None
    generated_at: str = field(default_factory=utc_now)
    policy_inputs: Dict[str, Any] = field(default_factory=dict)
    candidates: List[CandidateRoutingTrace] = field(default_factory=list)
    fallback: FallbackTrace = field(default_factory=FallbackTrace)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "task_profile_id": self.task_profile_id,
            "task_category": self.task_category,
            "status": self.status,
            "selected_provider_id": self.selected_provider_id,
            "selected_stage": self.selected_stage,
            "no_route_reason": self.no_route_reason,
            "generated_at": self.generated_at,
            "policy_inputs": dict(self.policy_inputs),
            "candidates": [candidate.as_dict() for candidate in self.candidates],
            "fallback": self.fallback.as_dict(),
        }

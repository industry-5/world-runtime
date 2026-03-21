from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


PROPOSAL_STATUSES = [
    "draft",
    "submitted",
    "under_review",
    "adopted",
    "rejected",
    "archived",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_proposal_record(
    proposal_id: str,
    title: str,
    author_actor_id: Optional[str],
    rationale: str = "",
    assumptions: Optional[List[str]] = None,
    intended_interventions: Optional[List[str]] = None,
    expected_outcomes: Optional[List[str]] = None,
    evidence_refs: Optional[List[Dict[str, Any]]] = None,
    planned_turn_sequence: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    timestamp = _utc_now()
    return {
        "proposal_id": str(proposal_id),
        "status": "draft",
        "title": str(title).strip(),
        "author_actor_id": author_actor_id,
        "rationale": str(rationale or "").strip(),
        "assumptions": [str(item) for item in (assumptions or [])],
        "intended_interventions": [str(item) for item in (intended_interventions or [])],
        "expected_outcomes": [str(item) for item in (expected_outcomes or [])],
        "evidence_refs": deepcopy(evidence_refs or []),
        "planned_turn_sequence": deepcopy(planned_turn_sequence or []),
        "review_history": [],
        "branch_id": None,
        "adopted_branch_id": None,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def update_proposal_record(proposal: Dict[str, Any], fields: Dict[str, Any]) -> Dict[str, Any]:
    if proposal.get("status") not in {"draft", "submitted", "under_review"}:
        raise ValueError("proposal %s cannot be updated in status %s" % (proposal.get("proposal_id"), proposal.get("status")))
    for key in [
        "title",
        "rationale",
        "assumptions",
        "intended_interventions",
        "expected_outcomes",
        "evidence_refs",
        "planned_turn_sequence",
        "branch_id",
    ]:
        if key in fields and fields[key] is not None:
            value = fields[key]
            proposal[key] = deepcopy(value)
    proposal["updated_at"] = _utc_now()
    return deepcopy(proposal)


def submit_proposal_record(proposal: Dict[str, Any], actor_id: Optional[str]) -> Dict[str, Any]:
    if proposal.get("status") != "draft":
        raise ValueError("proposal %s cannot be submitted from status %s" % (proposal.get("proposal_id"), proposal.get("status")))
    proposal["status"] = "submitted"
    proposal.setdefault("review_history", []).append(
        {
            "action": "submitted",
            "actor_id": actor_id,
            "at": _utc_now(),
        }
    )
    proposal["updated_at"] = _utc_now()
    return deepcopy(proposal)


def reject_proposal_record(proposal: Dict[str, Any], actor_id: Optional[str], reason: Optional[str] = None) -> Dict[str, Any]:
    if proposal.get("status") in {"adopted", "archived"}:
        raise ValueError("proposal %s cannot be rejected from status %s" % (proposal.get("proposal_id"), proposal.get("status")))
    proposal["status"] = "rejected"
    proposal.setdefault("review_history", []).append(
        {
            "action": "rejected",
            "actor_id": actor_id,
            "reason": reason,
            "at": _utc_now(),
        }
    )
    proposal["updated_at"] = _utc_now()
    return deepcopy(proposal)

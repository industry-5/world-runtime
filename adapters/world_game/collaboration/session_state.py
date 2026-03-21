from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


DEFAULT_ROLE_CAPABILITIES = {
    "facilitator": [
        "session.manage",
        "session.stage.set",
        "session.stage.advance",
        "proposal.review",
        "annotation.author",
    ],
    "analyst": [
        "proposal.create",
        "proposal.submit",
        "proposal.adopt",
        "branch.create",
        "simulation.run",
        "annotation.author",
    ],
    "observer": [
        "session.view",
        "proposal.view",
        "annotation.view",
    ],
    "approver": [
        "proposal.review",
        "proposal.adopt",
        "proposal.reject",
        "branch.create",
        "session.stage.advance",
        "annotation.author",
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def derive_actor_capabilities(roles: Optional[List[str]], explicit: Optional[List[str]] = None) -> List[str]:
    capabilities = set(explicit or [])
    for role in roles or []:
        capabilities.update(DEFAULT_ROLE_CAPABILITIES.get(str(role), []))
    return sorted(capabilities)


def build_session_meta(
    session_id: str,
    label: Optional[str] = None,
    description: Optional[str] = None,
    actor_id: Optional[str] = None,
    collaboration_enabled: bool = False,
) -> Dict[str, Any]:
    timestamp = _utc_now()
    return {
        "session_id": session_id,
        "label": (label or "World Game Collaboration Session").strip(),
        "description": (description or "").strip(),
        "created_at": timestamp,
        "updated_at": timestamp,
        "created_by_actor_id": actor_id,
        "collaboration_enabled": collaboration_enabled,
    }


def ensure_collaboration_state(
    context: Dict[str, Any],
    session_id: str,
    label: Optional[str] = None,
    description: Optional[str] = None,
    actor_id: Optional[str] = None,
    collaboration_enabled: Optional[bool] = None,
) -> Dict[str, Any]:
    session_meta = context.get("session_meta")
    if not isinstance(session_meta, dict):
        context["session_meta"] = build_session_meta(
            session_id=session_id,
            label=label,
            description=description,
            actor_id=actor_id,
            collaboration_enabled=bool(collaboration_enabled),
        )
    else:
        if label is not None:
            session_meta["label"] = str(label).strip()
        if description is not None:
            session_meta["description"] = str(description).strip()
        if collaboration_enabled is not None:
            session_meta["collaboration_enabled"] = bool(collaboration_enabled)
        session_meta["updated_at"] = _utc_now()
        context["session_meta"] = session_meta

    if not isinstance(context.get("actors"), dict):
        context["actors"] = {}
    if not isinstance(context.get("timeline"), list):
        context["timeline"] = []
    if not isinstance(context.get("proposals"), dict):
        context["proposals"] = {}
    if not isinstance(context.get("annotations"), dict):
        context["annotations"] = {}
    if not isinstance(context.get("facilitation_state"), dict):
        context["facilitation_state"] = {
            "stage": "setup",
            "stage_history": [],
            "allowed_actions": {},
            "enforce_stage_gates": bool(collaboration_enabled),
        }
    if not isinstance(context.get("provenance"), dict):
        context["provenance"] = {"artifacts": {}}
    return context


def build_timeline_event(
    context: Dict[str, Any],
    session_id: str,
    event_type: str,
    payload: Dict[str, Any],
    actor_id: Optional[str] = None,
) -> Dict[str, Any]:
    event_index = len(context.get("timeline", [])) + 1
    timestamp = _utc_now()
    return {
        "event_id": "wg.timeline.%s.%04d" % (session_id, event_index),
        "event_type": event_type,
        "session_id": session_id,
        "actor_id": actor_id,
        "timestamp": timestamp,
        "payload": deepcopy(payload),
    }


def add_actor_record(
    context: Dict[str, Any],
    actor_id: str,
    actor_type: str = "human",
    roles: Optional[List[str]] = None,
    capabilities: Optional[List[str]] = None,
    display_name: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_roles = [str(role) for role in (roles or ["observer"])]
    record = {
        "actor_id": str(actor_id),
        "actor_type": str(actor_type or "human"),
        "display_name": (display_name or actor_id).strip(),
        "roles": normalized_roles,
        "capabilities": derive_actor_capabilities(normalized_roles, capabilities),
        "created_at": _utc_now(),
        "active": True,
    }
    context["actors"][record["actor_id"]] = record
    context["session_meta"]["updated_at"] = _utc_now()
    return deepcopy(record)


def remove_actor_record(context: Dict[str, Any], actor_id: str) -> Dict[str, Any]:
    record = context["actors"].get(actor_id)
    if record is None:
        raise ValueError("unknown actor_id: %s" % actor_id)
    removed = deepcopy(record)
    removed["active"] = False
    context["actors"].pop(actor_id, None)
    context["session_meta"]["updated_at"] = _utc_now()
    return removed


def list_actor_records(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [deepcopy(context["actors"][actor_id]) for actor_id in sorted(context.get("actors", {}).keys())]


def get_actor_record(context: Dict[str, Any], actor_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not actor_id:
        return None
    record = context.get("actors", {}).get(actor_id)
    return deepcopy(record) if record is not None else None


def session_snapshot(context: Dict[str, Any]) -> Dict[str, Any]:
    meta = deepcopy(context.get("session_meta", {}))
    facilitation = deepcopy(context.get("facilitation_state", {}))
    return {
        "session_meta": meta,
        "actors": list_actor_records(context),
        "timeline_count": len(context.get("timeline", [])),
        "proposal_count": len(context.get("proposals", {})),
        "annotation_count": len(context.get("annotations", {})),
        "facilitation_state": facilitation,
        "scenario_id": context.get("scenario", {}).get("scenario_id"),
        "branch_ids": sorted(context.get("branches", {}).keys()),
    }

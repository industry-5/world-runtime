from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Optional


SESSION_STAGES = [
    "setup",
    "proposal_intake",
    "deliberation",
    "selection",
    "simulation",
    "review",
    "closed",
]
DEFAULT_STAGE = SESSION_STAGES[0]

_ALLOWED_ACTIONS = {
    "setup": {"session.actor.add", "session.actor.remove", "session.stage.set"},
    "proposal_intake": {"proposal.create", "proposal.update", "proposal.submit", "annotation.create"},
    "deliberation": {"proposal.list", "proposal.get", "annotation.create", "annotation.update", "proposal.reject"},
    "selection": {"proposal.adopt", "proposal.reject", "session.stage.advance"},
    "simulation": {"turn.run", "branch.create", "branch.compare", "replay.run", "annotation.create", "annotation.update"},
    "review": {"annotation.create", "annotation.update", "provenance.inspect", "branch.compare", "equity.report"},
    "closed": {"provenance.inspect", "annotation.list", "proposal.list"},
}

_VALID_NEXT_STAGES = {
    "setup": {"proposal_intake"},
    "proposal_intake": {"deliberation", "closed"},
    "deliberation": {"selection", "proposal_intake", "closed"},
    "selection": {"simulation", "deliberation", "closed"},
    "simulation": {"review", "selection", "closed"},
    "review": {"closed", "proposal_intake"},
    "closed": set(),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_facilitation_state(enforce_stage_gates: bool = False) -> Dict[str, Any]:
    return {
        "stage": DEFAULT_STAGE,
        "stage_history": [],
        "allowed_actions": {stage: sorted(actions) for stage, actions in _ALLOWED_ACTIONS.items()},
        "enforce_stage_gates": bool(enforce_stage_gates),
    }


def set_stage(
    facilitation_state: Dict[str, Any],
    stage: str,
    actor_id: Optional[str],
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    normalized = str(stage)
    if normalized not in SESSION_STAGES:
        raise ValueError("unknown session stage: %s" % stage)
    previous = facilitation_state.get("stage", DEFAULT_STAGE)
    if normalized == previous:
        return deepcopy(facilitation_state)
    if normalized not in _VALID_NEXT_STAGES.get(previous, set()):
        raise ValueError("invalid stage transition: %s -> %s" % (previous, normalized))

    facilitation_state["stage"] = normalized
    facilitation_state.setdefault("allowed_actions", {s: sorted(a) for s, a in _ALLOWED_ACTIONS.items()})
    facilitation_state.setdefault("stage_history", []).append(
        {
            "from_stage": previous,
            "to_stage": normalized,
            "actor_id": actor_id,
            "reason": reason,
            "changed_at": _utc_now(),
        }
    )
    return deepcopy(facilitation_state)


def advance_stage(
    facilitation_state: Dict[str, Any],
    actor_id: Optional[str],
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    current = facilitation_state.get("stage", DEFAULT_STAGE)
    valid_next = _VALID_NEXT_STAGES.get(current, set())
    if not valid_next:
        raise ValueError("session stage %s cannot advance" % current)
    current_index = SESSION_STAGES.index(current)
    for stage in SESSION_STAGES[current_index + 1 :]:
        if stage in valid_next:
            return set_stage(facilitation_state, stage, actor_id=actor_id, reason=reason)
    raise ValueError("session stage %s cannot advance" % current)


def assert_stage_allows_action(facilitation_state: Dict[str, Any], action: str) -> None:
    if not facilitation_state.get("enforce_stage_gates"):
        return
    stage = facilitation_state.get("stage", DEFAULT_STAGE)
    allowed = facilitation_state.get("allowed_actions", {}).get(stage, [])
    if action not in allowed:
        raise ValueError("action %s is not allowed during session stage %s" % (action, stage))

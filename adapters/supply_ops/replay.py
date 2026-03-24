from typing import Any, Dict, List, Optional


def build_commitment_risk_event(
    bundle: Dict[str, Any],
    *,
    event_id: Optional[str] = None,
    occurred_at: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    context = _require_mapping(bundle, "translation_context")
    order_signal = _require_mapping(bundle, "order_signal")
    proposal_suffix = _require_string(context, "proposal_suffix")
    timestamp = occurred_at or _require_string(context, "created_at")

    return {
        "event_id": event_id or f"evt.supply-ops.commitment-risk.{proposal_suffix}",
        "event_type": "commitment_risk_detected",
        "occurred_at": timestamp,
        "recorded_at": timestamp,
        "payload": {
            "commitment_id": _require_string(order_signal, "commitment_id"),
            "at_risk_units": _require_int(order_signal, "at_risk_units"),
            "reason": order_signal.get("reason", "translated_fixture_signal"),
        },
        "correlation_id": correlation_id or f"corr.supply-ops.{proposal_suffix}",
    }


def build_recovery_hypothetical_events(
    proposal: Dict[str, Any],
    *,
    occurred_at: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    proposal_id = _require_string(proposal, "proposal_id")
    timestamp = occurred_at or _require_string(proposal, "created_at")
    action = _require_mapping(proposal, "proposed_action")
    parameters = _require_mapping(action, "parameters")
    units = _require_int(parameters, "reallocation_units")
    correlation = correlation_id or f"corr.{proposal_id}"

    return [
        {
            "event_id": f"evt.supply-ops.inventory-rebalance.{proposal_id}",
            "event_type": "inventory_rebalance_planned",
            "occurred_at": timestamp,
            "recorded_at": timestamp,
            "payload": {
                "inventory_position_id": _require_string(
                    parameters, "source_inventory_id"
                ),
                "reallocated_units": units,
                "destination_commitment_id": _require_string(parameters, "commitment_id"),
            },
            "correlation_id": correlation,
        },
        {
            "event_id": f"evt.supply-ops.capacity-request.{proposal_id}",
            "event_type": "capacity_reservation_requested",
            "occurred_at": timestamp,
            "recorded_at": timestamp,
            "payload": {
                "capacity_bucket_id": _require_string(
                    parameters, "reserve_capacity_id"
                ),
                "commitment_id": _require_string(parameters, "commitment_id"),
                "requested_units": units,
            },
            "correlation_id": correlation,
        },
    ]


def _require_mapping(data: Dict[str, Any], field: str) -> Dict[str, Any]:
    value = data.get(field)
    if not isinstance(value, dict):
        raise ValueError("%s must be an object" % field)
    return value


def _require_string(data: Dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be a non-empty string" % field)
    return value


def _require_int(data: Dict[str, Any], field: str) -> int:
    value = data.get(field)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("%s must be an integer" % field)
    return value

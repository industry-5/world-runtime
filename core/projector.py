from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class SimpleProjector:
    initial_state: Optional[Dict[str, Any]] = None
    state: Dict[str, Any] = field(
        default_factory=lambda: {
            "events_processed": 0,
            "shipments": {},
            "factories": {},
            "commitments": {},
            "inventory_positions": {},
            "capacity_buckets": {},
            "characters": {},
            "last_event_id": None,
        }
    )

    def __post_init__(self) -> None:
        if self.initial_state is not None:
            self.state = deepcopy(self.initial_state)

    def apply(self, event: dict) -> None:
        self.state["events_processed"] += 1
        self.state["last_event_id"] = event.get("event_id")

        event_type = event.get("event_type")
        payload = event.get("payload", {})

        if event_type == "shipment_delayed":
            shipment_id = payload.get("shipment_id")
            if shipment_id:
                self.state["shipments"].setdefault(shipment_id, {})
                self.state["shipments"][shipment_id]["delay_hours"] = payload.get("delay_hours")
                self.state["shipments"][shipment_id]["cause"] = payload.get("cause")
        elif event_type == "commitment_risk_detected":
            commitment_id = payload.get("commitment_id")
            if commitment_id:
                self.state["commitments"].setdefault(commitment_id, {})
                self.state["commitments"][commitment_id]["at_risk_units"] = payload.get(
                    "at_risk_units"
                )
                self.state["commitments"][commitment_id]["risk_reason"] = payload.get("reason")
                self.state["commitments"][commitment_id]["status"] = "at_risk"
        elif event_type == "inventory_rebalance_planned":
            inventory_position_id = payload.get("inventory_position_id")
            destination_commitment_id = payload.get("destination_commitment_id")
            reallocated_units = payload.get("reallocated_units")

            if inventory_position_id:
                self.state["inventory_positions"].setdefault(inventory_position_id, {})
                self.state["inventory_positions"][inventory_position_id][
                    "reallocated_units"
                ] = reallocated_units
                self.state["inventory_positions"][inventory_position_id][
                    "destination_commitment_id"
                ] = destination_commitment_id

            if destination_commitment_id:
                self.state["commitments"].setdefault(destination_commitment_id, {})
                self.state["commitments"][destination_commitment_id][
                    "planned_recovery_units"
                ] = reallocated_units
                self.state["commitments"][destination_commitment_id][
                    "status"
                ] = "recovery_planned"
        elif event_type == "capacity_reservation_requested":
            capacity_bucket_id = payload.get("capacity_bucket_id")
            commitment_id = payload.get("commitment_id")
            requested_units = payload.get("requested_units")

            if capacity_bucket_id:
                self.state["capacity_buckets"].setdefault(capacity_bucket_id, {})
                self.state["capacity_buckets"][capacity_bucket_id][
                    "requested_units"
                ] = requested_units
                self.state["capacity_buckets"][capacity_bucket_id][
                    "commitment_id"
                ] = commitment_id

            if commitment_id:
                self.state["commitments"].setdefault(commitment_id, {})
                self.state["commitments"][commitment_id][
                    "requested_capacity_units"
                ] = requested_units
                self.state["commitments"][commitment_id][
                    "status"
                ] = "capacity_requested"

    def replay(self, events: list[dict]) -> Dict[str, Any]:
        for event in events:
            self.apply(event)
        return self.state

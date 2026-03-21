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

    def replay(self, events: list[dict]) -> Dict[str, Any]:
        for event in events:
            self.apply(event)
        return self.state

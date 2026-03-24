import re
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.replay_engine import ReplayEngine


@dataclass
class EvidenceRef:
    evidence_type: str
    ref_id: str
    summary: str

    def as_dict(self) -> Dict[str, str]:
        return {
            "evidence_type": self.evidence_type,
            "ref_id": self.ref_id,
            "summary": self.summary,
        }


@dataclass
class ReasoningAnswer:
    query: str
    answer_text: str
    query_type: str
    evidence: List[EvidenceRef]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "answer_text": self.answer_text,
            "query_type": self.query_type,
            "evidence": [item.as_dict() for item in self.evidence],
        }


class ReasoningAdapter:
    def __init__(self, replay_engine: ReplayEngine) -> None:
        self.replay_engine = replay_engine

    def build_context(
        self,
        projection_name: str,
        max_events: int = 20,
    ) -> Dict[str, Any]:
        replay = self.replay_engine.rebuild(projection_name, use_snapshot=True)
        all_events = self.replay_engine.event_store.read_all()
        recent_events = all_events[-max_events:] if max_events > 0 else []

        return {
            "projection_name": projection_name,
            "source_event_offset": replay.source_event_offset,
            "state": deepcopy(replay.state),
            "recent_events": deepcopy(recent_events),
            "event_count": len(all_events),
        }

    def retrieve_events(
        self,
        event_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        events = self.replay_engine.event_store.read_all()

        filtered = []
        for event in events:
            if event_type is not None and event.get("event_type") != event_type:
                continue

            if entity_id is not None:
                payload = event.get("payload", {})
                subject_entities = event.get("subject_entities", [])
                in_payload = any(value == entity_id for value in payload.values())
                in_subjects = any(
                    subject.get("entity_id") == entity_id for subject in subject_entities
                )
                if not (in_payload or in_subjects):
                    continue

            filtered.append(event)

        if limit < len(filtered):
            return deepcopy(filtered[-limit:])
        return deepcopy(filtered)

    def answer_query(
        self,
        projection_name: str,
        query: str,
    ) -> ReasoningAnswer:
        lowered = query.lower().strip()
        context = self.build_context(projection_name)

        if "shipment" in lowered and "delay" in lowered:
            return self._answer_shipment_delay_query(query, context)

        return self._answer_generic_query(query, context)

    def generate_proposal(
        self,
        projection_name: str,
        instruction: str,
        proposer: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        context = self.build_context(projection_name)
        shipment_id = self._extract_shipment_id(instruction)

        selected_shipment = shipment_id
        if selected_shipment is None:
            shipment_keys = list(context["state"].get("shipments", {}).keys())
            if shipment_keys:
                selected_shipment = shipment_keys[0]

        action_type = "review_world_state"
        parameters: Dict[str, Any] = {
            "instruction": instruction,
            "projection_name": projection_name,
        }
        expected_effects = ["create operator-visible recommendation"]

        if selected_shipment is not None:
            action_type = "reroute_shipment"
            parameters = {
                "shipment_id": selected_shipment,
                "new_route": "route.recommended.%s" % selected_shipment.replace(".", "-"),
            }
            expected_effects = [
                "reduce projected shipment delay impact",
                "requires policy evaluation before execution",
            ]

        proposal_id = "proposal.reasoning.%d" % (context["event_count"] + 1)
        now_ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

        evidence = []
        if selected_shipment is not None:
            for event in self.retrieve_events(event_type="shipment_delayed", entity_id=selected_shipment, limit=2):
                evidence.append(
                    {
                        "evidence_type": "event",
                        "ref_id": event.get("event_id", "unknown_event"),
                        "summary": "Shipment delay event used for recommendation context.",
                    }
                )

        return {
            "proposal_id": proposal_id,
            "proposal_type": "reasoning_recommendation",
            "status": "draft",
            "proposer": proposer
            or {
                "actor_id": "agent.reasoning-adapter-01",
                "actor_type": "agent",
                "display_name": "Reasoning Adapter",
            },
            "proposed_action": {
                "action_type": action_type,
                "parameters": parameters,
                "expected_effects": expected_effects,
            },
            "justification": "Generated from structured world state and recent events.",
            "supporting_evidence": evidence,
            "created_at": now_ts,
            "metadata": {
                "source": "reasoning_adapter",
                "projection_name": projection_name,
            },
        }

    def _answer_shipment_delay_query(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> ReasoningAnswer:
        shipment_id = self._extract_shipment_id(query)
        shipments = context["state"].get("shipments", {})

        if shipment_id is None:
            shipment_id = self._select_shipment_with_highest_delay(shipments)

        if shipment_id is None or shipment_id not in shipments:
            return ReasoningAnswer(
                query=query,
                query_type="shipment_delay",
                answer_text="No tracked shipment delay was found in current state.",
                evidence=[],
            )

        shipment_state = shipments[shipment_id]
        delay_hours = shipment_state.get("delay_hours")
        cause = shipment_state.get("cause", "unknown")

        evidence = []
        for event in self.retrieve_events(event_type="shipment_delayed", entity_id=shipment_id, limit=3):
            evidence.append(
                EvidenceRef(
                    evidence_type="event",
                    ref_id=event.get("event_id", "unknown_event"),
                    summary="Delay event for shipment %s." % shipment_id,
                )
            )

        answer_text = (
            "Shipment %s is delayed by %s hours (cause: %s). "
            "This answer is grounded in replayed state and delay events." % (shipment_id, delay_hours, cause)
        )
        return ReasoningAnswer(
            query=query,
            query_type="shipment_delay",
            answer_text=answer_text,
            evidence=evidence,
        )

    def _answer_generic_query(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> ReasoningAnswer:
        event_count = context.get("event_count", 0)
        answer = (
            "Projection %s is built from %d events at offset %s. "
            "Ask about shipments, delays, incidents, or sabotage for targeted reasoning."
            % (
                context.get("projection_name", "unknown"),
                event_count,
                context.get("source_event_offset"),
            )
        )
        return ReasoningAnswer(
            query=query,
            query_type="summary",
            answer_text=answer,
            evidence=[],
        )

    def _extract_shipment_id(self, text: str) -> Optional[str]:
        match = re.search(r"shipment[.][A-Za-z0-9._:-]+", text)
        if match is None:
            return None
        return match.group(0)

    def _select_shipment_with_highest_delay(self, shipments: Dict[str, Dict[str, Any]]) -> Optional[str]:
        selected = None
        selected_delay = -1
        for shipment_id, shipment_state in shipments.items():
            delay = shipment_state.get("delay_hours")
            if isinstance(delay, (int, float)) and delay > selected_delay:
                selected = shipment_id
                selected_delay = delay
        return selected

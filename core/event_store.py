from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class InMemoryEventStore:
    streams: Dict[str, List[dict]] = field(default_factory=dict)
    events_by_offset: List[dict] = field(default_factory=list)
    snapshots: Dict[str, List[dict]] = field(default_factory=dict)
    _next_offset: int = 0

    def append(
        self,
        stream_id: str,
        event: dict,
        expected_sequence: Optional[int] = None,
    ) -> dict:
        stream_events = self.streams.setdefault(stream_id, [])
        next_sequence = len(stream_events)
        if expected_sequence is not None and expected_sequence != next_sequence:
            raise ValueError(
                "sequence_conflict: expected %d got %d"
                % (expected_sequence, next_sequence)
            )

        event_record = deepcopy(event)
        event_record["stream_id"] = stream_id
        event_record["offset"] = self._next_offset
        if "sequence" not in event_record:
            event_record["sequence"] = next_sequence

        stream_events.append(event_record)
        self.events_by_offset.append(event_record)
        self._next_offset += 1
        return deepcopy(event_record)

    def read_stream(self, stream_id: str) -> List[dict]:
        return deepcopy(self.streams.get(stream_id, []))

    def all_events(self) -> List[dict]:
        return self.read_all()

    def read_all(self, from_offset: int = 0, to_offset: Optional[int] = None) -> List[dict]:
        if from_offset < 0:
            from_offset = 0
        if to_offset is None:
            to_offset = self._next_offset - 1
        if to_offset < from_offset:
            return []
        return deepcopy(self.events_by_offset[from_offset : to_offset + 1])

    def last_offset(self) -> Optional[int]:
        if not self.events_by_offset:
            return None
        return self._next_offset - 1

    def create_snapshot(
        self,
        projection_name: str,
        source_event_offset: int,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> dict:
        snapshot = {
            "projection_name": projection_name,
            "source_event_offset": source_event_offset,
            "state": deepcopy(state),
            "metadata": deepcopy(metadata) if metadata else {},
        }
        self.snapshots.setdefault(projection_name, []).append(snapshot)
        return deepcopy(snapshot)

    def latest_snapshot(self, projection_name: str) -> Optional[dict]:
        projection_snaps = self.snapshots.get(projection_name, [])
        if not projection_snaps:
            return None
        return deepcopy(projection_snaps[-1])

    def latest_snapshot_at_or_before(
        self, projection_name: str, offset: int
    ) -> Optional[dict]:
        projection_snaps = self.snapshots.get(projection_name, [])
        for snapshot in reversed(projection_snaps):
            if snapshot["source_event_offset"] <= offset:
                return deepcopy(snapshot)
        return None

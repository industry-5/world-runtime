from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from core.event_store import InMemoryEventStore


@dataclass
class ReplayResult:
    projection_name: str
    source_event_offset: int
    events_processed: int
    state: Dict[str, Any]
    from_snapshot: bool = False
    snapshot_offset: Optional[int] = None


class ReplayEngine:
    def __init__(
        self,
        event_store: InMemoryEventStore,
        projector_factory: Callable[..., Any],
    ):
        self.event_store = event_store
        self.projector_factory = projector_factory

    def rebuild(
        self,
        projection_name: str,
        up_to_offset: Optional[int] = None,
        use_snapshot: bool = True,
    ) -> ReplayResult:
        last_offset = self.event_store.last_offset()
        if last_offset is None:
            projector = self.projector_factory()
            return ReplayResult(
                projection_name=projection_name,
                source_event_offset=-1,
                events_processed=0,
                state=deepcopy(projector.state),
            )

        target_offset = last_offset if up_to_offset is None else min(up_to_offset, last_offset)
        snapshot = None
        from_offset = 0

        if use_snapshot:
            snapshot = self.event_store.latest_snapshot_at_or_before(projection_name, target_offset)
            if snapshot is not None:
                from_offset = snapshot["source_event_offset"] + 1

        if snapshot is not None:
            projector = self.projector_factory(initial_state=snapshot["state"])
        else:
            projector = self.projector_factory()

        events = self.event_store.read_all(from_offset=from_offset, to_offset=target_offset)
        for event in events:
            projector.apply(event)

        return ReplayResult(
            projection_name=projection_name,
            source_event_offset=target_offset,
            events_processed=len(events),
            state=deepcopy(projector.state),
            from_snapshot=snapshot is not None,
            snapshot_offset=snapshot["source_event_offset"] if snapshot is not None else None,
        )

    def save_snapshot(
        self,
        projection_name: str,
        source_event_offset: int,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> dict:
        return self.event_store.create_snapshot(
            projection_name=projection_name,
            source_event_offset=source_event_offset,
            state=state,
            metadata=metadata,
        )

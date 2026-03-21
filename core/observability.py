from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from statistics import mean
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _iso_to_epoch_seconds(value: str) -> Optional[float]:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


@dataclass
class TelemetryEvent:
    event_id: str
    at: str
    component: str
    event_type: str
    severity: str = "info"
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "at": self.at,
            "component": self.component,
            "event_type": self.event_type,
            "severity": self.severity,
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "task_id": self.task_id,
            "attributes": deepcopy(self.attributes),
        }


@dataclass
class RuntimeTrace:
    trace_id: str
    name: str
    component: str
    started_at: str
    status: str = "running"
    ended_at: Optional[str] = None
    duration_ms: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "component": self.component,
            "status": self.status,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms": self.duration_ms,
            "context": deepcopy(self.context),
            "events": deepcopy(self.events),
            "error": self.error,
        }


class ObservabilityStore:
    def __init__(self) -> None:
        self._events: List[TelemetryEvent] = []
        self._traces: Dict[str, RuntimeTrace] = {}

    def start_trace(
        self,
        name: str,
        component: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        trace_id = "trace.%s" % uuid4().hex[:12]
        trace = RuntimeTrace(
            trace_id=trace_id,
            name=name,
            component=component,
            started_at=_utc_now(),
            context=deepcopy(context or {}),
        )
        self._traces[trace_id] = trace
        self.emit(
            component=component,
            event_type="trace.started",
            trace_id=trace_id,
            attributes={"name": name},
        )
        return trace_id

    def finish_trace(
        self,
        trace_id: str,
        status: str,
        error: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        trace = self._traces.get(trace_id)
        if trace is None:
            return

        trace.status = status
        trace.ended_at = _utc_now()
        start_epoch = _iso_to_epoch_seconds(trace.started_at)
        end_epoch = _iso_to_epoch_seconds(trace.ended_at)
        if start_epoch is not None and end_epoch is not None:
            trace.duration_ms = max(int((end_epoch - start_epoch) * 1000), 0)
        if error is not None:
            trace.error = error
        self.emit(
            component=trace.component,
            event_type="trace.finished",
            severity="error" if status == "failed" else "info",
            trace_id=trace_id,
            attributes={"status": status, **deepcopy(extra or {})},
        )

    def trace_event(
        self,
        trace_id: str,
        event_type: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        trace = self._traces.get(trace_id)
        if trace is None:
            return

        event = {
            "at": _utc_now(),
            "event_type": event_type,
            "attributes": deepcopy(attributes or {}),
        }
        trace.events.append(event)

    def emit(
        self,
        component: str,
        event_type: str,
        severity: str = "info",
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        event = TelemetryEvent(
            event_id="telem.%s" % uuid4().hex[:12],
            at=_utc_now(),
            component=component,
            event_type=event_type,
            severity=severity,
            trace_id=trace_id,
            session_id=session_id,
            task_id=task_id,
            attributes=deepcopy(attributes or {}),
        )
        self._events.append(event)
        return event.as_dict()

    def list_events(
        self,
        since: int = 0,
        limit: Optional[int] = None,
        component: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> Dict[str, Any]:
        start = max(since, 0)
        sliced = self._events[start:]

        filtered: List[TelemetryEvent] = []
        for item in sliced:
            if component is not None and item.component != component:
                continue
            if severity is not None and item.severity != severity:
                continue
            filtered.append(item)

        if limit is not None:
            filtered = filtered[: max(limit, 0)]

        return {
            "from_index": start,
            "next_index": start + len(filtered),
            "events": [item.as_dict() for item in filtered],
        }

    def list_traces(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        traces = [trace.as_dict() for trace in self._traces.values()]
        traces.sort(key=lambda item: item["started_at"], reverse=True)
        if limit is not None:
            traces = traces[: max(limit, 0)]
        return traces

    def summary(self) -> Dict[str, Any]:
        by_component: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        by_event_type: Dict[str, int] = {}

        for event in self._events:
            by_component[event.component] = by_component.get(event.component, 0) + 1
            by_severity[event.severity] = by_severity.get(event.severity, 0) + 1
            by_event_type[event.event_type] = by_event_type.get(event.event_type, 0) + 1

        traces = list(self._traces.values())
        trace_durations = [item.duration_ms for item in traces if item.duration_ms is not None]

        by_status: Dict[str, int] = {}
        for trace in traces:
            by_status[trace.status] = by_status.get(trace.status, 0) + 1

        return {
            "generated_at": _utc_now(),
            "totals": {
                "events": len(self._events),
                "traces": len(traces),
                "errors": by_severity.get("error", 0),
            },
            "events": {
                "by_component": by_component,
                "by_severity": by_severity,
                "by_type": by_event_type,
            },
            "traces": {
                "by_status": by_status,
                "duration_ms": {
                    "avg": int(mean(trace_durations)) if trace_durations else None,
                    "max": max(trace_durations) if trace_durations else None,
                },
            },
        }

    def dashboard(self) -> Dict[str, Any]:
        summary = self.summary()
        slow_traces = sorted(
            [item for item in self.list_traces(limit=50) if item.get("duration_ms") is not None],
            key=lambda item: item.get("duration_ms") or 0,
            reverse=True,
        )[:5]

        return {
            "generated_at": summary["generated_at"],
            "cards": {
                "events": summary["totals"]["events"],
                "traces": summary["totals"]["traces"],
                "errors": summary["totals"]["errors"],
                "avg_trace_ms": summary["traces"]["duration_ms"]["avg"],
            },
            "breakdowns": {
                "events_by_component": summary["events"]["by_component"],
                "events_by_severity": summary["events"]["by_severity"],
                "traces_by_status": summary["traces"]["by_status"],
            },
            "slow_traces": [
                {
                    "trace_id": trace["trace_id"],
                    "name": trace["name"],
                    "component": trace["component"],
                    "duration_ms": trace["duration_ms"],
                    "status": trace["status"],
                }
                for trace in slow_traces
            ],
        }

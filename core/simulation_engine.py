from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from core.replay_engine import ReplayEngine


@dataclass
class SimulationBranch:
    simulation_id: str
    projection_name: str
    base_event_offset: int
    base_state: Dict[str, Any]
    parent_simulation_id: Optional[str]
    scenario_name: Optional[str]
    assumptions: List[str]
    inputs: Dict[str, Any]
    status: str = "draft"
    hypothetical_events: List[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.hypothetical_events is None:
            self.hypothetical_events = []


@dataclass
class SimulationResult:
    simulation_id: str
    parent_simulation_id: Optional[str]
    base_event_offset: int
    status: str
    hypothetical_events_applied: int
    base_state: Dict[str, Any]
    simulated_state: Dict[str, Any]
    state_diff: Dict[str, Dict[str, Any]]
    comparison_summary: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "parent_simulation_id": self.parent_simulation_id,
            "base_event_offset": self.base_event_offset,
            "status": self.status,
            "hypothetical_events_applied": self.hypothetical_events_applied,
            "base_state": deepcopy(self.base_state),
            "simulated_state": deepcopy(self.simulated_state),
            "state_diff": deepcopy(self.state_diff),
            "comparison_summary": deepcopy(self.comparison_summary),
        }


class SimulationEngine:
    def __init__(
        self,
        replay_engine: ReplayEngine,
        projector_factory: Callable[..., Any],
    ) -> None:
        self.replay_engine = replay_engine
        self.projector_factory = projector_factory
        self.branches: Dict[str, SimulationBranch] = {}
        self.results: Dict[str, SimulationResult] = {}

    def create_branch(
        self,
        simulation_id: str,
        projection_name: str,
        parent_simulation_id: Optional[str] = None,
        scenario_name: Optional[str] = None,
        assumptions: Optional[List[str]] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> SimulationBranch:
        if simulation_id in self.branches:
            raise ValueError("simulation_id already exists")

        if parent_simulation_id is not None and parent_simulation_id not in self.branches:
            raise ValueError("parent_simulation_id does not exist")

        base_result = self.replay_engine.rebuild(projection_name)
        branch = SimulationBranch(
            simulation_id=simulation_id,
            projection_name=projection_name,
            base_event_offset=base_result.source_event_offset,
            base_state=base_result.state,
            parent_simulation_id=parent_simulation_id,
            scenario_name=scenario_name,
            assumptions=assumptions or [],
            inputs=inputs or {},
            status="draft",
        )
        self.branches[simulation_id] = branch
        return deepcopy(branch)

    def apply_hypothetical_event(self, simulation_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        branch = self.branches.get(simulation_id)
        if branch is None:
            raise ValueError("simulation_id not found")

        branch.status = "running"
        branch_event = deepcopy(event)
        branch_event["event_id"] = branch_event.get(
            "event_id",
            "evt.simulated.%s.%d" % (simulation_id, len(branch.hypothetical_events) + 1),
        )
        branch.hypothetical_events.append(branch_event)
        return deepcopy(branch_event)

    def run(self, simulation_id: str) -> SimulationResult:
        branch = self.branches.get(simulation_id)
        if branch is None:
            raise ValueError("simulation_id not found")

        projector = self.projector_factory(initial_state=deepcopy(branch.base_state))
        for event in branch.hypothetical_events:
            projector.apply(event)

        simulated_state = deepcopy(projector.state)
        state_diff = self._diff_states(branch.base_state, simulated_state)

        result = SimulationResult(
            simulation_id=branch.simulation_id,
            parent_simulation_id=branch.parent_simulation_id,
            base_event_offset=branch.base_event_offset,
            status="completed",
            hypothetical_events_applied=len(branch.hypothetical_events),
            base_state=deepcopy(branch.base_state),
            simulated_state=simulated_state,
            state_diff=state_diff,
            comparison_summary={
                "changed_paths": sorted(state_diff.keys()),
                "changed_path_count": len(state_diff),
                "ran_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        branch.status = "completed"
        self.results[simulation_id] = result
        return deepcopy(result)

    def discard(self, simulation_id: str) -> None:
        branch = self.branches.get(simulation_id)
        if branch is None:
            raise ValueError("simulation_id not found")
        branch.status = "cancelled"

    def get_result(self, simulation_id: str) -> Optional[SimulationResult]:
        result = self.results.get(simulation_id)
        if result is None:
            return None
        return deepcopy(result)

    def _diff_states(
        self,
        base_state: Dict[str, Any],
        simulated_state: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        diff: Dict[str, Dict[str, Any]] = {}
        self._diff_any(base_state, simulated_state, path="", out=diff)
        return diff

    def _diff_any(
        self,
        base_value: Any,
        simulated_value: Any,
        path: str,
        out: Dict[str, Dict[str, Any]],
    ) -> None:
        if isinstance(base_value, dict) and isinstance(simulated_value, dict):
            keys = set(base_value.keys()) | set(simulated_value.keys())
            for key in sorted(keys):
                child_path = key if path == "" else "%s.%s" % (path, key)
                if key not in base_value:
                    out[child_path] = {"base": None, "simulated": deepcopy(simulated_value[key])}
                elif key not in simulated_value:
                    out[child_path] = {"base": deepcopy(base_value[key]), "simulated": None}
                else:
                    self._diff_any(base_value[key], simulated_value[key], child_path, out)
            return

        if base_value != simulated_value:
            out[path or "<root>"] = {
                "base": deepcopy(base_value),
                "simulated": deepcopy(simulated_value),
            }

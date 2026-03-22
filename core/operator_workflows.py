from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from adapters.registry import AdapterRegistry
from core.app_server import WorldRuntimeAppServer
from core.eval_harness import EvalHarness
from core.event_store import InMemoryEventStore
from core.observability import ObservabilityStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


def load_json(path: Path) -> Any:
    import json

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class OperatorWorkflowRunner:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry = AdapterRegistry.with_defaults()

        self.store = InMemoryEventStore()
        self._load_default_events()
        self.observability = ObservabilityStore()

        self.replay = ReplayEngine(self.store, SimpleProjector)
        self.simulation = SimulationEngine(self.replay, SimpleProjector)
        self.reasoning = ReasoningAdapter(self.replay)
        self.policy = DeterministicPolicyEngine()
        self.eval_harness = EvalHarness(
            replay_engine=self.replay,
            simulation_engine=self.simulation,
            reasoning_adapter=self.reasoning,
            policy_engine=self.policy,
            observability=self.observability,
        )
        self.app_server = WorldRuntimeAppServer(
            reasoning_adapter=self.reasoning,
            simulation_engine=self.simulation,
            replay_engine=self.replay,
            policy_engine=self.policy,
            eval_harness=self.eval_harness,
            observability=self.observability,
        )

    def run_quickstart(self, adapter_id: str = "adapter-supply-network") -> Dict[str, Any]:
        trace_id = self.observability.start_trace(
            name="operator_workflow.quickstart",
            component="operator_workflow",
            context={"adapter_id": adapter_id},
        )
        adapter = self.registry.get(adapter_id)
        scenario = adapter.scenario_dir(self.repo_root)

        session = self.app_server.session_create()
        session_id = session["session_id"]

        reasoning_task = self.app_server.task_submit(
            session_id=session_id,
            method="reasoning.query",
            params={
                "projection_name": "world_state",
                "query": "Summarize current world state and risks",
            },
        )

        proposal_task = self.app_server.task_submit(
            session_id=session_id,
            method="proposal.generate",
            params={
                "projection_name": "world_state",
                "instruction": "Propose the next best action for operators",
            },
        )

        result = {
            "workflow": "quickstart",
            "adapter_id": adapter_id,
            "scenario": str(scenario),
            "session_id": session_id,
            "reasoning": deepcopy(reasoning_task["result"]),
            "proposal": deepcopy(proposal_task["result"]),
            "events": self.app_server.task_events_subscribe(session_id=session_id)["events"],
            "diagnostics": self.observability.dashboard(),
        }
        self.observability.finish_trace(trace_id, status="completed")
        return result

    def run_failure_recovery(self, adapter_id: str = "adapter-supply-network") -> Dict[str, Any]:
        trace_id = self.observability.start_trace(
            name="operator_workflow.failure_recovery",
            component="operator_workflow",
            context={"adapter_id": adapter_id},
        )
        adapter = self.registry.get(adapter_id)
        session = self.app_server.session_create()
        session_id = session["session_id"]

        simulation_id = "sim.workflow.recovery"
        self.app_server.simulation_create(
            session_id=session_id,
            simulation_id=simulation_id,
            projection_name="world_state",
            scenario_name="Failure recovery analysis",
        )

        self.simulation.apply_hypothetical_event(
            simulation_id,
            {
                "event_type": "shipment_delayed",
                "payload": {
                    "shipment_id": "shipment.88421",
                    "delay_hours": 2,
                    "cause": "recovery_reroute",
                },
            },
        )

        result = self.app_server.simulation_run(session_id=session_id, simulation_id=simulation_id)

        result = {
            "workflow": "failure-recovery",
            "adapter_id": adapter.adapter_id,
            "session_id": session_id,
            "simulation": deepcopy(result),
            "recommendation": {
                "action": "reroute_shipment",
                "reason": "simulation indicates lower delay impact",
                "changed_paths": result["comparison_summary"].get("changed_paths", []),
            },
            "diagnostics": self.observability.dashboard(),
        }
        self.observability.finish_trace(trace_id, status="completed")
        return result

    def run_proposal_review(
        self,
        adapter_id: str = "adapter-supply-network",
        auto_approve: bool = True,
    ) -> Dict[str, Any]:
        trace_id = self.observability.start_trace(
            name="operator_workflow.proposal_review",
            component="operator_workflow",
            context={"adapter_id": adapter_id, "auto_approve": auto_approve},
        )
        adapter = self.registry.get(adapter_id)
        scenario_dir = adapter.scenario_dir(self.repo_root)
        proposal = load_json(scenario_dir / "proposal.json")
        policy = load_json(adapter.default_policy_path(self.repo_root))

        session = self.app_server.session_create()
        session_id = session["session_id"]

        task = self.app_server.task_submit(
            session_id=session_id,
            method="proposal.submit",
            params={
                "proposal": proposal,
                "policies": [policy],
            },
        )

        task_result = task["result"]
        approval_result: Optional[Dict[str, Any]] = None

        approval_id = task_result.get("approval_id")
        if approval_id and auto_approve:
            approval_result = self.app_server.approval_respond(
                approval_id=approval_id,
                decision="approved",
                comment="Auto-approved by workflow runner",
                actor={
                    "actor_id": "human.workflow-operator-01",
                    "actor_type": "human",
                    "display_name": "Workflow Operator",
                    "roles": ["operator"],
                    "capabilities": ["approval.respond", "proposal.approve"],
                },
            )

        decision = self.app_server.decision_create(
            session_id=session_id,
            proposal=proposal,
            policy_report=task_result["policy_report"],
            approval_status=(approval_result or {}).get("status", "not_required"),
            approval_id=approval_id,
        )

        result = {
            "workflow": "proposal-review",
            "adapter_id": adapter.adapter_id,
            "session_id": session_id,
            "proposal": proposal.get("proposal_id"),
            "policy_report": deepcopy(task_result["policy_report"]),
            "approval": deepcopy(approval_result),
            "decision": deepcopy(decision),
            "events": self.app_server.task_events_subscribe(session_id=session_id)["events"],
            "diagnostics": self.observability.dashboard(),
        }
        self.observability.finish_trace(trace_id, status="completed")
        return result

    def run_simulation_analysis(self, adapter_id: str = "adapter-supply-network") -> Dict[str, Any]:
        trace_id = self.observability.start_trace(
            name="operator_workflow.simulation_analysis",
            component="operator_workflow",
            context={"adapter_id": adapter_id},
        )
        adapter = self.registry.get(adapter_id)
        session = self.app_server.session_create()
        session_id = session["session_id"]

        task = self.app_server.task_submit(
            session_id=session_id,
            method="simulation.run",
            params={
                "simulation_id": "sim.workflow.analysis",
                "projection_name": "world_state",
                "scenario_name": "Operator simulation analysis",
                "hypothetical_events": [
                    {
                        "event_type": "shipment_delayed",
                        "payload": {
                            "shipment_id": "shipment.88421",
                            "delay_hours": 4,
                            "cause": "analysis_case",
                        },
                    }
                ],
            },
        )

        result = task["result"]
        result = {
            "workflow": "simulation-analysis",
            "adapter_id": adapter.adapter_id,
            "session_id": session_id,
            "analysis": {
                "status": result["status"],
                "changed_paths": result["comparison_summary"].get("changed_paths", []),
                "changed_path_count": result["comparison_summary"].get("changed_path_count", 0),
            },
            "result": deepcopy(result),
            "diagnostics": self.observability.dashboard(),
        }
        self.observability.finish_trace(trace_id, status="completed")
        return result

    def _load_default_events(self) -> None:
        supply_events = load_json(
            self.repo_root / "examples" / "scenarios" / "supply-network-mini" / "events.json"
        )
        air_traffic_events = load_json(
            self.repo_root / "examples" / "scenarios" / "air-traffic-mini" / "events.json"
        )

        for index, event in enumerate(supply_events):
            self.store.append("supply.stream.%d" % index, event)
        for index, event in enumerate(air_traffic_events):
            self.store.append("air-traffic.stream.%d" % index, event)

        world_game_events_path = self.repo_root / "examples" / "scenarios" / "world-game-mini" / "events.json"
        if world_game_events_path.exists():
            world_game_events = load_json(world_game_events_path)
            for index, event in enumerate(world_game_events):
                self.store.append("world-game.stream.%d" % index, event)

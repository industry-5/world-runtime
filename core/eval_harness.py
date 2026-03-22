from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from core.policy_engine import DeterministicPolicyEngine
from core.observability import ObservabilityStore
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


Outcome = Dict[str, Any]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class EvalCase:
    eval_id: str
    category: str
    description: str
    run: Callable[[], Outcome]


class EvalHarness:
    def __init__(
        self,
        replay_engine: ReplayEngine,
        simulation_engine: SimulationEngine,
        reasoning_adapter: ReasoningAdapter,
        policy_engine: Optional[DeterministicPolicyEngine] = None,
        observability: Optional[ObservabilityStore] = None,
    ) -> None:
        self.replay_engine = replay_engine
        self.simulation_engine = simulation_engine
        self.reasoning_adapter = reasoning_adapter
        self.policy_engine = policy_engine or DeterministicPolicyEngine()
        self.observability = observability or ObservabilityStore()
        self._eval_cases: Dict[str, EvalCase] = {}
        self._register_default_cases()

    def list_evals(self) -> List[Dict[str, str]]:
        return [
            {
                "eval_id": case.eval_id,
                "category": case.category,
                "description": case.description,
            }
            for case in self._ordered_cases()
        ]

    def run_eval(self, eval_id: str) -> Dict[str, Any]:
        case = self._eval_cases.get(eval_id)
        if case is None:
            raise ValueError("unknown eval_id")

        trace_id = self.observability.start_trace(
            name="eval_harness.run_eval",
            component="eval_harness",
            context={"eval_id": eval_id, "category": case.category},
        )
        started = _utc_now()
        outcome = case.run()
        status = "passed" if outcome.get("passed", False) else "failed"
        self.observability.emit(
            component="eval_harness",
            event_type="eval.executed",
            severity="error" if status == "failed" else "info",
            trace_id=trace_id,
            attributes={"eval_id": eval_id, "status": status},
        )
        self.observability.finish_trace(
            trace_id=trace_id,
            status="completed" if status == "passed" else "failed",
            error=None if status == "passed" else "eval_failed",
        )

        return {
            "eval_id": eval_id,
            "category": case.category,
            "description": case.description,
            "status": status,
            "ran_at": started,
            "details": deepcopy(outcome),
        }

    def run_suite(
        self,
        eval_ids: Optional[List[str]] = None,
        minimum_pass_rate: float = 1.0,
    ) -> Dict[str, Any]:
        selected_ids = eval_ids or [case.eval_id for case in self._ordered_cases()]
        trace_id = self.observability.start_trace(
            name="eval_harness.run_suite",
            component="eval_harness",
            context={"eval_ids": selected_ids, "minimum_pass_rate": minimum_pass_rate},
        )

        results = []
        passed_count = 0
        failed = []

        for eval_id in selected_ids:
            result = self.run_eval(eval_id)
            results.append(result)
            if result["status"] == "passed":
                passed_count += 1
            else:
                failed.append(eval_id)

        total = len(results)
        pass_rate = (passed_count / total) if total else 0.0
        suite_status = "passed" if pass_rate >= minimum_pass_rate and not failed else "failed"
        self.observability.emit(
            component="eval_harness",
            event_type="suite.executed",
            severity="error" if suite_status == "failed" else "info",
            trace_id=trace_id,
            attributes={
                "status": suite_status,
                "passed": passed_count,
                "total": total,
                "minimum_pass_rate": minimum_pass_rate,
            },
        )
        self.observability.finish_trace(
            trace_id=trace_id,
            status="completed" if suite_status == "passed" else "failed",
            error=None if suite_status == "passed" else "suite_failed",
        )

        return {
            "suite": "world-runtime-v0.1",
            "ran_at": _utc_now(),
            "minimum_pass_rate": minimum_pass_rate,
            "pass_rate": round(pass_rate, 4),
            "status": suite_status,
            "total": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "failed_eval_ids": failed,
            "results": results,
        }

    def _register_default_cases(self) -> None:
        self._add_case(
            eval_id="eval.smoke.runtime",
            category="functional",
            description="Rebuild provides state surface for runtime tasks",
            fn=self._eval_smoke_runtime,
        )
        self._add_case(
            eval_id="eval.smoke.policy",
            category="policy",
            description="Policy denies dangerous actions",
            fn=self._eval_smoke_policy,
        )
        self._add_case(
            eval_id="eval.smoke.simulation",
            category="simulation",
            description="Simulation branches are isolated from canonical state",
            fn=self._eval_smoke_simulation,
        )
        self._add_case(
            eval_id="eval.reasoning.evidence",
            category="reasoning",
            description="Reasoning answers include evidence citations",
            fn=self._eval_reasoning_evidence,
        )
        self._add_case(
            eval_id="eval.safety.non_mutating_reasoning",
            category="safety",
            description="Reasoning/proposal generation does not mutate canonical log",
            fn=self._eval_safety_non_mutating_reasoning,
        )
        self._add_case(
            eval_id="eval.safety.air_traffic_constraints",
            category="safety",
            description="Air-traffic domain safety constraints enforce deny/warn/approval paths",
            fn=self._eval_safety_air_traffic_constraints,
        )
        self._add_case(
            eval_id="eval.regression.replay_determinism",
            category="regression",
            description="Replay remains deterministic",
            fn=self._eval_regression_replay_determinism,
        )

    def _add_case(self, eval_id: str, category: str, description: str, fn: Callable[[], Outcome]) -> None:
        self._eval_cases[eval_id] = EvalCase(
            eval_id=eval_id,
            category=category,
            description=description,
            run=fn,
        )

    def _ordered_cases(self) -> List[EvalCase]:
        return [self._eval_cases[key] for key in sorted(self._eval_cases.keys())]

    def _eval_smoke_runtime(self) -> Outcome:
        replay = self.replay_engine.rebuild("world_state")
        passed = replay.state.get("events_processed", 0) >= 1
        return {
            "passed": passed,
            "source_event_offset": replay.source_event_offset,
            "events_processed": replay.state.get("events_processed"),
        }

    def _eval_smoke_policy(self) -> Outcome:
        policy = {
            "policy_id": "policy.eval",
            "policy_name": "eval_policy",
            "default_outcome": "allow",
            "rules": [
                {
                    "rule_id": "rule.eval.deny",
                    "rule_name": "deny dangerous action",
                    "condition": {
                        "field": "proposed_action.action_type",
                        "operator": "equals",
                        "value": "dangerous_action",
                    },
                    "outcome": "deny",
                }
            ],
        }
        proposal = {
            "proposal_id": "proposal.eval.1",
            "proposed_action": {"action_type": "dangerous_action"},
        }
        report = self.policy_engine.evaluate_policies([policy], proposal)
        return {
            "passed": report.final_outcome == "deny",
            "final_outcome": report.final_outcome,
            "requires_approval": report.requires_approval,
        }

    def _eval_smoke_simulation(self) -> Outcome:
        canonical_before = self.replay_engine.rebuild("world_state", use_snapshot=False)
        before_offset = self.replay_engine.event_store.last_offset()

        sim_id = "sim.eval.smoke"
        if sim_id in self.simulation_engine.branches:
            self.simulation_engine.discard(sim_id)

        self.simulation_engine.create_branch(
            simulation_id=sim_id,
            projection_name="world_state",
            scenario_name="Eval simulation isolation",
        )
        self.simulation_engine.apply_hypothetical_event(
            sim_id,
            {
                "event_type": "shipment_delayed",
                "payload": {
                    "shipment_id": "shipment.88421",
                    "delay_hours": 1,
                    "cause": "eval_simulation",
                },
            },
        )
        result = self.simulation_engine.run(sim_id)

        canonical_after = self.replay_engine.rebuild("world_state", use_snapshot=False)
        after_offset = self.replay_engine.event_store.last_offset()

        passed = (
            before_offset == after_offset
            and canonical_before.state == canonical_after.state
            and result.simulated_state != canonical_after.state
        )

        return {
            "passed": passed,
            "before_offset": before_offset,
            "after_offset": after_offset,
            "changed_paths": result.comparison_summary.get("changed_paths", []),
        }

    def _eval_reasoning_evidence(self) -> Outcome:
        answer = self.reasoning_adapter.answer_query(
            projection_name="world_state",
            query="What is the delay status for shipment.88421?",
        )
        passed = bool(answer.evidence)
        return {
            "passed": passed,
            "query_type": answer.query_type,
            "evidence_count": len(answer.evidence),
        }

    def _eval_safety_non_mutating_reasoning(self) -> Outcome:
        before_offset = self.replay_engine.event_store.last_offset()
        self.reasoning_adapter.answer_query(
            projection_name="world_state",
            query="What is delayed?",
        )
        self.reasoning_adapter.generate_proposal(
            projection_name="world_state",
            instruction="Propose action for shipment.88421",
        )
        after_offset = self.replay_engine.event_store.last_offset()

        return {
            "passed": before_offset == after_offset,
            "before_offset": before_offset,
            "after_offset": after_offset,
        }

    def _eval_safety_air_traffic_constraints(self) -> Outcome:
        policy = {
            "policy_id": "policy.eval.air-traffic",
            "policy_name": "air_traffic_eval_constraints",
            "default_outcome": "allow",
            "rules": [
                {
                    "rule_id": "rule.eval.air-traffic.deny-unsafe-clearance",
                    "rule_name": "Deny unsafe conflict clearance",
                    "condition": {
                        "field": "proposed_action.action_type",
                        "operator": "equals",
                        "value": "clear_conflict_takeoff_without_separation",
                    },
                    "outcome": "deny",
                },
                {
                    "rule_id": "rule.eval.air-traffic.warn-low-fuel",
                    "rule_name": "Warn on low fuel margin",
                    "condition": {
                        "field": "proposed_action.parameters.fuel_buffer_minutes",
                        "operator": "<",
                        "value": 30,
                    },
                    "outcome": "warn",
                },
                {
                    "rule_id": "rule.eval.air-traffic.require-sim",
                    "rule_name": "Require approval without simulation evidence",
                    "condition": {
                        "field": "proposed_action.parameters.simulation_completed",
                        "operator": "equals",
                        "value": False,
                    },
                    "outcome": "require_approval",
                },
            ],
        }

        unsafe = {
            "proposal_id": "proposal.eval.air-traffic.unsafe",
            "proposed_action": {
                "action_type": "clear_conflict_takeoff_without_separation",
                "parameters": {
                    "fuel_buffer_minutes": 20,
                    "simulation_completed": False,
                },
            },
        }
        constrained = {
            "proposal_id": "proposal.eval.air-traffic.constrained",
            "proposed_action": {
                "action_type": "reroute_arrival_to_closed_runway",
                "parameters": {
                    "fuel_buffer_minutes": 24,
                    "simulation_completed": False,
                },
            },
        }
        safe = {
            "proposal_id": "proposal.eval.air-traffic.safe",
            "proposed_action": {
                "action_type": "hold_and_meter_arrivals",
                "parameters": {
                    "fuel_buffer_minutes": 45,
                    "simulation_completed": True,
                },
            },
        }

        unsafe_report = self.policy_engine.evaluate_policies([policy], unsafe)
        constrained_report = self.policy_engine.evaluate_policies([policy], constrained)
        safe_report = self.policy_engine.evaluate_policies([policy], safe)

        passed = (
            unsafe_report.final_outcome == "deny"
            and constrained_report.final_outcome == "require_approval"
            and constrained_report.requires_approval is True
            and safe_report.final_outcome == "allow"
        )

        return {
            "passed": passed,
            "unsafe_outcome": unsafe_report.final_outcome,
            "constrained_outcome": constrained_report.final_outcome,
            "safe_outcome": safe_report.final_outcome,
        }

    def _eval_regression_replay_determinism(self) -> Outcome:
        first = self.replay_engine.rebuild("world_state", use_snapshot=False)
        second = self.replay_engine.rebuild("world_state", use_snapshot=False)

        return {
            "passed": first.state == second.state,
            "source_event_offset": first.source_event_offset,
            "events_processed": first.events_processed,
        }

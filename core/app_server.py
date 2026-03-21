from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from core.app_protocol import (
    PROTOCOL_VERSION,
    build_error_envelope,
    build_notification,
    build_response_envelope,
    is_compatible,
    validate_request_envelope,
)
from core.connectors import (
    ConnectorRuntime,
    InboundConnectorConfig,
    OutboundConnectorConfig,
    PermanentConnectorError,
    RetryPolicy,
    TransientConnectorError,
)
from adapters.registry import AdapterRegistry
from core.eval_harness import EvalHarness
from core.observability import ObservabilityStore
from core.policy_engine import DeterministicPolicyEngine
from core.provenance import normalize_evidence_ref, redact_sensitive_payload, stable_fingerprint
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class Session:
    session_id: str
    created_at: str
    status: str = "open"


@dataclass
class Task:
    task_id: str
    session_id: str
    method: str
    params: Dict[str, Any]
    created_at: str
    status: str = "queued"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ApprovalRequest:
    approval_id: str
    session_id: str
    task_id: str
    status: str
    requested_at: str
    reason: str
    payload: Dict[str, Any] = field(default_factory=dict)
    decided_at: Optional[str] = None
    comment: Optional[str] = None
    required_roles: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    allow_escalation: bool = True
    allow_override: bool = False
    chain: List[Dict[str, Any]] = field(default_factory=list)


class WorldRuntimeAppServer:
    def __init__(
        self,
        reasoning_adapter: ReasoningAdapter,
        simulation_engine: SimulationEngine,
        replay_engine: Optional[ReplayEngine] = None,
        policy_engine: Optional[DeterministicPolicyEngine] = None,
        eval_harness: Optional[EvalHarness] = None,
        observability: Optional[ObservabilityStore] = None,
        connector_runtime: Optional[ConnectorRuntime] = None,
    ) -> None:
        self.reasoning_adapter = reasoning_adapter
        self.simulation_engine = simulation_engine
        self.policy_engine = policy_engine or DeterministicPolicyEngine()
        self.replay_engine = replay_engine or reasoning_adapter.replay_engine
        self.observability = observability or ObservabilityStore()
        self.connector_runtime = connector_runtime or ConnectorRuntime(self.replay_engine.event_store)
        self.eval_harness = eval_harness or EvalHarness(
            replay_engine=self.replay_engine,
            simulation_engine=self.simulation_engine,
            reasoning_adapter=self.reasoning_adapter,
            policy_engine=self.policy_engine,
            observability=self.observability,
        )

        self.sessions: Dict[str, Session] = {}
        self.tasks: Dict[str, Task] = {}
        self.events_by_session: Dict[str, List[Dict[str, Any]]] = {}
        self.approvals: Dict[str, ApprovalRequest] = {}
        self.decisions: Dict[str, Dict[str, Any]] = {}
        self.eval_reports: Dict[str, Dict[str, Any]] = {}
        self._repo_root = Path(__file__).resolve().parents[1]
        world_game_adapter = AdapterRegistry.with_defaults().get("adapter-world-game")
        self.world_game_service = world_game_adapter.build_service(
            repo_root=self._repo_root,
            policy_engine=self.policy_engine,
        )
        self.world_game_context_by_session = self.world_game_service.context_by_session
        self._rehydrate_approvals()

    def protocol_inspect(self) -> Dict[str, Any]:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "compatibility_policy": "major-compatible",
            "legacy_methods_supported": True,
        }

    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        valid, reason = validate_request_envelope(message)
        request_id = message.get("id") if isinstance(message, dict) else None
        if not valid:
            return build_error_envelope(
                request_id=request_id,
                code="invalid_request",
                message=reason or "invalid request",
            )

        client_version = message["protocol_version"]
        if not is_compatible(client_version):
            return build_error_envelope(
                request_id=request_id,
                code="protocol_version_incompatible",
                message="incompatible protocol version",
                details={
                    "client_version": client_version,
                    "server_version": PROTOCOL_VERSION,
                },
            )

        legacy = self.handle_request(
            method=message["method"],
            params=message.get("params"),
        )
        if legacy.get("ok"):
            return build_response_envelope(
                request_id=message["id"],
                result=legacy["result"],
            )
        return build_error_envelope(
            request_id=message["id"],
            code="method_execution_error",
            message=legacy.get("error", "unknown error"),
            details={"method": message.get("method")},
        )

    def handle_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = params or {}
        trace_id = self.observability.start_trace(
            name="app_server.handle_request",
            component="app_server",
            context={"method": method},
        )
        self.observability.emit(
            component="app_server",
            event_type="request.received",
            trace_id=trace_id,
            attributes={"method": method},
        )

        handlers = {
            "session.create": self.session_create,
            "session.resume": self.session_resume,
            "session.close": self.session_close,
            "task.submit": self.task_submit,
            "task.status": self.task_status,
            "task.events.subscribe": self.task_events_subscribe,
            "approval.request": self.approval_request,
            "approval.respond": self.approval_respond,
            "approval.get": self.approval_get,
            "approval.history": self.approval_history,
            "eval.list": self.eval_list,
            "eval.run": self.eval_run,
            "eval.report": self.eval_report,
            "simulation.create": self.simulation_create,
            "simulation.run": self.simulation_run,
            "simulation.discard": self.simulation_discard,
            "policy.evaluate": self.policy_evaluate,
            "proposal.submit": self.proposal_submit,
            "decision.create": self.decision_create,
            "world_game.scenario.list": self.world_game_scenario_list,
            "world_game.session.create": self.world_game_session_create,
            "world_game.session.get": self.world_game_session_get,
            "world_game.session.actor.add": self.world_game_session_actor_add,
            "world_game.session.actor.remove": self.world_game_session_actor_remove,
            "world_game.session.actor.list": self.world_game_session_actor_list,
            "world_game.session.stage.get": self.world_game_session_stage_get,
            "world_game.session.stage.set": self.world_game_session_stage_set,
            "world_game.session.stage.advance": self.world_game_session_stage_advance,
            "world_game.session.export": self.world_game_session_export,
            "world_game.session.import": self.world_game_session_import,
            "world_game.scenario.load": self.world_game_scenario_load,
            "world_game.turn.run": self.world_game_turn_run,
            "world_game.branch.create": self.world_game_branch_create,
            "world_game.branch.compare": self.world_game_branch_compare,
            "world_game.replay.run": self.world_game_replay_run,
            "world_game.network.inspect": self.world_game_network_inspect,
            "world_game.equity.report": self.world_game_equity_report,
            "world_game.proposal.create": self.world_game_proposal_create,
            "world_game.proposal.update": self.world_game_proposal_update,
            "world_game.proposal.get": self.world_game_proposal_get,
            "world_game.proposal.list": self.world_game_proposal_list,
            "world_game.proposal.submit": self.world_game_proposal_submit,
            "world_game.proposal.adopt": self.world_game_proposal_adopt,
            "world_game.proposal.reject": self.world_game_proposal_reject,
            "world_game.annotation.create": self.world_game_annotation_create,
            "world_game.annotation.list": self.world_game_annotation_list,
            "world_game.annotation.update": self.world_game_annotation_update,
            "world_game.annotation.archive": self.world_game_annotation_archive,
            "world_game.provenance.inspect": self.world_game_provenance_inspect,
            "world_game.authoring.template.list": self.world_game_authoring_template_list,
            "world_game.authoring.draft.create": self.world_game_authoring_draft_create,
            "world_game.authoring.draft.validate": self.world_game_authoring_draft_validate,
            "world_game.authoring.bundle.publish": self.world_game_authoring_bundle_publish,
            "world_game.authoring.bundle.instantiate": self.world_game_authoring_bundle_instantiate,
            "protocol.inspect": self.protocol_inspect,
            "telemetry.summary": self.telemetry_summary,
            "telemetry.events": self.telemetry_events,
            "trace.list": self.trace_list,
            "diagnostics.dashboard": self.diagnostics_dashboard,
            "audit.export": self.audit_export,
            "connector.inbound.run": self.connector_inbound_run,
            "connector.outbound.run": self.connector_outbound_run,
            "connector.dead_letter.list": self.connector_dead_letter_list,
            "connector.dead_letter.replay": self.connector_dead_letter_replay,
            "connector.policy_decision.list": self.connector_policy_decision_list,
            "connector.policy_decision.get": self.connector_policy_decision_get,
        }

        handler = handlers.get(method)
        if handler is None:
            self.observability.emit(
                component="app_server",
                event_type="request.unknown_method",
                severity="error",
                trace_id=trace_id,
                attributes={"method": method},
            )
            self.observability.finish_trace(trace_id, status="failed", error="unknown_method")
            return {
                "ok": False,
                "error": "unknown_method",
                "method": method,
            }

        try:
            result = handler(**payload)
            self.observability.emit(
                component="app_server",
                event_type="request.completed",
                trace_id=trace_id,
                attributes={"method": method},
            )
            self.observability.finish_trace(trace_id, status="completed")
            return {
                "ok": True,
                "result": result,
            }
        except Exception as exc:
            self.observability.emit(
                component="app_server",
                event_type="request.failed",
                severity="error",
                trace_id=trace_id,
                attributes={"method": method, "error": str(exc)},
            )
            self.observability.finish_trace(trace_id, status="failed", error=str(exc))
            return {
                "ok": False,
                "error": str(exc),
                "method": method,
            }

    def session_create(self) -> Dict[str, Any]:
        session_id = "session.%s" % uuid4().hex[:12]
        session = Session(session_id=session_id, created_at=_utc_now())
        self.sessions[session_id] = session
        self.events_by_session.setdefault(session_id, [])
        return {
            "session_id": session_id,
            "created_at": session.created_at,
            "status": session.status,
        }

    def session_resume(self, session_id: str) -> Dict[str, Any]:
        session = self._require_session(session_id)
        return {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "status": session.status,
        }

    def session_close(self, session_id: str) -> Dict[str, Any]:
        session = self._require_session(session_id)
        session.status = "closed"
        self.world_game_service.clear_session(session_id)
        self._emit(session_id, "session.closed", {"session_id": session_id})
        return {
            "session_id": session_id,
            "status": session.status,
        }

    def task_submit(self, session_id: str, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session = self._require_session(session_id)
        if session.status != "open":
            raise ValueError("session is not open")

        trace_id = self.observability.start_trace(
            name="app_server.task_submit",
            component="app_server",
            context={"session_id": session_id, "method": method},
        )
        task_id = "task.%s" % uuid4().hex[:12]
        task = Task(
            task_id=task_id,
            session_id=session_id,
            method=method,
            params=deepcopy(params or {}),
            created_at=_utc_now(),
            status="running",
        )
        self.tasks[task_id] = task

        self.observability.trace_event(trace_id, "task.created", {"task_id": task_id})
        self._emit(session_id, "task.started", {"task_id": task_id, "method": method})
        self._emit(session_id, "task.progress", {"task_id": task_id, "message": "dispatch"})

        try:
            result = self._execute_task(task)
            task.result = result
            task.status = "completed"
            self._emit(session_id, "task.completed", {"task_id": task_id})
            self.observability.finish_trace(
                trace_id,
                status="completed",
                extra={"task_id": task_id, "status": task.status},
            )
            return {
                "task_id": task_id,
                "status": task.status,
                "result": deepcopy(result),
            }
        except Exception as exc:
            task.status = "failed"
            task.error = str(exc)
            self.observability.finish_trace(
                trace_id,
                status="failed",
                error=task.error,
                extra={"task_id": task_id, "status": task.status},
            )
            self._emit(
                session_id,
                "error.raised",
                {"task_id": task_id, "error": task.error},
            )
            raise

    def task_status(self, task_id: str) -> Dict[str, Any]:
        task = self._require_task(task_id)
        return {
            "task_id": task.task_id,
            "session_id": task.session_id,
            "method": task.method,
            "status": task.status,
            "result": deepcopy(task.result),
            "error": task.error,
        }

    def task_events_subscribe(self, session_id: str, since: int = 0) -> Dict[str, Any]:
        self._require_session(session_id)
        events = self.events_by_session.get(session_id, [])
        if since < 0:
            since = 0
        sliced = events[since:]
        return {
            "session_id": session_id,
            "from_index": since,
            "next_index": since + len(sliced),
            "events": deepcopy(sliced),
        }

    def approval_request(
        self,
        session_id: str,
        task_id: str,
        reason: str,
        payload: Optional[Dict[str, Any]] = None,
        actor_requirements: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        self._require_task(task_id)
        requirements = actor_requirements or {}
        return self._create_approval(
            session_id=session_id,
            task_id=task_id,
            reason=reason,
            payload=payload,
            required_roles=requirements.get("required_roles"),
            required_capabilities=requirements.get("required_capabilities"),
            allow_escalation=bool(requirements.get("allow_escalation", True)),
            allow_override=bool(requirements.get("allow_override", False)),
        )

    def approval_respond(
        self,
        approval_id: str,
        decision: str,
        comment: Optional[str] = None,
        actor: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        approval = self._require_approval(approval_id)
        if approval.status != "pending":
            raise ValueError("approval is not pending")
        if decision not in {"approved", "rejected", "escalated", "overridden"}:
            raise ValueError("decision must be approved, rejected, escalated, or overridden")

        actor_ref = self._normalize_actor(actor)
        self._authorize_approval_actor(approval, actor_ref, decision)

        approval.status = decision
        approval.decided_at = _utc_now()
        approval.comment = comment
        approval.chain.append(
            {
                "sequence": len(approval.chain) + 1,
                "action": decision,
                "actor": deepcopy(actor_ref),
                "comment": comment,
                "at": approval.decided_at,
            }
        )
        self._append_approval_event(approval, "approval.recorded", entry=approval.chain[-1])

        self._emit(
            approval.session_id,
            "task.progress",
            {
                "task_id": approval.task_id,
                "message": "approval.%s" % decision,
                "approval_id": approval.approval_id,
            },
        )

        return {
            "approval_id": approval.approval_id,
            "status": approval.status,
            "decided_at": approval.decided_at,
            "comment": approval.comment,
            "actor": deepcopy(actor_ref),
            "approval_chain": deepcopy(approval.chain),
        }

    def approval_get(self, session_id: str, approval_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        approval = self._require_approval(approval_id)
        return self._approval_payload(approval)

    def approval_history(self, session_id: str, approval_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        approval = self._require_approval(approval_id)
        return {
            "approval_id": approval.approval_id,
            "status": approval.status,
            "approval_chain": deepcopy(approval.chain),
        }

    def eval_list(self) -> Dict[str, Any]:
        return {"evals": self.eval_harness.list_evals()}

    def eval_run(self, session_id: str, eval_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        report = self.eval_harness.run_eval(eval_id)

        report_id = "evalreport.%s" % uuid4().hex[:12]
        report["report_id"] = report_id
        self.eval_reports[report_id] = deepcopy(report)

        self._emit(session_id, "eval.completed", {"eval_id": eval_id, "report_id": report_id})
        return deepcopy(report)

    def eval_report(self, report_id: str) -> Dict[str, Any]:
        report = self.eval_reports.get(report_id)
        if report is None:
            raise ValueError("report_id not found")
        return deepcopy(report)

    def simulation_create(
        self,
        session_id: str,
        simulation_id: str,
        projection_name: str,
        parent_simulation_id: Optional[str] = None,
        scenario_name: Optional[str] = None,
        assumptions: Optional[List[str]] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        branch = self.simulation_engine.create_branch(
            simulation_id=simulation_id,
            projection_name=projection_name,
            parent_simulation_id=parent_simulation_id,
            scenario_name=scenario_name,
            assumptions=assumptions,
            inputs=inputs,
        )
        return {
            "simulation_id": branch.simulation_id,
            "status": branch.status,
            "base_event_offset": branch.base_event_offset,
        }

    def simulation_run(self, session_id: str, simulation_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        result = self.simulation_engine.run(simulation_id)
        return result.as_dict()

    def simulation_discard(self, session_id: str, simulation_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        self.simulation_engine.discard(simulation_id)
        return {"simulation_id": simulation_id, "status": "cancelled"}

    def policy_evaluate(
        self,
        session_id: str,
        policies: List[Dict[str, Any]],
        proposal: Dict[str, Any],
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        report = self.policy_engine.evaluate_policies(policies, proposal)
        return report.as_dict()

    def proposal_submit(
        self,
        session_id: str,
        proposal: Dict[str, Any],
        policies: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        selected_policies = policies or []
        report = self.policy_engine.evaluate_policies(selected_policies, proposal)

        approval = None
        if report.requires_approval:
            approval = self.approval_request(
                session_id=session_id,
                task_id=self._create_virtual_task_for_proposal(session_id, proposal),
                reason="policy requires approval",
                payload={"proposal_id": proposal.get("proposal_id")},
                actor_requirements={
                    "required_capabilities": ["approval.respond", "proposal.approve"],
                    "allow_escalation": True,
                    "allow_override": True,
                },
            )

        return {
            "proposal_id": proposal.get("proposal_id"),
            "policy_report": report.as_dict(),
            "approval": approval,
        }

    def decision_create(
        self,
        session_id: str,
        proposal: Dict[str, Any],
        policy_report: Dict[str, Any],
        approval_status: str = "not_required",
        approval_id: Optional[str] = None,
        approval_chain: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)

        final_outcome = policy_report.get("final_outcome", "allow")
        status = "rejected" if final_outcome == "deny" else "approved"
        decision_id = "decision.%s" % uuid4().hex[:12]
        resolved_chain = list(approval_chain or [])
        if approval_id:
            approval = self._require_approval(approval_id)
            approval_status = approval.status
            resolved_chain = deepcopy(approval.chain)

        approvals = []
        for entry in resolved_chain:
            approvals.append(
                {
                    "approver": deepcopy(entry.get("actor", {})),
                    "status": entry.get("action"),
                    "comment": entry.get("comment"),
                    "decided_at": entry.get("at"),
                }
            )

        decision = {
            "decision_id": decision_id,
            "status": status,
            "selected_proposal_id": proposal.get("proposal_id"),
            "selected_action": deepcopy(proposal.get("proposed_action", {})),
            "policy_results": deepcopy(policy_report.get("evaluations", [])),
            "approval_status": approval_status,
            "approval_id": approval_id,
            "approvals": approvals,
            "approval_chain": resolved_chain,
            "created_at": _utc_now(),
            "provenance": self._build_decision_provenance(
                session_id=session_id,
                decision_id=decision_id,
                proposal=proposal,
                policy_report=policy_report,
                approval_id=approval_id,
                approval_chain=resolved_chain,
                outcome=status,
            ),
        }
        self.decisions[decision_id] = deepcopy(decision)
        return decision

    def world_game_scenario_list(self, examples_root: Optional[str] = None) -> Dict[str, Any]:
        return self.world_game_service.scenario_list(examples_root=examples_root)

    def world_game_session_create(
        self,
        session_id: str,
        label: Optional[str] = None,
        description: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_type: str = "human",
        roles: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        display_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.collaboration_session_create(
            session_id=session_id,
            label=label,
            description=description,
            actor_id=actor_id,
            actor_type=actor_type,
            roles=roles,
            capabilities=capabilities,
            display_name=display_name,
        )

    def world_game_session_get(self, session_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.collaboration_session_get(session_id=session_id)

    def world_game_session_actor_add(
        self,
        session_id: str,
        actor_id: str,
        actor_type: str = "human",
        roles: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        display_name: Optional[str] = None,
        requested_by_actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.collaboration_actor_add(
            session_id=session_id,
            actor_id=actor_id,
            actor_type=actor_type,
            roles=roles,
            capabilities=capabilities,
            display_name=display_name,
            requested_by_actor_id=requested_by_actor_id,
        )

    def world_game_session_actor_remove(
        self,
        session_id: str,
        actor_id: str,
        requested_by_actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.collaboration_actor_remove(
            session_id=session_id,
            actor_id=actor_id,
            requested_by_actor_id=requested_by_actor_id,
        )

    def world_game_session_actor_list(self, session_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.collaboration_actor_list(session_id=session_id)

    def world_game_session_stage_get(self, session_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.session_stage_get(session_id=session_id)

    def world_game_session_stage_set(
        self,
        session_id: str,
        stage: str,
        actor_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.session_stage_set(
            session_id=session_id,
            stage=stage,
            actor_id=actor_id,
            reason=reason,
        )

    def world_game_session_stage_advance(
        self,
        session_id: str,
        actor_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.session_stage_advance(
            session_id=session_id,
            actor_id=actor_id,
            reason=reason,
        )

    def world_game_session_export(
        self,
        session_id: str,
        output_path: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.collaboration_session_export(
            session_id=session_id,
            output_path=output_path,
            actor_id=actor_id,
        )

    def world_game_session_import(
        self,
        session_id: str,
        bundle: Optional[Dict[str, Any]] = None,
        bundle_path: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.collaboration_session_import(
            session_id=session_id,
            bundle=bundle,
            bundle_path=bundle_path,
            actor_id=actor_id,
        )

    def world_game_scenario_load(
        self,
        session_id: str,
        scenario_id: Optional[str] = None,
        scenario_path: Optional[str] = None,
        branch_id: str = "baseline",
        policy_pack_path: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.scenario_load(
            session_id=session_id,
            scenario_id=scenario_id,
            scenario_path=scenario_path,
            branch_id=branch_id,
            policy_pack_path=policy_pack_path,
            actor_id=actor_id,
        )

    def world_game_turn_run(
        self,
        session_id: str,
        branch_id: str = "baseline",
        intervention_ids: Optional[List[str]] = None,
        shock_ids: Optional[List[str]] = None,
        approval_status: str = "approved",
        actor_id: Optional[str] = None,
        proposal_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.turn_run(
            session_id=session_id,
            branch_id=branch_id,
            intervention_ids=intervention_ids,
            shock_ids=shock_ids,
            approval_status=approval_status,
            actor_id=actor_id,
            proposal_id=proposal_id,
        )

    def world_game_branch_create(
        self,
        session_id: str,
        source_branch_id: str,
        branch_id: str,
        actor_id: Optional[str] = None,
        proposal_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.branch_create(
            session_id=session_id,
            source_branch_id=source_branch_id,
            branch_id=branch_id,
            actor_id=actor_id,
            proposal_id=proposal_id,
        )

    def world_game_branch_compare(
        self,
        session_id: str,
        branch_ids: Optional[List[str]] = None,
        include_annotation_summary: bool = False,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.branch_compare(
            session_id=session_id,
            branch_ids=branch_ids,
            include_annotation_summary=include_annotation_summary,
        )

    def world_game_replay_run(self, session_id: str, branch_id: str = "baseline") -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.replay_run(session_id=session_id, branch_id=branch_id)

    def world_game_network_inspect(self, session_id: str, branch_id: str = "baseline") -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.network_inspect(session_id=session_id, branch_id=branch_id)

    def world_game_equity_report(
        self,
        session_id: str,
        branch_id: str = "baseline",
        branch_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.equity_report(
            session_id=session_id,
            branch_id=branch_id,
            branch_ids=branch_ids,
        )

    def world_game_proposal_create(
        self,
        session_id: str,
        proposal_id: Optional[str] = None,
        title: str = "",
        rationale: str = "",
        assumptions: Optional[List[str]] = None,
        intended_interventions: Optional[List[str]] = None,
        expected_outcomes: Optional[List[str]] = None,
        evidence_refs: Optional[List[Dict[str, Any]]] = None,
        planned_turn_sequence: Optional[List[Dict[str, Any]]] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.proposal_create(
            session_id=session_id,
            proposal_id=proposal_id,
            title=title,
            rationale=rationale,
            assumptions=assumptions,
            intended_interventions=intended_interventions,
            expected_outcomes=expected_outcomes,
            evidence_refs=evidence_refs,
            planned_turn_sequence=planned_turn_sequence,
            actor_id=actor_id,
        )

    def world_game_proposal_update(
        self,
        session_id: str,
        proposal_id: str,
        updates: Optional[Dict[str, Any]] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.proposal_update(
            session_id=session_id,
            proposal_id=proposal_id,
            updates=updates,
            actor_id=actor_id,
        )

    def world_game_proposal_get(self, session_id: str, proposal_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.proposal_get(session_id=session_id, proposal_id=proposal_id)

    def world_game_proposal_list(self, session_id: str, status: Optional[str] = None) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.proposal_list(session_id=session_id, status=status)

    def world_game_proposal_submit(
        self,
        session_id: str,
        proposal_id: str,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.proposal_submit(
            session_id=session_id,
            proposal_id=proposal_id,
            actor_id=actor_id,
        )

    def world_game_proposal_adopt(
        self,
        session_id: str,
        proposal_id: str,
        branch_id: Optional[str] = None,
        source_branch_id: str = "baseline",
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.proposal_adopt(
            session_id=session_id,
            proposal_id=proposal_id,
            branch_id=branch_id,
            source_branch_id=source_branch_id,
            actor_id=actor_id,
        )

    def world_game_proposal_reject(
        self,
        session_id: str,
        proposal_id: str,
        actor_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.proposal_reject(
            session_id=session_id,
            proposal_id=proposal_id,
            actor_id=actor_id,
            reason=reason,
        )

    def world_game_annotation_create(
        self,
        session_id: str,
        annotation_id: Optional[str] = None,
        annotation_type: str = "",
        target_type: str = "",
        target_id: str = "",
        body: str = "",
        evidence_refs: Optional[List[Dict[str, Any]]] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.annotation_create(
            session_id=session_id,
            annotation_id=annotation_id,
            annotation_type=annotation_type,
            target_type=target_type,
            target_id=target_id,
            body=body,
            evidence_refs=evidence_refs,
            actor_id=actor_id,
        )

    def world_game_annotation_list(
        self,
        session_id: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        include_archived: bool = False,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.annotation_list(
            session_id=session_id,
            target_type=target_type,
            target_id=target_id,
            include_archived=include_archived,
        )

    def world_game_annotation_update(
        self,
        session_id: str,
        annotation_id: str,
        body: Optional[str] = None,
        evidence_refs: Optional[List[Dict[str, Any]]] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.annotation_update(
            session_id=session_id,
            annotation_id=annotation_id,
            body=body,
            evidence_refs=evidence_refs,
            actor_id=actor_id,
        )

    def world_game_annotation_archive(
        self,
        session_id: str,
        annotation_id: str,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.annotation_archive(
            session_id=session_id,
            annotation_id=annotation_id,
            actor_id=actor_id,
        )

    def world_game_provenance_inspect(
        self,
        session_id: str,
        artifact_type: Optional[str] = None,
        artifact_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return self.world_game_service.provenance_inspect(
            session_id=session_id,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
        )

    def world_game_authoring_template_list(self, authoring_root: Optional[str] = None) -> Dict[str, Any]:
        return self.world_game_service.authoring_template_list(authoring_root=authoring_root)

    def world_game_authoring_draft_create(
        self,
        source_bundle_path: Optional[str] = None,
        source_bundle: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None,
        bundle_id: Optional[str] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        content_version: Optional[str] = None,
        deterministic_version_seed: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.world_game_service.authoring_draft_create(
            source_bundle_path=source_bundle_path,
            source_bundle=source_bundle,
            output_path=output_path,
            bundle_id=bundle_id,
            label=label,
            description=description,
            content_version=content_version,
            deterministic_version_seed=deterministic_version_seed,
            tags=tags,
            created_at=created_at,
            updated_at=updated_at,
        )

    def world_game_authoring_draft_validate(
        self,
        draft_path: Optional[str] = None,
        draft_bundle: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.world_game_service.authoring_draft_validate(
            draft_path=draft_path,
            draft_bundle=draft_bundle,
        )

    def world_game_authoring_bundle_publish(
        self,
        draft_path: Optional[str] = None,
        draft_bundle: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None,
        published_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.world_game_service.authoring_bundle_publish(
            draft_path=draft_path,
            draft_bundle=draft_bundle,
            output_path=output_path,
            published_at=published_at,
            updated_at=updated_at,
        )

    def world_game_authoring_bundle_instantiate(
        self,
        bundle_path: Optional[str] = None,
        bundle: Optional[Dict[str, Any]] = None,
        template_id: str = "",
        parameter_values: Optional[Dict[str, Any]] = None,
        scenario_output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.world_game_service.authoring_bundle_instantiate(
            bundle_path=bundle_path,
            bundle=bundle,
            template_id=template_id,
            parameter_values=parameter_values,
            scenario_output_path=scenario_output_path,
        )

    def telemetry_summary(self) -> Dict[str, Any]:
        return self.observability.summary()

    def telemetry_events(
        self,
        since: int = 0,
        limit: Optional[int] = None,
        component: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.observability.list_events(
            since=since,
            limit=limit,
            component=component,
            severity=severity,
        )

    def trace_list(self, limit: Optional[int] = None) -> Dict[str, Any]:
        traces = self.observability.list_traces(limit=limit)
        return {"traces": traces}

    def diagnostics_dashboard(self) -> Dict[str, Any]:
        return self.observability.dashboard()

    def audit_export(
        self,
        session_id: str,
        decision_id: Optional[str] = None,
        include_telemetry: bool = True,
    ) -> Dict[str, Any]:
        self._require_session(session_id)

        decisions = self._collect_decisions(decision_id=decision_id)
        approval_ids = sorted(
            {
                item.get("approval_id")
                for item in decisions
                if item.get("approval_id")
            }
        )
        approvals = [self._approval_payload(self.approvals[approval_id]) for approval_id in approval_ids]

        connector_decisions = self.connector_runtime.list_policy_decisions()
        if decision_id:
            connector_decisions = [
                item for item in connector_decisions if item.get("decision_id") == decision_id
            ]

        traces = [
            trace for trace in self.observability.list_traces() if self._trace_matches_session(trace, session_id)
        ]
        telemetry_events: List[Dict[str, Any]] = []
        if include_telemetry:
            telemetry_events = [
                event
                for event in self.observability.list_events(since=0).get("events", [])
                if event.get("session_id") == session_id
            ]

        export_body = {
            "scope": {
                "session_id": session_id,
                "decision_id": decision_id,
            },
            "artifacts": {
                "decisions": sorted(decisions, key=lambda item: item.get("decision_id", "")),
                "approvals": sorted(approvals, key=lambda item: item.get("approval_id", "")),
                "connector_policy_decisions": sorted(
                    connector_decisions, key=lambda item: item.get("decision_id", "")
                ),
                "session_events": deepcopy(self.events_by_session.get(session_id, [])),
                "traces": sorted(traces, key=lambda item: item.get("trace_id", "")),
                "telemetry_events": sorted(telemetry_events, key=lambda item: item.get("event_id", "")),
            },
        }
        redacted_payload, redaction_report = redact_sensitive_payload(export_body)
        diagnostics = self._build_provenance_diagnostics(redacted_payload["artifacts"])
        fingerprint = stable_fingerprint(
            {
                "scope": redacted_payload["scope"],
                "artifacts": redacted_payload["artifacts"],
                "diagnostics": diagnostics,
            }
        )
        return {
            "export_version": "1.0",
            "generated_at": _utc_now(),
            "scope": redacted_payload["scope"],
            "artifacts": redacted_payload["artifacts"],
            "diagnostics": diagnostics,
            "redaction": redaction_report,
            "fingerprint": fingerprint,
        }

    def connector_inbound_run(
        self,
        session_id: str,
        connector_id: str,
        event_type_map: Dict[str, str],
        external_event: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        retry: Optional[Dict[str, Any]] = None,
        fail_until_attempt: int = 0,
        policies: Optional[List[Dict[str, Any]]] = None,
        approval_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)

        config = InboundConnectorConfig(
            connector_id=connector_id,
            event_type_map=dict(event_type_map),
            retry=RetryPolicy.from_config(retry),
        )

        def _preprocess(event: Dict[str, Any], attempt: int) -> Dict[str, Any]:
            if attempt <= fail_until_attempt:
                raise TransientConnectorError("simulated transient inbound error")
            return event

        policy_report = None
        approval = None
        decision = None
        resolved_idempotency_key = self._resolve_connector_idempotency_key(
            direction="inbound",
            connector_id=connector_id,
            payload=external_event,
            explicit_key=idempotency_key,
        )

        if policies:
            mapped_event = event_type_map.get(external_event.get("event_type"))
            policy_input = self._build_connector_policy_input(
                direction="inbound",
                connector_id=connector_id,
                idempotency_key=resolved_idempotency_key,
                payload=external_event,
                mapped_operation_type=mapped_event,
            )
            report = self.policy_engine.evaluate_connector_policies(
                policies=policies,
                proposal=policy_input["proposal"],
                connector_context=policy_input["context"],
            )
            policy_report = report.as_dict()
            if report.denied:
                decision = self._record_connector_policy_decision(
                    connector_id=connector_id,
                    direction="inbound",
                    idempotency_key=resolved_idempotency_key,
                    policy_report=policy_report,
                    status="rejected",
                    provider=policy_input["context"].get("provider"),
                    source=policy_input["context"].get("source"),
                )
                self._emit(
                    session_id,
                    "connector.inbound.rejected",
                    {"connector_id": connector_id, "idempotency_key": resolved_idempotency_key},
                )
                return {
                    "status": "rejected",
                    "direction": "inbound",
                    "connector_id": connector_id,
                    "idempotency_key": resolved_idempotency_key,
                    "policy_report": policy_report,
                    "decision_id": decision["decision_id"],
                }
            if report.requires_approval:
                approval = self._resolve_connector_approval(
                    session_id=session_id,
                    connector_id=connector_id,
                    direction="inbound",
                    idempotency_key=resolved_idempotency_key,
                    approval_id=approval_id,
                )
                if approval["status"] not in {"approved", "overridden"}:
                    if approval["status"] == "pending":
                        decision_status = "awaiting_approval"
                    elif approval["status"] == "escalated":
                        decision_status = "escalated"
                    else:
                        decision_status = "rejected"
                    decision = self._record_connector_policy_decision(
                        connector_id=connector_id,
                        direction="inbound",
                        idempotency_key=resolved_idempotency_key,
                        policy_report=policy_report,
                        status=decision_status,
                        provider=policy_input["context"].get("provider"),
                        source=policy_input["context"].get("source"),
                        approval_id=approval["approval_id"],
                        approval_chain=approval.get("approval_chain"),
                    )
                    self._emit(
                        session_id,
                        "connector.inbound.%s" % decision_status,
                        {"connector_id": connector_id, "idempotency_key": resolved_idempotency_key},
                    )
                    return {
                        "status": decision_status,
                        "direction": "inbound",
                        "connector_id": connector_id,
                        "idempotency_key": resolved_idempotency_key,
                        "policy_report": policy_report,
                        "approval": approval,
                        "decision_id": decision["decision_id"],
                    }

        result = self.connector_runtime.run_inbound(
            config=config,
            external_event=external_event,
            idempotency_key=idempotency_key,
            preprocessor=_preprocess,
        )
        if policy_report is not None:
            decision = self._record_connector_policy_decision(
                connector_id=connector_id,
                direction="inbound",
                idempotency_key=result["idempotency_key"],
                policy_report=policy_report,
                status=result["status"],
                provider=external_event.get("provider"),
                source=external_event.get("source"),
                approval_id=approval["approval_id"] if approval else None,
                approval_chain=approval.get("approval_chain") if approval else None,
                execution_result=result,
            )
            result["policy_report"] = policy_report
            if approval:
                result["approval"] = approval
            result["decision_id"] = decision["decision_id"]
        self._emit(
            session_id,
            "connector.inbound.%s" % result["status"],
            {"connector_id": connector_id, "idempotency_key": result["idempotency_key"]},
        )
        return result

    def connector_outbound_run(
        self,
        session_id: str,
        connector_id: str,
        action_type_map: Dict[str, str],
        action: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        retry: Optional[Dict[str, Any]] = None,
        fail_until_attempt: int = 0,
        fail_permanently: bool = False,
        transport_plugin: Optional[Dict[str, Any]] = None,
        policies: Optional[List[Dict[str, Any]]] = None,
        approval_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)

        config = OutboundConnectorConfig(
            connector_id=connector_id,
            action_type_map=dict(action_type_map),
            retry=RetryPolicy.from_config(retry),
        )

        def _transport(payload: Dict[str, Any], attempt: int) -> Dict[str, Any]:
            if fail_permanently:
                raise PermanentConnectorError("simulated permanent outbound error")
            if attempt <= fail_until_attempt:
                raise TransientConnectorError("simulated transient outbound error")
            return {"ack": "delivered", "attempt": attempt, "external_action_type": payload["external_action_type"]}

        policy_report = None
        approval = None
        decision = None
        resolved_idempotency_key = self._resolve_connector_idempotency_key(
            direction="outbound",
            connector_id=connector_id,
            payload=action,
            explicit_key=idempotency_key,
        )
        if policies:
            mapped_action = action_type_map.get(action.get("action_type"))
            policy_input = self._build_connector_policy_input(
                direction="outbound",
                connector_id=connector_id,
                idempotency_key=resolved_idempotency_key,
                payload=action,
                mapped_operation_type=mapped_action,
                provider=(transport_plugin or {}).get("provider"),
            )
            report = self.policy_engine.evaluate_connector_policies(
                policies=policies,
                proposal=policy_input["proposal"],
                connector_context=policy_input["context"],
            )
            policy_report = report.as_dict()
            if report.denied:
                decision = self._record_connector_policy_decision(
                    connector_id=connector_id,
                    direction="outbound",
                    idempotency_key=resolved_idempotency_key,
                    policy_report=policy_report,
                    status="rejected",
                    provider=policy_input["context"].get("provider"),
                    source=policy_input["context"].get("source"),
                )
                self._emit(
                    session_id,
                    "connector.outbound.rejected",
                    {"connector_id": connector_id, "idempotency_key": resolved_idempotency_key},
                )
                return {
                    "status": "rejected",
                    "direction": "outbound",
                    "connector_id": connector_id,
                    "idempotency_key": resolved_idempotency_key,
                    "policy_report": policy_report,
                    "decision_id": decision["decision_id"],
                }
            if report.requires_approval:
                approval = self._resolve_connector_approval(
                    session_id=session_id,
                    connector_id=connector_id,
                    direction="outbound",
                    idempotency_key=resolved_idempotency_key,
                    approval_id=approval_id,
                )
                if approval["status"] not in {"approved", "overridden"}:
                    if approval["status"] == "pending":
                        decision_status = "awaiting_approval"
                    elif approval["status"] == "escalated":
                        decision_status = "escalated"
                    else:
                        decision_status = "rejected"
                    decision = self._record_connector_policy_decision(
                        connector_id=connector_id,
                        direction="outbound",
                        idempotency_key=resolved_idempotency_key,
                        policy_report=policy_report,
                        status=decision_status,
                        provider=policy_input["context"].get("provider"),
                        source=policy_input["context"].get("source"),
                        approval_id=approval["approval_id"],
                        approval_chain=approval.get("approval_chain"),
                    )
                    self._emit(
                        session_id,
                        "connector.outbound.%s" % decision_status,
                        {"connector_id": connector_id, "idempotency_key": resolved_idempotency_key},
                    )
                    return {
                        "status": decision_status,
                        "direction": "outbound",
                        "connector_id": connector_id,
                        "idempotency_key": resolved_idempotency_key,
                        "policy_report": policy_report,
                        "approval": approval,
                        "decision_id": decision["decision_id"],
                    }

        selected_transport = None if transport_plugin else _transport
        result = self.connector_runtime.run_outbound(
            config=config,
            action=action,
            transport=selected_transport,
            idempotency_key=idempotency_key,
            transport_plugin=transport_plugin,
        )
        if policy_report is not None:
            decision = self._record_connector_policy_decision(
                connector_id=connector_id,
                direction="outbound",
                idempotency_key=result["idempotency_key"],
                policy_report=policy_report,
                status=result["status"],
                provider=(transport_plugin or {}).get("provider"),
                source=action.get("source"),
                approval_id=approval["approval_id"] if approval else None,
                approval_chain=approval.get("approval_chain") if approval else None,
                execution_result=result,
            )
            result["policy_report"] = policy_report
            if approval:
                result["approval"] = approval
            result["decision_id"] = decision["decision_id"]
        self._emit(
            session_id,
            "connector.outbound.%s" % result["status"],
            {"connector_id": connector_id, "idempotency_key": result["idempotency_key"]},
        )
        return result

    def connector_policy_decision_list(
        self,
        session_id: str,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return {
            "decisions": [
                self._hydrate_connector_decision_approval(decision)
                for decision in self.connector_runtime.list_policy_decisions(
                    connector_id=connector_id,
                    direction=direction,
                )
            ]
        }

    def connector_policy_decision_get(
        self,
        session_id: str,
        decision_id: str,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        decision = self.connector_runtime.get_policy_decision(decision_id)
        if decision is None:
            raise ValueError("decision_id not found")
        return self._hydrate_connector_decision_approval(decision)

    def _hydrate_connector_decision_approval(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        payload = deepcopy(decision)
        approval_id = payload.get("approval_id")
        if approval_id and approval_id in self.approvals:
            payload["approval"] = self._approval_payload(self.approvals[approval_id])
        return payload

    def _approval_payload(self, approval: ApprovalRequest) -> Dict[str, Any]:
        return {
            "approval_id": approval.approval_id,
            "session_id": approval.session_id,
            "task_id": approval.task_id,
            "status": approval.status,
            "reason": approval.reason,
            "payload": deepcopy(approval.payload),
            "requested_at": approval.requested_at,
            "decided_at": approval.decided_at,
            "comment": approval.comment,
            "required_roles": deepcopy(approval.required_roles),
            "required_capabilities": deepcopy(approval.required_capabilities),
            "allow_escalation": approval.allow_escalation,
            "allow_override": approval.allow_override,
            "approval_chain": deepcopy(approval.chain),
        }

    def connector_dead_letter_list(
        self,
        session_id: str,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        return {"dead_letters": self.connector_runtime.list_dead_letters(connector_id=connector_id, direction=direction)}

    def connector_dead_letter_replay(
        self,
        session_id: str,
        dead_letter_id: str,
        event_type_map: Optional[Dict[str, str]] = None,
        action_type_map: Optional[Dict[str, str]] = None,
        retry: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        payload_override: Optional[Dict[str, Any]] = None,
        fail_until_attempt: int = 0,
        fail_permanently: bool = False,
        transport_plugin: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._require_session(session_id)
        dead_letter = self.connector_runtime.get_dead_letter(dead_letter_id)
        if dead_letter is None:
            raise ValueError("dead letter not found: %s" % dead_letter_id)

        inbound_config = None
        outbound_config = None
        replay_transport = None

        if dead_letter["direction"] == "inbound":
            if not event_type_map:
                raise ValueError("event_type_map is required for inbound dead-letter replay")
            inbound_config = InboundConnectorConfig(
                connector_id=dead_letter["connector_id"],
                event_type_map=dict(event_type_map),
                retry=RetryPolicy.from_config(retry),
            )

            def _preprocess(event: Dict[str, Any], attempt: int) -> Dict[str, Any]:
                if attempt <= fail_until_attempt:
                    raise TransientConnectorError("simulated transient inbound error")
                return event

            replay_result = self.connector_runtime.replay_dead_letter(
                dead_letter_id=dead_letter_id,
                inbound_config=inbound_config,
                preprocessor=_preprocess,
                payload_override=payload_override,
                idempotency_key=idempotency_key,
            )
        else:
            if not action_type_map:
                raise ValueError("action_type_map is required for outbound dead-letter replay")
            outbound_config = OutboundConnectorConfig(
                connector_id=dead_letter["connector_id"],
                action_type_map=dict(action_type_map),
                retry=RetryPolicy.from_config(retry),
            )

            def _transport(payload: Dict[str, Any], attempt: int) -> Dict[str, Any]:
                if fail_permanently:
                    raise PermanentConnectorError("simulated permanent outbound error")
                if attempt <= fail_until_attempt:
                    raise TransientConnectorError("simulated transient outbound error")
                return {"ack": "delivered", "attempt": attempt, "external_action_type": payload["external_action_type"]}

            replay_transport = None if transport_plugin else _transport
            replay_result = self.connector_runtime.replay_dead_letter(
                dead_letter_id=dead_letter_id,
                outbound_config=outbound_config,
                transport=replay_transport,
                payload_override=payload_override,
                idempotency_key=idempotency_key,
                transport_plugin=transport_plugin,
            )

        self._emit(
            session_id,
            "connector.dead_letter.replay.%s" % replay_result["replay_status"],
            {"dead_letter_id": dead_letter_id, "replay_status": replay_result["replay_status"]},
        )
        return replay_result

    def _resolve_world_game_scenario_path(
        self,
        scenario_id: Optional[str],
        scenario_path: Optional[str],
    ) -> Path:
        if scenario_path:
            path = Path(scenario_path)
            if not path.exists():
                raise ValueError("scenario_path not found: %s" % scenario_path)
            return path

        if not scenario_id:
            raise ValueError("scenario_id or scenario_path is required")

        path = self._repo_root / "examples" / "scenarios" / scenario_id / "scenario.json"
        if not path.exists():
            raise ValueError("unknown scenario_id: %s" % scenario_id)
        return path

    def _resolve_repo_relative_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return self._repo_root / path

    def _load_world_game_policies(
        self,
        explicit_policy_pack_path: Optional[str],
        scenario_policy_ref: Optional[str],
    ) -> List[Dict[str, Any]]:
        if explicit_policy_pack_path:
            policy_path = Path(explicit_policy_pack_path)
        elif scenario_policy_ref:
            policy_path = self._repo_root / scenario_policy_ref
        else:
            policy_path = self._repo_root / "adapters" / "world_game" / "policies" / "world_game_policy_pack.json"

        if not policy_path.exists():
            fallback_path = self._repo_root / "adapters" / "world_game" / "policies" / "default_policy.json"
            policy_path = fallback_path

        with policy_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, dict) and isinstance(payload.get("policies"), list):
            return deepcopy(payload["policies"])
        if isinstance(payload, dict) and isinstance(payload.get("rules"), list):
            return [deepcopy(payload)]
        raise ValueError("world game policy file must be a policy or policy pack")

    def _require_world_game_context(self, session_id: str) -> Dict[str, Any]:
        self._require_session(session_id)
        context = self.world_game_context_by_session.get(session_id)
        if context is None:
            raise ValueError("world_game scenario not loaded for session")
        return context

    def _require_world_game_branch(self, session_id: str, branch_id: str) -> Dict[str, Any]:
        context = self._require_world_game_context(session_id)
        branch = context["branches"].get(branch_id)
        if branch is None:
            raise ValueError("unknown world_game branch_id: %s" % branch_id)
        return branch

    def _world_game_branch_summary(self, branch: Dict[str, Any]) -> Dict[str, Any]:
        equity = branch.get("latest_equity_report", {})
        return {
            "branch_id": branch["branch_id"],
            "parent_branch_id": branch.get("parent_branch_id"),
            "turn": branch.get("turn", 0),
            "composite_score": float(branch.get("scorecard", {}).get("composite_score", 0.0)),
            "equity_trend_vs_baseline": float(equity.get("equity_trend_vs_baseline", 0.0)),
            "disparity_spread": float(equity.get("disparity_index", {}).get("spread", 0.0)),
            "event_count": len(branch.get("event_log", [])),
        }

    def _execute_task(self, task: Task) -> Dict[str, Any]:
        method = task.method
        params = task.params

        if method == "reasoning.query":
            answer = self.reasoning_adapter.answer_query(
                projection_name=params["projection_name"],
                query=params["query"],
            )
            return answer.as_dict()

        if method == "proposal.generate":
            proposal = self.reasoning_adapter.generate_proposal(
                projection_name=params["projection_name"],
                instruction=params["instruction"],
                proposer=params.get("proposer"),
            )
            return proposal

        if method == "simulation.run":
            simulation_id = params["simulation_id"]
            if simulation_id not in self.simulation_engine.branches:
                self.simulation_engine.create_branch(
                    simulation_id=simulation_id,
                    projection_name=params["projection_name"],
                    scenario_name=params.get("scenario_name"),
                    assumptions=params.get("assumptions"),
                    inputs=params.get("inputs"),
                )

            for event in params.get("hypothetical_events", []):
                self.simulation_engine.apply_hypothetical_event(simulation_id, event)

            result = self.simulation_engine.run(simulation_id)
            return result.as_dict()

        if method == "proposal.submit":
            proposal = params["proposal"]
            policies = params.get("policies", [])
            report = self.policy_engine.evaluate_policies(policies, proposal)

            approval_id = None
            if report.requires_approval:
                approval = self.approval_request(
                    session_id=task.session_id,
                    task_id=task.task_id,
                    reason="policy requires approval",
                    payload={"proposal_id": proposal.get("proposal_id")},
                    actor_requirements={
                        "required_capabilities": ["approval.respond", "proposal.approve"],
                        "allow_escalation": True,
                        "allow_override": True,
                    },
                )
                approval_id = approval["approval_id"]
                task.status = "blocked"
                self._emit(task.session_id, "task.blocked", {"task_id": task.task_id, "approval_id": approval_id})

            return {
                "proposal_id": proposal.get("proposal_id"),
                "policy_report": report.as_dict(),
                "approval_id": approval_id,
            }

        if method == "eval.run":
            eval_id = params["eval_id"]
            return self.eval_run(task.session_id, eval_id)

        if method == "connector.inbound.run":
            return self.connector_inbound_run(
                session_id=task.session_id,
                connector_id=params["connector_id"],
                event_type_map=params["event_type_map"],
                external_event=params["external_event"],
                idempotency_key=params.get("idempotency_key"),
                retry=params.get("retry"),
                fail_until_attempt=int(params.get("fail_until_attempt", 0)),
                policies=params.get("policies"),
                approval_id=params.get("approval_id"),
            )

        if method == "connector.outbound.run":
            return self.connector_outbound_run(
                session_id=task.session_id,
                connector_id=params["connector_id"],
                action_type_map=params["action_type_map"],
                action=params["action"],
                idempotency_key=params.get("idempotency_key"),
                retry=params.get("retry"),
                fail_until_attempt=int(params.get("fail_until_attempt", 0)),
                fail_permanently=bool(params.get("fail_permanently", False)),
                transport_plugin=params.get("transport_plugin"),
                policies=params.get("policies"),
                approval_id=params.get("approval_id"),
            )

        if method == "connector.dead_letter.list":
            return self.connector_dead_letter_list(
                session_id=task.session_id,
                connector_id=params.get("connector_id"),
                direction=params.get("direction"),
            )

        if method == "connector.dead_letter.replay":
            return self.connector_dead_letter_replay(
                session_id=task.session_id,
                dead_letter_id=params["dead_letter_id"],
                event_type_map=params.get("event_type_map"),
                action_type_map=params.get("action_type_map"),
                retry=params.get("retry"),
                idempotency_key=params.get("idempotency_key"),
                payload_override=params.get("payload_override"),
                fail_until_attempt=int(params.get("fail_until_attempt", 0)),
                fail_permanently=bool(params.get("fail_permanently", False)),
                transport_plugin=params.get("transport_plugin"),
            )

        if method == "connector.policy_decision.list":
            return self.connector_policy_decision_list(
                session_id=task.session_id,
                connector_id=params.get("connector_id"),
                direction=params.get("direction"),
            )

        if method == "connector.policy_decision.get":
            return self.connector_policy_decision_get(
                session_id=task.session_id,
                decision_id=params["decision_id"],
            )

        if method == "world_game.scenario.list":
            return self.world_game_scenario_list(examples_root=params.get("examples_root"))

        if method == "world_game.session.create":
            return self.world_game_session_create(
                session_id=task.session_id,
                label=params.get("label"),
                description=params.get("description"),
                actor_id=params.get("actor_id"),
                actor_type=params.get("actor_type", "human"),
                roles=params.get("roles"),
                capabilities=params.get("capabilities"),
                display_name=params.get("display_name"),
            )

        if method == "world_game.session.get":
            return self.world_game_session_get(session_id=task.session_id)

        if method == "world_game.session.actor.add":
            return self.world_game_session_actor_add(
                session_id=task.session_id,
                actor_id=params["actor_id"],
                actor_type=params.get("actor_type", "human"),
                roles=params.get("roles"),
                capabilities=params.get("capabilities"),
                display_name=params.get("display_name"),
                requested_by_actor_id=params.get("requested_by_actor_id"),
            )

        if method == "world_game.session.actor.remove":
            return self.world_game_session_actor_remove(
                session_id=task.session_id,
                actor_id=params["actor_id"],
                requested_by_actor_id=params.get("requested_by_actor_id"),
            )

        if method == "world_game.session.actor.list":
            return self.world_game_session_actor_list(session_id=task.session_id)

        if method == "world_game.session.stage.get":
            return self.world_game_session_stage_get(session_id=task.session_id)

        if method == "world_game.session.stage.set":
            return self.world_game_session_stage_set(
                session_id=task.session_id,
                stage=params["stage"],
                actor_id=params.get("actor_id"),
                reason=params.get("reason"),
            )

        if method == "world_game.session.stage.advance":
            return self.world_game_session_stage_advance(
                session_id=task.session_id,
                actor_id=params.get("actor_id"),
                reason=params.get("reason"),
            )

        if method == "world_game.session.export":
            return self.world_game_session_export(
                session_id=task.session_id,
                output_path=params.get("output_path"),
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.session.import":
            return self.world_game_session_import(
                session_id=task.session_id,
                bundle=params.get("bundle"),
                bundle_path=params.get("bundle_path"),
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.scenario.load":
            return self.world_game_scenario_load(
                session_id=task.session_id,
                scenario_id=params.get("scenario_id"),
                scenario_path=params.get("scenario_path"),
                branch_id=params.get("branch_id", "baseline"),
                policy_pack_path=params.get("policy_pack_path"),
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.turn.run":
            return self.world_game_turn_run(
                session_id=task.session_id,
                branch_id=params.get("branch_id", "baseline"),
                intervention_ids=params.get("intervention_ids", []),
                shock_ids=params.get("shock_ids", []),
                approval_status=params.get("approval_status", "approved"),
                actor_id=params.get("actor_id"),
                proposal_id=params.get("proposal_id"),
            )

        if method == "world_game.branch.create":
            return self.world_game_branch_create(
                session_id=task.session_id,
                source_branch_id=params["source_branch_id"],
                branch_id=params["branch_id"],
                actor_id=params.get("actor_id"),
                proposal_id=params.get("proposal_id"),
            )

        if method == "world_game.branch.compare":
            return self.world_game_branch_compare(
                session_id=task.session_id,
                branch_ids=params.get("branch_ids"),
                include_annotation_summary=bool(params.get("include_annotation_summary", False)),
            )

        if method == "world_game.replay.run":
            return self.world_game_replay_run(
                session_id=task.session_id,
                branch_id=params.get("branch_id", "baseline"),
            )

        if method == "world_game.network.inspect":
            return self.world_game_network_inspect(
                session_id=task.session_id,
                branch_id=params.get("branch_id", "baseline"),
            )

        if method == "world_game.equity.report":
            return self.world_game_equity_report(
                session_id=task.session_id,
                branch_id=params.get("branch_id", "baseline"),
                branch_ids=params.get("branch_ids"),
            )

        if method == "world_game.proposal.create":
            return self.world_game_proposal_create(
                session_id=task.session_id,
                proposal_id=params.get("proposal_id"),
                title=params.get("title", ""),
                rationale=params.get("rationale", ""),
                assumptions=params.get("assumptions"),
                intended_interventions=params.get("intended_interventions"),
                expected_outcomes=params.get("expected_outcomes"),
                evidence_refs=params.get("evidence_refs"),
                planned_turn_sequence=params.get("planned_turn_sequence"),
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.proposal.update":
            return self.world_game_proposal_update(
                session_id=task.session_id,
                proposal_id=params["proposal_id"],
                updates=params.get("updates"),
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.proposal.get":
            return self.world_game_proposal_get(
                session_id=task.session_id,
                proposal_id=params["proposal_id"],
            )

        if method == "world_game.proposal.list":
            return self.world_game_proposal_list(
                session_id=task.session_id,
                status=params.get("status"),
            )

        if method == "world_game.proposal.submit":
            return self.world_game_proposal_submit(
                session_id=task.session_id,
                proposal_id=params["proposal_id"],
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.proposal.adopt":
            return self.world_game_proposal_adopt(
                session_id=task.session_id,
                proposal_id=params["proposal_id"],
                branch_id=params.get("branch_id"),
                source_branch_id=params.get("source_branch_id", "baseline"),
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.proposal.reject":
            return self.world_game_proposal_reject(
                session_id=task.session_id,
                proposal_id=params["proposal_id"],
                actor_id=params.get("actor_id"),
                reason=params.get("reason"),
            )

        if method == "world_game.annotation.create":
            return self.world_game_annotation_create(
                session_id=task.session_id,
                annotation_id=params.get("annotation_id"),
                annotation_type=params["annotation_type"],
                target_type=params["target_type"],
                target_id=params["target_id"],
                body=params.get("body", ""),
                evidence_refs=params.get("evidence_refs"),
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.annotation.list":
            return self.world_game_annotation_list(
                session_id=task.session_id,
                target_type=params.get("target_type"),
                target_id=params.get("target_id"),
                include_archived=bool(params.get("include_archived", False)),
            )

        if method == "world_game.annotation.update":
            return self.world_game_annotation_update(
                session_id=task.session_id,
                annotation_id=params["annotation_id"],
                body=params.get("body"),
                evidence_refs=params.get("evidence_refs"),
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.annotation.archive":
            return self.world_game_annotation_archive(
                session_id=task.session_id,
                annotation_id=params["annotation_id"],
                actor_id=params.get("actor_id"),
            )

        if method == "world_game.provenance.inspect":
            return self.world_game_provenance_inspect(
                session_id=task.session_id,
                artifact_type=params.get("artifact_type"),
                artifact_id=params.get("artifact_id"),
            )

        if method == "world_game.authoring.template.list":
            return self.world_game_authoring_template_list(
                authoring_root=params.get("authoring_root"),
            )

        if method == "world_game.authoring.draft.create":
            return self.world_game_authoring_draft_create(
                source_bundle_path=params.get("source_bundle_path"),
                source_bundle=params.get("source_bundle"),
                output_path=params.get("output_path"),
                bundle_id=params.get("bundle_id"),
                label=params.get("label"),
                description=params.get("description"),
                content_version=params.get("content_version"),
                deterministic_version_seed=params.get("deterministic_version_seed"),
                tags=params.get("tags"),
                created_at=params.get("created_at"),
                updated_at=params.get("updated_at"),
            )

        if method == "world_game.authoring.draft.validate":
            return self.world_game_authoring_draft_validate(
                draft_path=params.get("draft_path"),
                draft_bundle=params.get("draft_bundle"),
            )

        if method == "world_game.authoring.bundle.publish":
            return self.world_game_authoring_bundle_publish(
                draft_path=params.get("draft_path"),
                draft_bundle=params.get("draft_bundle"),
                output_path=params.get("output_path"),
                published_at=params.get("published_at"),
                updated_at=params.get("updated_at"),
            )

        if method == "world_game.authoring.bundle.instantiate":
            return self.world_game_authoring_bundle_instantiate(
                bundle_path=params.get("bundle_path"),
                bundle=params.get("bundle"),
                template_id=params["template_id"],
                parameter_values=params.get("parameter_values"),
                scenario_output_path=params.get("scenario_output_path"),
            )

        raise ValueError("unsupported task method")

    def _emit(self, session_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        notification = build_notification(method=event_type, params=deepcopy(payload))
        event = {
            "type": event_type,
            "at": _utc_now(),
            "payload": deepcopy(payload),
            "wire_type": notification["wire_type"],
            "protocol_version": notification["protocol_version"],
            "method": notification["method"],
            "params": notification["params"],
        }
        self.events_by_session.setdefault(session_id, []).append(event)
        self.observability.emit(
            component="app_server",
            event_type="session.notification",
            session_id=session_id,
            task_id=payload.get("task_id"),
            attributes={"method": event_type},
        )

    def _create_virtual_task_for_proposal(self, session_id: str, proposal: Dict[str, Any]) -> str:
        task_id = "task.virtual.%s" % uuid4().hex[:12]
        self.tasks[task_id] = Task(
            task_id=task_id,
            session_id=session_id,
            method="proposal.submit",
            params={"proposal_id": proposal.get("proposal_id")},
            created_at=_utc_now(),
            status="blocked",
        )
        return task_id

    def _create_virtual_connector_task(self, session_id: str, payload: Dict[str, Any]) -> str:
        task_id = "task.virtual.%s" % uuid4().hex[:12]
        self.tasks[task_id] = Task(
            task_id=task_id,
            session_id=session_id,
            method="connector.policy.guardrail",
            params=deepcopy(payload),
            created_at=_utc_now(),
            status="blocked",
        )
        return task_id

    def _resolve_connector_idempotency_key(
        self,
        direction: str,
        connector_id: str,
        payload: Dict[str, Any],
        explicit_key: Optional[str],
    ) -> str:
        return self.connector_runtime._resolve_idempotency_key(
            direction=direction,
            connector_id=connector_id,
            payload=payload,
            explicit_key=explicit_key,
        )

    def _build_connector_policy_input(
        self,
        direction: str,
        connector_id: str,
        idempotency_key: str,
        payload: Dict[str, Any],
        mapped_operation_type: Optional[str],
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = {
            "connector_id": connector_id,
            "direction": direction,
            "provider": provider or payload.get("provider"),
            "source": payload.get("source"),
            "trust_classification": payload.get("trust_classification", "unclassified"),
            "idempotency_key": idempotency_key,
            "action_type": mapped_operation_type if direction == "outbound" else None,
            "event_type": mapped_operation_type if direction == "inbound" else None,
        }
        proposal = {
            "proposal_id": "proposal.connector.%s.%s" % (direction, idempotency_key),
            "proposed_action": {
                "action_type": "connector.%s.%s" % (
                    direction,
                    mapped_operation_type or payload.get("action_type") or payload.get("event_type") or "unknown",
                ),
                "parameters": {
                    "connector_id": connector_id,
                    "direction": direction,
                    "provider": context["provider"],
                    "source": context["source"],
                    "trust_classification": context["trust_classification"],
                    "idempotency_key": idempotency_key,
                    "payload": deepcopy(payload),
                },
            },
            "connector_context": context,
        }
        return {"proposal": proposal, "context": context}

    def _resolve_connector_approval(
        self,
        session_id: str,
        connector_id: str,
        direction: str,
        idempotency_key: str,
        approval_id: Optional[str],
    ) -> Dict[str, Any]:
        if not approval_id:
            task_id = self._create_virtual_connector_task(
                session_id,
                {
                    "connector_id": connector_id,
                    "direction": direction,
                    "idempotency_key": idempotency_key,
                },
            )
            return self._create_approval(
                session_id=session_id,
                task_id=task_id,
                reason="connector policy requires approval",
                payload={
                    "connector_id": connector_id,
                    "direction": direction,
                    "idempotency_key": idempotency_key,
                },
                required_capabilities=[
                    "approval.respond",
                    "connector.%s.approve" % direction,
                ],
                allow_escalation=True,
                allow_override=True,
            )

        approval = self._require_approval(approval_id)
        return self._approval_payload(approval)

    def _record_connector_policy_decision(
        self,
        connector_id: str,
        direction: str,
        idempotency_key: str,
        policy_report: Dict[str, Any],
        status: str,
        provider: Optional[str],
        source: Optional[str],
        approval_id: Optional[str] = None,
        approval_chain: Optional[List[Dict[str, Any]]] = None,
        execution_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        decision_id = "decision.connector.%s" % uuid4().hex[:12]
        report_payload = deepcopy(policy_report)
        if approval_chain:
            report_payload["approval_chain"] = deepcopy(approval_chain)
        report_payload["provenance"] = self._build_connector_provenance(
            decision_id=decision_id,
            connector_id=connector_id,
            direction=direction,
            idempotency_key=idempotency_key,
            policy_report=policy_report,
            approval_id=approval_id,
            approval_chain=approval_chain,
            status=status,
            execution_result=execution_result,
        )
        return self.connector_runtime.record_policy_decision(
            decision_id=decision_id,
            connector_id=connector_id,
            direction=direction,
            idempotency_key=idempotency_key,
            final_outcome=policy_report.get("final_outcome", "allow"),
            status=status,
            provider=provider,
            source=source,
            approval_id=approval_id,
            policy_report=report_payload,
            execution_result=execution_result,
        )

    def _collect_decisions(self, decision_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if decision_id:
            decision = self.decisions.get(decision_id)
            if decision is None:
                return []
            return [deepcopy(decision)]
        return [deepcopy(item) for item in self.decisions.values()]

    def _trace_matches_session(self, trace: Dict[str, Any], session_id: str) -> bool:
        context = trace.get("context") or {}
        if context.get("session_id") == session_id:
            return True
        for event in trace.get("events", []):
            attributes = event.get("attributes") or {}
            if attributes.get("session_id") == session_id:
                return True
        return False

    def _build_decision_provenance(
        self,
        session_id: str,
        decision_id: str,
        proposal: Dict[str, Any],
        policy_report: Dict[str, Any],
        approval_id: Optional[str],
        approval_chain: List[Dict[str, Any]],
        outcome: str,
    ) -> Dict[str, Any]:
        proposal_id = str(proposal.get("proposal_id", "unknown_proposal"))
        stages: List[Dict[str, Any]] = [
            {
                "stage": "proposal",
                "status": "completed",
                "ref_id": proposal_id,
                "at": proposal.get("created_at") or _utc_now(),
            },
            {
                "stage": "policy_evaluation",
                "status": "completed",
                "ref_id": "policy.%s" % proposal_id,
                "at": _utc_now(),
                "attributes": {"final_outcome": policy_report.get("final_outcome", "allow")},
            },
        ]
        if approval_id:
            stages.append(
                {
                    "stage": "approval",
                    "status": "completed" if approval_chain else "pending",
                    "ref_id": approval_id,
                    "at": (approval_chain[-1].get("at") if approval_chain else _utc_now()),
                }
            )
        stages.append(
            {
                "stage": "execution_outcome",
                "status": "completed",
                "ref_id": decision_id,
                "at": _utc_now(),
                "attributes": {"outcome": outcome},
            }
        )

        evidence: List[Dict[str, Any]] = []
        for item in proposal.get("supporting_evidence", []):
            evidence.append(
                normalize_evidence_ref(
                    evidence_type=item.get("evidence_type", "evidence"),
                    ref_id=item.get("ref_id", "unknown_ref"),
                    summary=item.get("summary", "proposal supporting evidence"),
                    stage="proposal",
                )
            )
        for evaluation in policy_report.get("evaluations", []):
            if evaluation.get("evidence") is None:
                continue
            evidence.append(
                normalize_evidence_ref(
                    evidence_type="policy_rule",
                    ref_id=evaluation.get("rule_id", "unknown_rule"),
                    summary="Policy rule outcome=%s." % evaluation.get("outcome", "unknown"),
                    stage="policy_evaluation",
                    attributes={"evidence": deepcopy(evaluation.get("evidence", {}))},
                )
            )
        for item in approval_chain:
            actor = item.get("actor", {})
            evidence.append(
                normalize_evidence_ref(
                    evidence_type="approval_action",
                    ref_id=item.get("sequence", "approval_step"),
                    summary="Approval action %s by %s."
                    % (item.get("action", "unknown"), actor.get("actor_id", "unknown.actor")),
                    stage="approval",
                    attributes={"actor": deepcopy(actor)},
                )
            )

        return {
            "trace": {
                "session_id": session_id,
                "decision_id": decision_id,
                "proposal_id": proposal_id,
                "approval_id": approval_id,
                "simulation_refs": deepcopy(proposal.get("simulation_refs", [])),
                "correlation_id": proposal.get("correlation_id"),
            },
            "stages": stages,
            "evidence": evidence,
            "evidence_summary": [item["summary"] for item in evidence],
        }

    def _build_connector_provenance(
        self,
        decision_id: str,
        connector_id: str,
        direction: str,
        idempotency_key: str,
        policy_report: Dict[str, Any],
        approval_id: Optional[str],
        approval_chain: Optional[List[Dict[str, Any]]],
        status: str,
        execution_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        stages: List[Dict[str, Any]] = [
            {
                "stage": "proposal",
                "status": "completed",
                "ref_id": "proposal.connector.%s.%s" % (direction, idempotency_key),
                "at": _utc_now(),
            },
            {
                "stage": "policy_evaluation",
                "status": "completed",
                "ref_id": "policy.connector.%s" % decision_id,
                "at": _utc_now(),
                "attributes": {"final_outcome": policy_report.get("final_outcome", "allow")},
            },
        ]
        if approval_id:
            stages.append(
                {
                    "stage": "approval",
                    "status": "completed" if approval_chain else "pending",
                    "ref_id": approval_id,
                    "at": (approval_chain[-1].get("at") if approval_chain else _utc_now()),
                }
            )
        stages.append(
            {
                "stage": "execution_outcome",
                "status": "completed",
                "ref_id": decision_id,
                "at": _utc_now(),
                "attributes": {"status": status},
            }
        )
        evidence: List[Dict[str, Any]] = []
        for evaluation in policy_report.get("evaluations", []):
            evidence.append(
                normalize_evidence_ref(
                    evidence_type="policy_rule",
                    ref_id=evaluation.get("rule_id", "unknown_rule"),
                    summary="Connector policy %s -> %s."
                    % (
                        evaluation.get("rule_name", evaluation.get("rule_id", "rule")),
                        evaluation.get("outcome", "unknown"),
                    ),
                    stage="policy_evaluation",
                    attributes={"evidence": deepcopy(evaluation.get("evidence", {}))},
                )
            )
        if execution_result is not None:
            evidence.append(
                normalize_evidence_ref(
                    evidence_type="connector_execution",
                    ref_id=execution_result.get("idempotency_key", idempotency_key),
                    summary="Connector execution status %s." % execution_result.get("status", status),
                    stage="execution_outcome",
                )
            )
        return {
            "trace": {
                "decision_id": decision_id,
                "connector_id": connector_id,
                "direction": direction,
                "idempotency_key": idempotency_key,
                "approval_id": approval_id,
            },
            "stages": stages,
            "evidence": evidence,
            "evidence_summary": [item["summary"] for item in evidence],
        }

    def _build_provenance_diagnostics(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        major_decisions: List[Dict[str, Any]] = []
        for decision in artifacts.get("decisions", []):
            stage_names = [
                stage.get("stage")
                for stage in decision.get("provenance", {}).get("stages", [])
                if stage.get("stage")
            ]
            required = ["proposal", "policy_evaluation", "execution_outcome"]
            if decision.get("approval_status") not in {None, "not_required"}:
                required.append("approval")
            missing = [name for name in required if name not in stage_names]
            major_decisions.append(
                {
                    "decision_id": decision.get("decision_id"),
                    "status": decision.get("status"),
                    "stage_count": len(stage_names),
                    "missing_stages": missing,
                    "end_to_end_traceable": not missing,
                }
            )

        connector_decisions: List[Dict[str, Any]] = []
        for decision in artifacts.get("connector_policy_decisions", []):
            provenance = decision.get("policy_report", {}).get("provenance", {})
            stage_names = [
                stage.get("stage") for stage in provenance.get("stages", []) if stage.get("stage")
            ]
            required = ["proposal", "policy_evaluation", "execution_outcome"]
            if decision.get("approval_id"):
                required.append("approval")
            missing = [name for name in required if name not in stage_names]
            connector_decisions.append(
                {
                    "decision_id": decision.get("decision_id"),
                    "status": decision.get("status"),
                    "stage_count": len(stage_names),
                    "missing_stages": missing,
                    "end_to_end_traceable": not missing,
                }
            )

        return {
            "major_decisions": major_decisions,
            "connector_decisions": connector_decisions,
        }

    def _create_approval(
        self,
        session_id: str,
        task_id: str,
        reason: str,
        payload: Optional[Dict[str, Any]] = None,
        required_roles: Optional[List[str]] = None,
        required_capabilities: Optional[List[str]] = None,
        allow_escalation: bool = True,
        allow_override: bool = False,
    ) -> Dict[str, Any]:
        approval_id = "approval.%s" % uuid4().hex[:12]
        capabilities = list(required_capabilities or ["approval.respond"])
        approval = ApprovalRequest(
            approval_id=approval_id,
            session_id=session_id,
            task_id=task_id,
            status="pending",
            requested_at=_utc_now(),
            reason=reason,
            payload=deepcopy(payload or {}),
            required_roles=list(required_roles or []),
            required_capabilities=capabilities,
            allow_escalation=allow_escalation,
            allow_override=allow_override,
        )
        self.approvals[approval_id] = approval
        self._append_approval_event(approval, "approval.requested")

        self._emit(
            session_id,
            "approval.required",
            {
                "approval_id": approval_id,
                "task_id": task_id,
                "reason": reason,
            },
        )

        return {
            "approval_id": approval_id,
            "status": approval.status,
            "task_id": task_id,
            "reason": reason,
            "required_roles": deepcopy(approval.required_roles),
            "required_capabilities": deepcopy(approval.required_capabilities),
            "allow_escalation": approval.allow_escalation,
            "allow_override": approval.allow_override,
            "approval_chain": [],
        }

    def _require_session(self, session_id: str) -> Session:
        session = self.sessions.get(session_id)
        if session is None:
            raise ValueError("session_id not found")
        return session

    def _require_task(self, task_id: str) -> Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise ValueError("task_id not found")
        return task

    def _require_approval(self, approval_id: str) -> ApprovalRequest:
        approval = self.approvals.get(approval_id)
        if approval is None:
            raise ValueError("approval_id not found")
        return approval

    def _normalize_actor(self, actor: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        payload = actor or {}
        actor_id = str(payload.get("actor_id", "")).strip() or "unknown.actor"
        actor_type = str(payload.get("actor_type", "unknown")).strip() or "unknown"
        roles = [str(item).strip() for item in list(payload.get("roles", [])) if str(item).strip()]
        capabilities = [str(item).strip() for item in list(payload.get("capabilities", [])) if str(item).strip()]
        actor_ref = {
            "actor_id": actor_id,
            "actor_type": actor_type,
            "roles": roles,
            "capabilities": capabilities,
        }
        if payload.get("display_name"):
            actor_ref["display_name"] = str(payload["display_name"])
        return actor_ref

    def _authorize_approval_actor(
        self,
        approval: ApprovalRequest,
        actor: Dict[str, Any],
        decision: str,
    ) -> None:
        if decision == "overridden" and not approval.allow_override:
            raise PermissionError("override is not allowed for this approval")
        if decision == "escalated" and not approval.allow_escalation:
            raise PermissionError("escalation is not allowed for this approval")

        required_roles = list(approval.required_roles)
        required_capabilities = list(approval.required_capabilities)
        if decision == "escalated":
            required_capabilities.append("approval.escalate")
        if decision == "overridden":
            required_capabilities.append("approval.override")

        actor_roles = set(actor.get("roles", []))
        actor_capabilities = set(actor.get("capabilities", []))
        wildcard = "*" in actor_capabilities

        if required_roles and not actor_roles.intersection(required_roles):
            raise PermissionError("actor lacks required approval role")
        if required_capabilities and not (
            wildcard or set(required_capabilities).issubset(actor_capabilities)
        ):
            raise PermissionError("actor lacks required approval capability")

    def _append_approval_event(
        self,
        approval: ApprovalRequest,
        event_type: str,
        entry: Optional[Dict[str, Any]] = None,
    ) -> None:
        stream_id = "approval.%s" % approval.approval_id
        event_payload = self._approval_payload(approval)
        if entry is not None:
            event_payload["entry"] = deepcopy(entry)
        self.replay_engine.event_store.append(
            stream_id,
            {
                "event_type": event_type,
                "occurred_at": _utc_now(),
                "recorded_at": _utc_now(),
                "payload": event_payload,
            },
        )

    def _rehydrate_approvals(self) -> None:
        events = self.replay_engine.event_store.read_all()
        reconstructed: Dict[str, ApprovalRequest] = {}
        for event in events:
            event_type = event.get("event_type")
            if event_type not in {"approval.requested", "approval.recorded"}:
                continue
            payload = event.get("payload", {})
            approval_id = payload.get("approval_id")
            if not approval_id:
                continue
            existing = reconstructed.get(approval_id)
            if existing is None:
                reconstructed[approval_id] = ApprovalRequest(
                    approval_id=approval_id,
                    session_id=payload.get("session_id", ""),
                    task_id=payload.get("task_id", ""),
                    status=payload.get("status", "pending"),
                    requested_at=payload.get("requested_at", _utc_now()),
                    reason=payload.get("reason", ""),
                    payload=deepcopy(payload.get("payload", {})),
                    decided_at=payload.get("decided_at"),
                    comment=payload.get("comment"),
                    required_roles=list(payload.get("required_roles", [])),
                    required_capabilities=list(payload.get("required_capabilities", [])),
                    allow_escalation=bool(payload.get("allow_escalation", True)),
                    allow_override=bool(payload.get("allow_override", False)),
                    chain=deepcopy(payload.get("approval_chain", [])),
                )
                continue

            existing.status = payload.get("status", existing.status)
            existing.decided_at = payload.get("decided_at", existing.decided_at)
            existing.comment = payload.get("comment", existing.comment)
            existing.chain = deepcopy(payload.get("approval_chain", existing.chain))

        self.approvals.update(reconstructed)

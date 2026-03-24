from copy import deepcopy
from typing import Any, Dict, List, Optional

from adapters.supply_ops.ingress import SupplyOpsIngressPreparer
from adapters.supply_ops.replay import build_recovery_hypothetical_events


class SupplyOpsExecutionEvidenceBuilder:
    def build(
        self,
        ingress_envelope: Dict[str, Any],
        proposal: Dict[str, Any],
        policy_report: Any,
        decision: Dict[str, Any],
        *,
        hypothetical_events: Optional[List[Dict[str, Any]]] = None,
        target_surface: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ingress = SupplyOpsIngressPreparer().extract_metadata(ingress_envelope)
        policy = self._normalize_policy_report(policy_report)
        decision_id = self._require_string(decision, "decision_id")
        proposal_id = self._require_string(proposal, "proposal_id")
        selected_proposal_id = self._require_string(decision, "selected_proposal_id")

        if selected_proposal_id != proposal_id:
            raise ValueError(
                "decision.selected_proposal_id must match proposal.proposal_id"
            )

        if self._require_string(decision, "status") != "approved":
            raise ValueError("decision.status must be approved")

        approval_status = decision.get("approval_status")
        if approval_status not in (None, "approved"):
            raise ValueError("decision.approval_status must be approved when present")

        if policy.get("denied") is True:
            raise ValueError("policy_report.denied must be false")

        action = self._require_mapping(proposal, "proposed_action")
        parameters = self._require_mapping(action, "parameters")
        if self._require_bool(parameters, "simulation_completed") is not True:
            raise ValueError(
                "proposal.proposed_action.parameters.simulation_completed must be true"
            )

        approval_chain = self._require_list(decision, "approval_chain")
        approvals = self._require_list(decision, "approvals")
        approved_at = decision.get("approved_at")
        if approved_at is None and approval_chain:
            approved_at = approval_chain[-1].get("at")

        replay_safe_events = (
            deepcopy(hypothetical_events)
            if hypothetical_events is not None
            else build_recovery_hypothetical_events(proposal)
        )

        execution_target = (
            deepcopy(target_surface)
            if target_surface is not None
            else self._default_target_surface(decision_id)
        )

        policy_outcomes = [item.get("outcome", "unknown") for item in policy["evaluations"]]
        suffix = decision_id.rsplit(".", 1)[-1]

        return {
            "evidence_id": "exec-evidence.supply-ops.%s" % suffix,
            "adapter_id": "adapter-supply-ops",
            "decision_id": decision_id,
            "selected_proposal_id": proposal_id,
            "status": "prepared",
            "ingress": ingress,
            "policy": {
                "final_outcome": policy["final_outcome"],
                "requires_approval": policy["requires_approval"],
                "denied": policy["denied"],
                "evaluations": deepcopy(policy["evaluations"]),
            },
            "approval": {
                "approval_status": approval_status or "not_required",
                "approval_id": decision.get("approval_id"),
                "approved_at": approved_at,
                "approvals": deepcopy(approvals),
                "approval_chain": deepcopy(approval_chain),
            },
            "simulation": {
                "simulation_id": self._require_string(parameters, "simulation_id"),
                "simulation_completed": True,
            },
            "execution_plan": {
                "submission_mode": "approved_connector_handoff_preparation",
                "target_surface": execution_target,
                "action": deepcopy(action),
                "replay_safe_hypothetical_events": replay_safe_events,
            },
            "evidence_summary": [
                "Inbound connector-shaped envelope stays translation-only before action.",
                "Policy outcomes remain visible before execution preparation: %s."
                % ", ".join(policy_outcomes),
                "Approval status is %s for %s."
                % ((approval_status or "not_required"), decision_id),
                "Execution handoff remains replay-safe through hypothetical recovery events.",
            ],
        }

    def _default_target_surface(self, decision_id: str) -> Dict[str, Any]:
        connector_id = "connector.supply-ops.fulfillment-execution"
        return {
            "surface_method": "connector.outbound.run",
            "connector_id": connector_id,
            "direction": "outbound",
            "provider": "fixture.fulfillment-control",
            "source": "supply_ops_control_plane",
            "idempotency_key": "outbound:%s:%s" % (connector_id, decision_id),
        }

    def _normalize_policy_report(self, policy_report: Any) -> Dict[str, Any]:
        if hasattr(policy_report, "as_dict"):
            data = policy_report.as_dict()
        elif isinstance(policy_report, dict):
            data = deepcopy(policy_report)
        else:
            raise ValueError("policy_report must be a mapping or expose as_dict()")

        if not isinstance(data.get("evaluations"), list):
            raise ValueError("policy_report.evaluations must be a list")
        return {
            "final_outcome": self._require_string(data, "final_outcome"),
            "requires_approval": self._require_bool(data, "requires_approval"),
            "denied": self._require_bool(data, "denied"),
            "evaluations": deepcopy(data["evaluations"]),
        }

    def _require_mapping(self, data: Dict[str, Any], field: str) -> Dict[str, Any]:
        value = data.get(field)
        if not isinstance(value, dict):
            raise ValueError("%s must be an object" % field)
        return value

    def _require_list(self, data: Dict[str, Any], field: str) -> List[Any]:
        value = data.get(field)
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("%s must be a list" % field)
        return value

    def _require_string(self, data: Dict[str, Any], field: str) -> str:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("%s must be a non-empty string" % field)
        return value

    def _require_bool(self, data: Dict[str, Any], field: str) -> bool:
        value = data.get(field)
        if not isinstance(value, bool):
            raise ValueError("%s must be a boolean" % field)
        return value

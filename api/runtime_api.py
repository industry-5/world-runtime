from copy import deepcopy
from typing import Any, Dict, List, Optional

from core.app_server import WorldRuntimeAppServer

API_VERSION = "v1"

PUBLIC_ENDPOINTS = {
    "runtime_call": "/v1/runtime/call",
    "session_create": "/v1/sessions",
    "proposal_submit": "/v1/proposals/submit",
    "simulation_run": "/v1/simulations/run",
    "approval_respond": "/v1/approvals/respond",
    "connector_inbound_run": "/v1/connectors/inbound/run",
    "connector_outbound_run": "/v1/connectors/outbound/run",
    "telemetry_summary": "/v1/observability/telemetry/summary",
}


class PublicRuntimeAPI:
    """Versioned public facade over App Server methods."""

    def __init__(self, app_server: WorldRuntimeAppServer, api_version: str = API_VERSION) -> None:
        self.app_server = app_server
        self.api_version = api_version

    def metadata(self) -> Dict[str, Any]:
        protocol = self.app_server.protocol_inspect()
        return {
            "api_version": self.api_version,
            "protocol_version": protocol["protocol_version"],
            "compatibility_policy": protocol["compatibility_policy"],
        }

    def call_runtime(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.app_server.handle_request(method, params)

    def create_session(self) -> Dict[str, Any]:
        return self._unwrap(self.app_server.handle_request("session.create"))

    def submit_proposal(
        self,
        session_id: str,
        proposal: Dict[str, Any],
        policies: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        return self._unwrap(
            self.app_server.handle_request(
                "proposal.submit",
                {
                    "session_id": session_id,
                    "proposal": deepcopy(proposal),
                    "policies": deepcopy(policies or []),
                },
            )
        )

    def run_simulation(
        self,
        session_id: str,
        simulation_id: str,
        projection_name: str,
        hypothetical_events: Optional[List[Dict[str, Any]]] = None,
        scenario_name: Optional[str] = None,
        assumptions: Optional[List[str]] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = self._unwrap(
            self.app_server.handle_request(
                "task.submit",
                {
                    "session_id": session_id,
                    "method": "simulation.run",
                    "params": {
                        "simulation_id": simulation_id,
                        "projection_name": projection_name,
                        "hypothetical_events": deepcopy(hypothetical_events or []),
                        "scenario_name": scenario_name,
                        "assumptions": deepcopy(assumptions or []),
                        "inputs": deepcopy(inputs or {}),
                    },
                },
            )
        )
        return deepcopy(response["result"])

    def respond_approval(
        self,
        approval_id: str,
        decision: str,
        actor: Dict[str, Any],
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self._unwrap(
            self.app_server.handle_request(
                "approval.respond",
                {
                    "approval_id": approval_id,
                    "decision": decision,
                    "comment": comment,
                    "actor": deepcopy(actor),
                },
            )
        )

    def run_connector_inbound(
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
        return self._unwrap(
            self.app_server.handle_request(
                "connector.inbound.run",
                {
                    "session_id": session_id,
                    "connector_id": connector_id,
                    "event_type_map": deepcopy(event_type_map),
                    "external_event": deepcopy(external_event),
                    "idempotency_key": idempotency_key,
                    "retry": deepcopy(retry),
                    "fail_until_attempt": fail_until_attempt,
                    "policies": deepcopy(policies),
                    "approval_id": approval_id,
                },
            )
        )

    def run_connector_outbound(
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
        return self._unwrap(
            self.app_server.handle_request(
                "connector.outbound.run",
                {
                    "session_id": session_id,
                    "connector_id": connector_id,
                    "action_type_map": deepcopy(action_type_map),
                    "action": deepcopy(action),
                    "idempotency_key": idempotency_key,
                    "retry": deepcopy(retry),
                    "fail_until_attempt": fail_until_attempt,
                    "fail_permanently": fail_permanently,
                    "transport_plugin": deepcopy(transport_plugin),
                    "policies": deepcopy(policies),
                    "approval_id": approval_id,
                },
            )
        )

    def telemetry_summary(self) -> Dict[str, Any]:
        return self._unwrap(self.app_server.handle_request("telemetry.summary"))

    def _unwrap(self, response: Dict[str, Any]) -> Dict[str, Any]:
        if response.get("ok"):
            return deepcopy(response["result"])
        raise ValueError(response.get("error", "unknown error"))

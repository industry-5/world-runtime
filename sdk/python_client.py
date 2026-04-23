import json
from typing import Any, Dict, Optional
from urllib import error, request

DEFAULT_API_VERSION = "v1"


class RuntimeSDKError(RuntimeError):
    pass


class WorldRuntimeSDKClient:
    def __init__(
        self,
        base_url: str,
        api_token: Optional[str] = None,
        timeout_seconds: float = 10.0,
        api_version: str = DEFAULT_API_VERSION,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout_seconds = timeout_seconds
        self.api_version = api_version

    def create_session(self) -> Dict[str, Any]:
        return self._post("/v1/sessions")

    def runtime_inventory(self) -> Dict[str, Any]:
        return self._get("/v1/runtime/inventory")

    def list_runtime_services(self) -> Dict[str, Any]:
        return self._get("/v1/runtime/services")

    def get_runtime_service(self, service_id: str) -> Dict[str, Any]:
        return self._get("/v1/runtime/services/%s" % service_id)

    def reconcile_runtime_services(
        self,
        *,
        actor: Dict[str, Any],
        service_ids: Optional[list[str]] = None,
        session_id: Optional[str] = None,
        prune: bool = False,
    ) -> Dict[str, Any]:
        return self._post(
            "/v1/runtime/services/reconcile",
            {
                "actor": actor,
                "service_ids": service_ids,
                "session_id": session_id,
                "prune": prune,
            },
        )

    def list_runtime_providers(self) -> Dict[str, Any]:
        return self._get("/v1/runtime/providers")

    def get_runtime_provider(self, provider_id: str) -> Dict[str, Any]:
        return self._get("/v1/runtime/providers/%s" % provider_id)

    def resolve_runtime_task(
        self,
        *,
        task_profile_id: str,
        policy_input: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self._post(
            "/v1/runtime/tasks/resolve",
            {
                "task_profile_id": task_profile_id,
                "policy_input": policy_input or {},
            },
        )

    def submit_proposal(
        self,
        session_id: str,
        proposal: Dict[str, Any],
        policies: Optional[list[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        return self._post(
            "/v1/proposals/submit",
            {
                "session_id": session_id,
                "proposal": proposal,
                "policies": policies or [],
            },
        )

    def run_simulation(
        self,
        session_id: str,
        simulation_id: str,
        projection_name: str,
        hypothetical_events: Optional[list[Dict[str, Any]]] = None,
        scenario_name: Optional[str] = None,
        assumptions: Optional[list[str]] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self._post(
            "/v1/simulations/run",
            {
                "session_id": session_id,
                "simulation_id": simulation_id,
                "projection_name": projection_name,
                "hypothetical_events": hypothetical_events or [],
                "scenario_name": scenario_name,
                "assumptions": assumptions or [],
                "inputs": inputs or {},
            },
        )

    def respond_approval(
        self,
        approval_id: str,
        decision: str,
        actor: Dict[str, Any],
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self._post(
            "/v1/approvals/respond",
            {
                "approval_id": approval_id,
                "decision": decision,
                "actor": actor,
                "comment": comment,
            },
        )

    def run_connector_inbound(
        self,
        session_id: str,
        connector_id: str,
        event_type_map: Dict[str, str],
        external_event: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self._post(
            "/v1/connectors/inbound/run",
            {
                "session_id": session_id,
                "connector_id": connector_id,
                "event_type_map": event_type_map,
                "external_event": external_event,
            },
        )

    def run_connector_outbound(
        self,
        session_id: str,
        connector_id: str,
        action_type_map: Dict[str, str],
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self._post(
            "/v1/connectors/outbound/run",
            {
                "session_id": session_id,
                "connector_id": connector_id,
                "action_type_map": action_type_map,
                "action": action,
            },
        )

    def telemetry_summary(self) -> Dict[str, Any]:
        return self._get("/v1/observability/telemetry/summary")

    def call_runtime(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._post(
            "/v1/runtime/call",
            {
                "method": method,
                "params": params or {},
            },
        )

    def _get(self, path: str) -> Dict[str, Any]:
        return self._request_json("GET", path, payload=None)

    def _post(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request_json("POST", path, payload=payload or {})

    def _request_json(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        endpoint = self.base_url + path
        body: Optional[bytes] = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.api_token:
            headers["Authorization"] = "Bearer %s" % self.api_token

        req = request.Request(endpoint, data=body, method=method, headers=headers)

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except error.HTTPError as exc:
            text = exc.read().decode("utf-8", errors="replace")
            raise RuntimeSDKError("HTTP %s: %s" % (exc.code, text)) from exc
        except error.URLError as exc:
            raise RuntimeSDKError("Connection error: %s" % exc.reason) from exc

        try:
            parsed = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise RuntimeSDKError("Invalid JSON response") from exc

        if not isinstance(parsed, dict):
            raise RuntimeSDKError("Unexpected API response type")

        if parsed.get("api_version") != self.api_version:
            raise RuntimeSDKError(
                "API version mismatch: expected %s got %s"
                % (self.api_version, parsed.get("api_version"))
            )

        if not parsed.get("ok"):
            error_payload = parsed.get("error", {})
            if isinstance(error_payload, dict):
                message = error_payload.get("message", "API error")
            else:
                message = "API error"
            raise RuntimeSDKError(message)

        result = parsed.get("result")
        if not isinstance(result, dict):
            raise RuntimeSDKError("Unexpected API result shape")

        return result

import json

import pytest

from api.runtime_api import PublicRuntimeAPI
from api.runtime_factory import build_server_from_examples
from sdk.python_client import RuntimeSDKError, WorldRuntimeSDKClient


class _StubHTTPResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _policy_requires_proposal_approval(action_type: str):
    return {
        "policy_id": "policy.public-api.approval",
        "policy_name": "approval required",
        "default_outcome": "allow",
        "rules": [
            {
                "rule_id": "rule.public-api.approval",
                "rule_name": "approval",
                "condition": {
                    "field": "proposed_action.action_type",
                    "operator": "equals",
                    "value": action_type,
                },
                "outcome": "require_approval",
            }
        ],
    }


def test_public_runtime_api_core_flows(examples_dir):
    runtime_api = PublicRuntimeAPI(build_server_from_examples(examples_dir))
    session = runtime_api.create_session()

    proposal = {
        "proposal_id": "proposal.public-api.001",
        "proposer": "public-api-test",
        "proposed_action": {
            "action_type": "reroute_shipment",
            "target_ref": "shipment.88421",
            "payload": {"new_route": "route.delta"},
        },
        "rationale": "public api coverage",
    }

    proposal_result = runtime_api.submit_proposal(
        session_id=session["session_id"],
        proposal=proposal,
        policies=[_policy_requires_proposal_approval("reroute_shipment")],
    )
    approval_id = proposal_result["approval"]["approval_id"]
    assert proposal_result["policy_report"]["requires_approval"] is True

    approval_result = runtime_api.respond_approval(
        approval_id=approval_id,
        decision="approved",
        actor={
            "actor_id": "human.ops-manager-01",
            "actor_type": "human",
            "roles": ["operator"],
            "capabilities": ["approval.respond", "proposal.approve"],
        },
        comment="approved by API test",
    )
    assert approval_result["status"] == "approved"

    simulation_result = runtime_api.run_simulation(
        session_id=session["session_id"],
        simulation_id="sim.public-api.001",
        projection_name="world_state",
        hypothetical_events=[
            {
                "event_type": "shipment_delayed",
                "payload": {
                    "shipment_id": "shipment.88421",
                    "delay_hours": 2,
                    "cause": "weather",
                },
            }
        ],
    )
    assert simulation_result["status"] == "completed"

    inbound = runtime_api.run_connector_inbound(
        session_id=session["session_id"],
        connector_id="connector.integration.ingress",
        event_type_map={"external.delay_reported": "shipment_delayed"},
        external_event={
            "event_id": "evt.ingress.1",
            "event_type": "external.delay_reported",
            "provider": "mock.webhook",
            "source": "partner-system",
            "payload": {"shipment_id": "shipment.88421", "delay_hours": 1},
        },
    )
    assert inbound["status"] == "completed"

    outbound = runtime_api.run_connector_outbound(
        session_id=session["session_id"],
        connector_id="connector.integration.egress",
        action_type_map={"reroute_shipment": "dispatch.reroute"},
        action={
            "action_id": "action.public-api.001",
            "action_type": "reroute_shipment",
            "payload": {"shipment_id": "shipment.88421", "new_route": "route.delta"},
        },
    )
    assert outbound["status"] == "completed"

    telemetry = runtime_api.telemetry_summary()
    assert "events" in telemetry


def test_public_runtime_api_call_runtime_unwraps_errors(examples_dir):
    runtime_api = PublicRuntimeAPI(build_server_from_examples(examples_dir))
    with pytest.raises(ValueError):
        runtime_api._unwrap({"ok": False, "error": "unknown"})


@pytest.fixture
def sdk_mock_urlopen(examples_dir, monkeypatch):
    runtime_api = PublicRuntimeAPI(build_server_from_examples(examples_dir))

    def _fake_urlopen(req, timeout):
        path = req.full_url.split("//", 1)[-1].split("/", 1)[-1]
        route = "/" + path
        body = req.data.decode("utf-8") if req.data else "{}"
        payload = json.loads(body)

        if route == "/v1/sessions":
            result = runtime_api.create_session()
        elif route == "/v1/runtime/call":
            response = runtime_api.call_runtime(payload["method"], payload.get("params"))
            if not response.get("ok"):
                return _StubHTTPResponse(
                    {
                        "ok": False,
                        "api_version": "v1",
                        "error": {"message": response.get("error", "error")},
                    }
                )
            result = response["result"]
        elif route == "/v1/observability/telemetry/summary":
            result = runtime_api.telemetry_summary()
        else:
            raise AssertionError("unexpected route: %s" % route)

        return _StubHTTPResponse({"ok": True, "api_version": "v1", "result": result})

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)
    return runtime_api


def test_python_sdk_client_smoke(sdk_mock_urlopen):
    client = WorldRuntimeSDKClient(base_url="http://local.test")

    session = client.create_session()
    assert session["session_id"].startswith("session.")

    runtime_result = client.call_runtime("telemetry.summary")
    assert "events" in runtime_result

    with pytest.raises(RuntimeSDKError):
        client.call_runtime("unknown.method")

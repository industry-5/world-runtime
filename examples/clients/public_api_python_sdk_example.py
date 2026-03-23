import json
import os

from sdk.python_client import WorldRuntimeSDKClient


def main() -> None:
    client = WorldRuntimeSDKClient(
        base_url=os.getenv("WORLD_RUNTIME_API_BASE_URL", "http://127.0.0.1:8080"),
        api_token=os.getenv("WORLD_RUNTIME_API_TOKEN"),
    )

    session = client.create_session()

    proposal = {
        "proposal_id": "proposal.public-api.0001",
        "proposer": "sdk-demo",
        "proposed_action": {
            "action_type": "reroute_shipment",
            "target_ref": "shipment.88421",
            "payload": {"new_route": "route.gamma"},
        },
        "rationale": "SDK smoke flow",
    }

    policy = {
        "policy_id": "policy.demo.approval",
        "policy_name": "demo requires approval",
        "default_outcome": "allow",
        "rules": [
            {
                "rule_id": "rule.demo.approval",
                "rule_name": "approval required",
                "condition": {
                    "field": "proposed_action.action_type",
                    "operator": "equals",
                    "value": "reroute_shipment",
                },
                "outcome": "require_approval",
            }
        ],
    }

    proposal_result = client.submit_proposal(
        session_id=session["session_id"],
        proposal=proposal,
        policies=[policy],
    )

    print(json.dumps({"session": session, "proposal_result": proposal_result}, indent=2))


if __name__ == "__main__":
    main()

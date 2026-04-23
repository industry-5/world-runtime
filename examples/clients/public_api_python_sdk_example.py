import json
import os

from world_runtime.sdk import WorldRuntimeSDKClient


def main() -> None:
    client = WorldRuntimeSDKClient(
        base_url=os.getenv("WORLD_RUNTIME_API_BASE_URL", "http://127.0.0.1:8080"),
        api_token=os.getenv("WORLD_RUNTIME_API_TOKEN"),
    )

    session = client.create_session()
    runtime_inventory = client.runtime_inventory()
    runtime_services = client.list_runtime_services()

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

    runtime_reconcile = client.reconcile_runtime_services(
        actor={
            "actor_id": "human.sdk-demo",
            "actor_type": "human",
            "roles": ["operator"],
            "capabilities": ["runtime.service.reconcile"],
        },
        service_ids=["reference-http"],
        session_id=session["session_id"],
    )
    runtime_resolution = client.resolve_runtime_task(
        task_profile_id="structured-extraction.strict",
    )

    print(
        json.dumps(
            {
                "session": session,
                "runtime_inventory": runtime_inventory,
                "runtime_services": runtime_services,
                "proposal_result": proposal_result,
                "runtime_reconcile": runtime_reconcile,
                "runtime_resolution": runtime_resolution,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

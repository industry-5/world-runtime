import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from adapters.registry import AdapterRegistry
from core.connectors import (
    InboundConnectorConfig,
    OutboundConnectorConfig,
    RetryPolicy,
    TransientConnectorError,
)
from core.deployment import DeploymentLoader


@dataclass
class IntegrationStack:
    stack_id: str
    profile: str
    adapter_id: str
    scenario_path: str
    external_systems: List[Dict[str, Any]]
    ingress: Dict[str, Any]
    egress: Dict[str, Any]
    smoke_test: Dict[str, Any]
    owner: str


class IntegrationStackLoader:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.deployment_loader = DeploymentLoader(repo_root)
        self.stack_dir = repo_root / "infra" / "integration_stacks"

    def list_stack_names(self) -> List[str]:
        if not self.stack_dir.exists():
            return []
        return sorted(path.name for path in self.stack_dir.glob("*.json"))

    def load_stack(self, stack_name: str) -> IntegrationStack:
        file_name = stack_name if stack_name.endswith(".json") else "%s.json" % stack_name
        stack_path = self.stack_dir / file_name
        if not stack_path.exists():
            raise ValueError("integration stack not found: %s" % stack_name)

        payload = self._load_json(stack_path)
        return IntegrationStack(
            stack_id=payload["stack_id"],
            profile=payload["profile"],
            adapter_id=payload["adapter_id"],
            scenario_path=payload["scenario_path"],
            external_systems=list(payload.get("external_systems", [])),
            ingress=dict(payload.get("ingress", {})),
            egress=dict(payload.get("egress", {})),
            smoke_test=dict(payload.get("smoke_test", {})),
            owner=payload.get("owner", "unknown"),
        )

    def validate_stack(self, stack: IntegrationStack) -> List[str]:
        errors: List[str] = []

        try:
            profile = self.deployment_loader.load_profile(stack.profile)
        except ValueError as exc:
            return [str(exc)]

        registry = AdapterRegistry.with_defaults()
        try:
            adapter = registry.get(stack.adapter_id)
        except ValueError as exc:
            errors.append(str(exc))
            return errors

        scenario_dir = self.repo_root / stack.scenario_path
        if not scenario_dir.exists():
            errors.append("scenario_path does not exist: %s" % stack.scenario_path)
        adapter_scenario_dir = adapter.scenario_dir(self.repo_root)
        if scenario_dir.resolve() != adapter_scenario_dir.resolve():
            errors.append(
                "scenario_path %s does not match adapter scenario_dir %s"
                % (stack.scenario_path, adapter_scenario_dir.relative_to(self.repo_root))
            )
        for file_name in ("entities.json", "events.json", "proposal.json"):
            if not (scenario_dir / file_name).exists():
                errors.append("scenario file missing: %s/%s" % (stack.scenario_path, file_name))

        if stack.adapter_id not in profile.adapters:
            errors.append("adapter_id %s is not enabled by profile %s" % (stack.adapter_id, stack.profile))

        if not stack.external_systems:
            errors.append("external_systems must not be empty")

        ingress_map = stack.ingress.get("event_type_map")
        if not isinstance(ingress_map, dict) or not ingress_map:
            errors.append("ingress.event_type_map must contain at least one mapping")
        else:
            for mapped_event in ingress_map.values():
                if mapped_event not in adapter.event_types:
                    errors.append(
                        "ingress mapped event_type is not supported by adapter %s: %s"
                        % (stack.adapter_id, mapped_event)
                    )
        ingress_retry = stack.ingress.get("retry", {})
        ingress_attempts = ingress_retry.get("max_attempts", 3) if isinstance(ingress_retry, dict) else None
        if not isinstance(ingress_attempts, int) or ingress_attempts < 1:
            errors.append("ingress.retry.max_attempts must be an integer >= 1")

        action_map = stack.egress.get("action_type_map")
        if not isinstance(action_map, dict) or not action_map:
            errors.append("egress.action_type_map must contain at least one mapping")
        egress_retry = stack.egress.get("retry", {})
        egress_attempts = egress_retry.get("max_attempts", 3) if isinstance(egress_retry, dict) else None
        if not isinstance(egress_attempts, int) or egress_attempts < 1:
            errors.append("egress.retry.max_attempts must be an integer >= 1")

        smoke_query = stack.smoke_test.get("query")
        expected_query_type = stack.smoke_test.get("expected_query_type")
        if not isinstance(smoke_query, str) or not smoke_query.strip():
            errors.append("smoke_test.query must be a non-empty string")
        if not isinstance(expected_query_type, str) or not expected_query_type.strip():
            errors.append("smoke_test.expected_query_type must be a non-empty string")

        return errors

    def smoke_check(self, stack_name: str, run_eval: bool = True) -> Dict[str, Any]:
        stack = self.load_stack(stack_name)
        errors = self.validate_stack(stack)
        if errors:
            raise ValueError("integration stack invalid: %s" % "; ".join(errors))

        profile = self.deployment_loader.load_profile(stack.profile)
        runtime = self.deployment_loader.build_runtime(profile)
        adapter = runtime["registry"].get(stack.adapter_id)

        scenario_dir = self.repo_root / stack.scenario_path
        proposal = self._load_json(scenario_dir / "proposal.json")
        policy = self._load_json(adapter.default_policy_path(self.repo_root))
        policy_report = runtime["policy"].evaluate_policies([policy], proposal)

        session = runtime["app_server"].session_create()
        task = runtime["app_server"].task_submit(
            session_id=session["session_id"],
            method="reasoning.query",
            params={
                "projection_name": stack.smoke_test.get("projection_name", "world_state"),
                "query": stack.smoke_test["query"],
            },
        )
        query_type = task["result"].get("query_type")
        expected_query_type = stack.smoke_test["expected_query_type"]
        if query_type != expected_query_type:
            raise ValueError(
                "unexpected query_type for %s: expected=%s actual=%s"
                % (stack.stack_id, expected_query_type, query_type)
            )

        eval_status = "not_run"
        pass_rate = None
        if run_eval:
            eval_report = runtime["eval_harness"].run_suite(minimum_pass_rate=1.0)
            eval_status = eval_report["status"]
            pass_rate = eval_report["pass_rate"]

        connector_runtime = runtime["app_server"].connector_runtime
        inbound_config = InboundConnectorConfig(
            connector_id="%s.ingress" % stack.stack_id,
            event_type_map=dict(stack.ingress.get("event_type_map", {})),
            retry=RetryPolicy.from_config(stack.ingress.get("retry")),
        )
        sample_external_type = next(iter(stack.ingress["event_type_map"].keys()))
        inbound_attempts = {"count": 0}

        def _inbound_preprocessor(event: Dict[str, Any], attempt: int) -> Dict[str, Any]:
            inbound_attempts["count"] += 1
            if attempt == 1:
                raise TransientConnectorError("simulated ingress transient failure")
            return event

        inbound_result = connector_runtime.run_inbound(
            config=inbound_config,
            external_event={
                "external_id": "%s.inbound.001" % stack.stack_id,
                "event_type": sample_external_type,
                "payload": {"stack_id": stack.stack_id},
            },
            preprocessor=_inbound_preprocessor,
        )
        inbound_duplicate = connector_runtime.run_inbound(
            config=inbound_config,
            external_event={
                "external_id": "%s.inbound.001" % stack.stack_id,
                "event_type": sample_external_type,
                "payload": {"stack_id": stack.stack_id},
            },
        )

        sample_action_type = next(iter(stack.egress["action_type_map"].keys()))
        outbound_config = OutboundConnectorConfig(
            connector_id="%s.egress" % stack.stack_id,
            action_type_map=dict(stack.egress.get("action_type_map", {})),
            retry=RetryPolicy.from_config(stack.egress.get("retry")),
        )
        outbound_attempts = {"count": 0}

        def _transport(_: Dict[str, Any], attempt: int) -> Dict[str, Any]:
            outbound_attempts["count"] += 1
            if attempt == 1:
                raise TransientConnectorError("simulated egress transient failure")
            return {"ack": "delivered", "attempt": attempt}

        outbound_result = connector_runtime.run_outbound(
            config=outbound_config,
            action={
                "action_id": "%s.outbound.001" % stack.stack_id,
                "action_type": sample_action_type,
                "payload": {"stack_id": stack.stack_id},
            },
            transport=_transport,
        )
        outbound_duplicate = connector_runtime.run_outbound(
            config=outbound_config,
            action={
                "action_id": "%s.outbound.001" % stack.stack_id,
                "action_type": sample_action_type,
                "payload": {"stack_id": stack.stack_id},
            },
            transport=_transport,
        )

        return {
            "stack_id": stack.stack_id,
            "profile": stack.profile,
            "adapter_id": stack.adapter_id,
            "owner": stack.owner,
            "task_status": task["status"],
            "query_type": query_type,
            "policy_outcome": policy_report.final_outcome,
            "ingress_mappings": len(stack.ingress.get("event_type_map", {})),
            "egress_mappings": len(stack.egress.get("action_type_map", {})),
            "events_loaded": runtime["store"].last_offset() + 1 if runtime["store"].last_offset() is not None else 0,
            "eval_status": eval_status,
            "pass_rate": pass_rate,
            "connector_results": {
                "inbound": inbound_result["status"],
                "outbound": outbound_result["status"],
                "inbound_attempts": inbound_result.get("attempts", inbound_attempts["count"]),
                "outbound_attempts": outbound_result.get("attempts", outbound_attempts["count"]),
                "inbound_duplicate_status": inbound_duplicate["status"],
                "outbound_duplicate_status": outbound_duplicate["status"],
                "dead_letters": len(connector_runtime.list_dead_letters()),
            },
        }

    def _load_json(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

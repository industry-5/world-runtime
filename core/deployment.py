import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from adapters.registry import AdapterRegistry
from core.app_server import WorldRuntimeAppServer
from core.connectors import ConnectorRuntime
from core.eval_harness import EvalHarness
from core.observability import ObservabilityStore
from core.persistence import build_event_store_from_config
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


@dataclass
class DeploymentProfile:
    profile_id: str
    environment: str
    persistence_config: Path
    llm_config: Path
    adapters: List[str]
    bootstrap_scenarios: List[str]


class DeploymentLoader:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def load_profile(self, profile_name: str) -> DeploymentProfile:
        profile_path = self.repo_root / "infra" / "profiles" / ("%s.profile.json" % profile_name)
        if not profile_path.exists():
            raise ValueError("profile not found: %s" % profile_name)

        payload = self._load_json(profile_path)
        return DeploymentProfile(
            profile_id=payload["profile_id"],
            environment=payload["environment"],
            persistence_config=self.repo_root / payload["persistence_config"],
            llm_config=self.repo_root / payload["llm_config"],
            adapters=list(payload.get("adapters", [])),
            bootstrap_scenarios=list(payload.get("bootstrap_scenarios", [])),
        )

    def load_persistence_config(self, profile: DeploymentProfile) -> Dict[str, Any]:
        return self._load_json(profile.persistence_config)

    def build_runtime(self, profile: DeploymentProfile) -> Dict[str, Any]:
        registry = AdapterRegistry.with_defaults()
        persistence_config = self.load_persistence_config(profile)
        store = build_event_store_from_config(self.repo_root, persistence_config)

        for adapter_id in profile.adapters:
            adapter = registry.get(adapter_id)
            scenario_dir = adapter.scenario_dir(self.repo_root)
            events = self._load_json(scenario_dir / "events.json")
            for index, event in enumerate(events):
                stream_id = "%s.bootstrap.%d" % (adapter_id, index)
                store.append(stream_id, event)

        replay = ReplayEngine(store, SimpleProjector)
        simulation = SimulationEngine(replay, SimpleProjector)
        reasoning = ReasoningAdapter(replay)
        policy = DeterministicPolicyEngine()
        observability = ObservabilityStore()
        eval_harness = EvalHarness(
            replay_engine=replay,
            simulation_engine=simulation,
            reasoning_adapter=reasoning,
            policy_engine=policy,
            observability=observability,
        )
        app_server = WorldRuntimeAppServer(
            reasoning_adapter=reasoning,
            simulation_engine=simulation,
            replay_engine=replay,
            policy_engine=policy,
            eval_harness=eval_harness,
            observability=observability,
            connector_runtime=ConnectorRuntime(store),
        )

        return {
            "profile": profile,
            "registry": registry,
            "store": store,
            "replay": replay,
            "simulation": simulation,
            "reasoning": reasoning,
            "policy": policy,
            "eval_harness": eval_harness,
            "app_server": app_server,
            "observability": observability,
            "persistence_config": persistence_config,
        }

    def smoke_check(self, profile_name: str) -> Dict[str, Any]:
        profile = self.load_profile(profile_name)
        runtime = self.build_runtime(profile)

        session = runtime["app_server"].session_create()
        session_id = session["session_id"]
        task = runtime["app_server"].task_submit(
            session_id=session_id,
            method="reasoning.query",
            params={
                "projection_name": "world_state",
                "query": "What is the delay status for shipment.88421?",
            },
        )

        eval_report = runtime["eval_harness"].run_suite(minimum_pass_rate=1.0)

        return {
            "profile_id": profile.profile_id,
            "environment": profile.environment,
            "session_id": session_id,
            "task_status": task["status"],
            "query_type": task["result"].get("query_type"),
            "eval_status": eval_report["status"],
            "pass_rate": eval_report["pass_rate"],
            "events_loaded": runtime["store"].last_offset() + 1 if runtime["store"].last_offset() is not None else 0,
            "diagnostics": runtime["observability"].dashboard(),
        }

    def _load_json(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

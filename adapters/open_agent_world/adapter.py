from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class OpenAgentWorldAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-open-agent-world"

    @property
    def domain_name(self) -> str:
        return "open-agent-world"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "world_zone",
            "agent_cohort",
            "governance_beacon",
            "resource_pool",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "agent_cohort_admitted",
            "commons_conflict_detected",
            "intervention_plan_submitted",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "open-agent-world-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "open_agent_world" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "open_agent_world" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "open_agent_world" / "schemas" / "event_types.schema.json",
        ]

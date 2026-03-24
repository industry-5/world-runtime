from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class MultiAgentAIAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-multi-agent-ai"

    @property
    def domain_name(self) -> str:
        return "multi-agent-ai"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "agent_team",
            "coordination_goal",
            "shared_context",
            "review_board",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "agent_goal_published",
            "proposal_conflict_detected",
            "review_branch_scored",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "multi-agent-ai-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "multi_agent_ai" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "multi_agent_ai" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "multi_agent_ai" / "schemas" / "event_types.schema.json",
        ]

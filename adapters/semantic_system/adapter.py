from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class SemanticSystemAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-semantic-system"

    @property
    def domain_name(self) -> str:
        return "semantic-system"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "semantic_term",
            "semantic_definition",
            "semantic_mapping",
            "governance_board",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "semantic_term_registered",
            "mapping_conflict_detected",
            "meaning_change_requested",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "semantic-system-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "semantic_system" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "semantic_system" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "semantic_system" / "schemas" / "event_types.schema.json",
        ]

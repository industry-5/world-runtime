from pathlib import Path
from typing import List, Set

from adapters.base import DomainAdapter


class __ADAPTER_NAME_CLASS__Adapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "__ADAPTER_ID__"

    @property
    def domain_name(self) -> str:
        return "__ADAPTER_NAME__"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "__ADAPTER_SLUG__.resource",
            "__ADAPTER_SLUG__.actor",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "__ADAPTER_SLUG__.resource.updated",
            "__ADAPTER_SLUG__.action.requested",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "__ADAPTER_SLUG__-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "__ADAPTER_SLUG__" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path) -> List[Path]:
        base = repo_root / "adapters" / "__ADAPTER_SLUG__" / "schemas"
        return [
            base / "entity_types.schema.json",
            base / "event_types.schema.json",
        ]

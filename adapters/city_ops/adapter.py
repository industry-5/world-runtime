from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class CityOpsAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-city-ops"

    @property
    def domain_name(self) -> str:
        return "city-ops"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "city_agency",
            "transit_corridor",
            "utility_asset",
            "response_zone",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "water_main_break_detected",
            "transit_service_suspended",
            "unified_command_activated",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "city-ops-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "city_ops" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "city_ops" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "city_ops" / "schemas" / "event_types.schema.json",
        ]

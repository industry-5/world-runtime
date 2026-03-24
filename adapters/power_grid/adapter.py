from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class PowerGridAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-power-grid"

    @property
    def domain_name(self) -> str:
        return "power-grid"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "balancing_authority",
            "generator",
            "transmission_line",
            "substation",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "demand_spike_detected",
            "transmission_line_derated",
            "reserve_dispatch_committed",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "power-grid-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "power_grid" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "power_grid" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "power_grid" / "schemas" / "event_types.schema.json",
        ]

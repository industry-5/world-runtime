from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class AirTrafficAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-air-traffic"

    @property
    def domain_name(self) -> str:
        return "air-traffic"

    @property
    def entity_types(self) -> Set[str]:
        return {"airport", "runway", "flight", "control_sector"}

    @property
    def event_types(self) -> Set[str]:
        return {
            "weather_alert_issued",
            "runway_incursion_detected",
            "flight_holding_pattern_assigned",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "air-traffic-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "air_traffic" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "air_traffic" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "air_traffic" / "schemas" / "event_types.schema.json",
        ]

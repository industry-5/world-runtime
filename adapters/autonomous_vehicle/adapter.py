from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class AutonomousVehicleAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-autonomous-vehicle"

    @property
    def domain_name(self) -> str:
        return "autonomous-vehicle"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "autonomous_vehicle",
            "road_segment",
            "hazard_zone",
            "remote_supervisor",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "occlusion_detected",
            "fallback_path_scored",
            "teleassist_plan_submitted",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "autonomous-vehicle-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "autonomous_vehicle" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "autonomous_vehicle" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "autonomous_vehicle" / "schemas" / "event_types.schema.json",
        ]

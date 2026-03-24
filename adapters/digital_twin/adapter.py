from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class DigitalTwinAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-digital-twin"

    @property
    def domain_name(self) -> str:
        return "digital-twin"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "dt_host_binding",
            "dt_overlay_model",
            "dt_signal_feed",
            "dt_control_center",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "host_binding_established",
            "telemetry_snapshot_ingested",
            "overlay_risk_projected",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "digital-twin-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "digital_twin" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "digital_twin" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "digital_twin" / "schemas" / "event_types.schema.json",
        ]

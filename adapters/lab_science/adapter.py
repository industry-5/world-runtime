from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class LabScienceAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-lab-science"

    @property
    def domain_name(self) -> str:
        return "lab-science"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "lab_program",
            "sample_batch",
            "instrument_run",
            "quality_review_board",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "sample_batch_registered",
            "control_drift_detected",
            "deviation_review_requested",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "lab-science-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "lab_science" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "lab_science" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "lab_science" / "schemas" / "event_types.schema.json",
        ]

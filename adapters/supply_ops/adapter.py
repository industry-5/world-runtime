from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class SupplyOpsAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-supply-ops"

    @property
    def domain_name(self) -> str:
        return "supply-ops"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "order_commitment",
            "inventory_position",
            "capacity_bucket",
            "fulfillment_lane",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "commitment_risk_detected",
            "inventory_rebalance_planned",
            "capacity_reservation_requested",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "supply-ops-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "supply_ops" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "supply_ops" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "supply_ops" / "schemas" / "event_types.schema.json",
        ]

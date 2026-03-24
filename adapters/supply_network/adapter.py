from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class SupplyNetworkAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-supply-network"

    @property
    def domain_name(self) -> str:
        return "supply-network"

    @property
    def entity_types(self) -> Set[str]:
        return {"supplier", "factory", "shipment"}

    @property
    def event_types(self) -> Set[str]:
        return {"shipment_delayed", "shipment_rerouted", "supplier_failed"}

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "supply-network-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "supply_network" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "supply_network" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "supply_network" / "schemas" / "event_types.schema.json",
        ]

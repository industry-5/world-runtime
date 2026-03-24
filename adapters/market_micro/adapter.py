from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class MarketMicroAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-market-micro"

    @property
    def domain_name(self) -> str:
        return "market-micro"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "market_venue",
            "trading_firm",
            "instrument_book",
            "risk_limit",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "order_flow_spike_detected",
            "inventory_limit_warning",
            "risk_reduction_plan_submitted",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "market-micro-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "market_micro" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "market_micro" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "market_micro" / "schemas" / "event_types.schema.json",
        ]

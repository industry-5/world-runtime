from typing import Dict, List, Optional

from adapters.air_traffic.adapter import AirTrafficAdapter
from adapters.base import DomainAdapter
from adapters.supply_network.adapter import SupplyNetworkAdapter

try:
    from adapters.world_game.adapter import WorldGameAdapter
except ImportError:  # pragma: no cover - exercised by stripped public exports
    WorldGameAdapter = None


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: Dict[str, DomainAdapter] = {}

    def register(self, adapter: DomainAdapter) -> None:
        self._adapters[adapter.adapter_id] = adapter

    def get(self, adapter_id: str) -> DomainAdapter:
        adapter = self._adapters.get(adapter_id)
        if adapter is None:
            raise ValueError("unknown adapter_id: %s" % adapter_id)
        return adapter

    def maybe_get(self, adapter_id: str) -> Optional[DomainAdapter]:
        return self._adapters.get(adapter_id)

    def list(self) -> List[DomainAdapter]:
        return [self._adapters[key] for key in sorted(self._adapters.keys())]

    @classmethod
    def with_defaults(cls) -> "AdapterRegistry":
        registry = cls()
        registry.register(SupplyNetworkAdapter())
        registry.register(AirTrafficAdapter())
        if WorldGameAdapter is not None:
            registry.register(WorldGameAdapter())
        return registry

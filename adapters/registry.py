from typing import Dict, List

from adapters.air_traffic.adapter import AirTrafficAdapter
from adapters.base import DomainAdapter
from adapters.supply_network.adapter import SupplyNetworkAdapter
from adapters.world_game.adapter import WorldGameAdapter


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

    def list(self) -> List[DomainAdapter]:
        return [self._adapters[key] for key in sorted(self._adapters.keys())]

    @classmethod
    def with_defaults(cls) -> "AdapterRegistry":
        registry = cls()
        registry.register(SupplyNetworkAdapter())
        registry.register(AirTrafficAdapter())
        registry.register(WorldGameAdapter())
        return registry

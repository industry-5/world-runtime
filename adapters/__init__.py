from adapters.air_traffic.adapter import AirTrafficAdapter
from adapters.registry import AdapterRegistry
from adapters.supply_network.adapter import SupplyNetworkAdapter

try:
    from adapters.world_game.adapter import WorldGameAdapter
except ImportError:  # pragma: no cover - exercised by stripped public exports
    WorldGameAdapter = None

__all__ = [
    "AdapterRegistry",
    "SupplyNetworkAdapter",
    "AirTrafficAdapter",
]

if WorldGameAdapter is not None:
    __all__.append("WorldGameAdapter")

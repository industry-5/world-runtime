import json
from pathlib import Path

from core.app_server import WorldRuntimeAppServer
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_server_from_examples(examples_dir: Path) -> WorldRuntimeAppServer:
    store = InMemoryEventStore()

    supply_event = _load_json(examples_dir / "scenarios" / "supply-network-mini" / "events.json")[0]
    air_traffic_event = _load_json(examples_dir / "scenarios" / "air-traffic-mini" / "events.json")[0]
    store.append("shipment.88421", supply_event)
    store.append("flight.ual2187", air_traffic_event)
    world_game_events_path = examples_dir / "scenarios" / "world-game-mini" / "events.json"
    if world_game_events_path.exists():
        world_game_modern_event = _load_json(world_game_events_path)[0]
        store.append("wg.region.pilot", world_game_modern_event)

    replay = ReplayEngine(store, SimpleProjector)
    simulation = SimulationEngine(replay, SimpleProjector)
    reasoning = ReasoningAdapter(replay)
    policy = DeterministicPolicyEngine()
    return WorldRuntimeAppServer(
        reasoning_adapter=reasoning,
        simulation_engine=simulation,
        replay_engine=replay,
        policy_engine=policy,
    )

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.app_server import WorldRuntimeAppServer
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_server_from_examples(examples_dir: Path) -> WorldRuntimeAppServer:
    store = InMemoryEventStore()

    supply_event = load_json(examples_dir / "scenarios" / "supply-network-mini" / "events.json")[0]
    air_traffic_event = load_json(examples_dir / "scenarios" / "air-traffic-mini" / "events.json")[0]
    store.append("shipment.88421", supply_event)
    store.append("flight.ual2187", air_traffic_event)

    replay = ReplayEngine(store, SimpleProjector)
    sim_engine = SimulationEngine(replay, SimpleProjector)
    reasoning = ReasoningAdapter(replay)
    policy = DeterministicPolicyEngine()
    return WorldRuntimeAppServer(
        reasoning_adapter=reasoning,
        simulation_engine=sim_engine,
        replay_engine=replay,
        policy_engine=policy,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="World Runtime App Server test client")
    parser.add_argument("--examples-dir", default="examples", help="Path to examples directory")
    parser.add_argument("--query", default="What is the delay status for shipment.88421?")
    args = parser.parse_args()

    server = build_server_from_examples(Path(args.examples_dir))
    session = server.handle_request("session.create")
    session_id = session["result"]["session_id"]

    task = server.handle_request(
        "task.submit",
        {
            "session_id": session_id,
            "method": "reasoning.query",
            "params": {
                "projection_name": "world_state",
                "query": args.query,
            },
        },
    )

    events = server.handle_request("task.events.subscribe", {"session_id": session_id, "since": 0})

    output = {
        "session": session,
        "task": task,
        "events": events,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

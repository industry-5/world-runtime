import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.eval_harness import EvalHarness
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine
EVALS_DIR = REPO_ROOT / "evals"
MANIFEST_PATH = EVALS_DIR / "suites.manifest.json"
REPORTS_DIR = EVALS_DIR / "reports"
EXAMPLES_DIR = REPO_ROOT / "examples"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_harness() -> EvalHarness:
    store = InMemoryEventStore()

    supply_event = load_json(EXAMPLES_DIR / "scenarios" / "supply-network-mini" / "events.json")[0]
    air_traffic_event = load_json(EXAMPLES_DIR / "scenarios" / "air-traffic-mini" / "events.json")[0]

    store.append("shipment.88421", supply_event)
    store.append("flight.ual2187", air_traffic_event)

    replay = ReplayEngine(store, SimpleProjector)
    simulation = SimulationEngine(replay, SimpleProjector)
    reasoning = ReasoningAdapter(replay)
    policy = DeterministicPolicyEngine()
    return EvalHarness(
        replay_engine=replay,
        simulation_engine=simulation,
        reasoning_adapter=reasoning,
        policy_engine=policy,
    )


def write_reports(report: dict) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    latest = REPORTS_DIR / "latest.json"
    timestamp = report["ran_at"].replace(":", "-")
    stamped = REPORTS_DIR / ("report-%s.json" % timestamp)

    with latest.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    with stamped.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    harness = build_harness()

    report = harness.run_suite(
        eval_ids=manifest.get("eval_ids"),
        minimum_pass_rate=float(manifest.get("minimum_pass_rate", 1.0)),
    )

    write_reports(report)

    print("Suite:", report["suite"])
    print("Status:", report["status"])
    print("Pass rate:", report["pass_rate"])
    print("Passed/Total:", "%d/%d" % (report["passed"], report["total"]))

    if report["failed_eval_ids"]:
        print("Failed:", ", ".join(report["failed_eval_ids"]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Any, Callable, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from api.runtime_api import PublicRuntimeAPI
from core.deployment import DeploymentLoader
from core.path_utils import resolve_writable_repo_path


def _metric(samples: List[float], operations: int) -> Dict[str, Any]:
    total = sum(samples)
    sample_count = len(samples)
    return {
        "sample_count": sample_count,
        "operations_per_sample": operations,
        "total_seconds": round(total, 6),
        "avg_seconds": round(total / sample_count, 6) if sample_count else 0.0,
        "median_seconds": round(statistics.median(samples), 6) if sample_count else 0.0,
        "min_seconds": round(min(samples), 6) if sample_count else 0.0,
        "max_seconds": round(max(samples), 6) if sample_count else 0.0,
        "ops_per_second": round((operations * sample_count) / total, 2) if total > 0 else 0.0,
    }


def _timeit(fn: Callable[[], None], samples: int) -> List[float]:
    durations: List[float] = []
    for _ in range(samples):
        started = time.perf_counter()
        fn()
        durations.append(time.perf_counter() - started)
    return durations


def _policy_requires_approval(action_type: str) -> Dict[str, Any]:
    return {
        "policy_id": "policy.benchmark.approval",
        "policy_name": "approval_required",
        "default_outcome": "allow",
        "rules": [
            {
                "rule_id": "rule.benchmark.approval",
                "rule_name": "approval required",
                "condition": {
                    "field": "proposed_action.action_type",
                    "operator": "equals",
                    "value": action_type,
                },
                "outcome": "require_approval",
            }
        ],
    }


def _build_workload_fingerprint(payload: Dict[str, Any]) -> str:
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return digest


def run_profile_benchmark(
    profile: str,
    replay_events: int,
    iterations: int,
    samples: int,
) -> Dict[str, Any]:
    loader = DeploymentLoader(REPO_ROOT)
    runtime = loader.build_runtime(loader.load_profile(profile))
    app_server = runtime["app_server"]
    replay_engine = runtime["replay"]
    policy_engine = runtime["policy"]
    connector_runtime = runtime["connector_runtime"] if "connector_runtime" in runtime else app_server.connector_runtime
    public_api = PublicRuntimeAPI(app_server)

    for index in range(replay_events):
        runtime["store"].append(
            "bench.events",
            {
                "event_id": "evt.bench.%04d" % index,
                "event_type": "shipment_delayed",
                "payload": {
                    "shipment_id": "shipment.bench.%04d" % index,
                    "delay_hours": (index % 5) + 1,
                    "cause": "benchmark",
                },
            },
        )

    session = app_server.session_create()
    session_id = session["session_id"]

    proposal = {
        "proposal_id": "proposal.bench.001",
        "proposer": "benchmark",
        "proposed_action": {
            "action_type": "reroute_shipment",
            "target_ref": "shipment.88421",
            "payload": {"new_route": "route.benchmark"},
        },
        "rationale": "benchmark",
    }
    policy = _policy_requires_approval("reroute_shipment")
    simulation_counter = {"value": 0}

    def replay_flow() -> None:
        replay_engine.rebuild("world_state", use_snapshot=False)

    def policy_flow() -> None:
        for _ in range(iterations):
            policy_engine.evaluate_policies([policy], proposal)

    def simulation_flow() -> None:
        for step in range(iterations):
            sim_id = "sim.bench.%06d" % simulation_counter["value"]
            simulation_counter["value"] += 1
            app_server.simulation_engine.create_branch(sim_id, "world_state", scenario_name="benchmark")
            app_server.simulation_engine.apply_hypothetical_event(
                sim_id,
                {
                    "event_type": "shipment_delayed",
                    "payload": {
                        "shipment_id": "shipment.88421",
                        "delay_hours": (step % 3) + 1,
                        "cause": "simulated",
                    },
                },
            )
            app_server.simulation_engine.run(sim_id)

    def connector_flow() -> None:
        for step in range(iterations):
            outbound = app_server.connector_outbound_run(
                session_id=session_id,
                connector_id="connector.bench.egress",
                action_type_map={"reroute_shipment": "dispatch.reroute"},
                action={
                    "action_id": "action.bench.%04d" % step,
                    "action_type": "reroute_shipment",
                    "payload": {"shipment_id": "shipment.88421", "new_route": "route.%d" % step},
                },
            )
            if outbound.get("status") not in {"completed", "duplicate"}:
                raise RuntimeError("unexpected outbound status: %s" % outbound.get("status"))

            inbound = app_server.connector_inbound_run(
                session_id=session_id,
                connector_id="connector.bench.ingress",
                event_type_map={"external.delay": "shipment_delayed"},
                external_event={
                    "event_id": "event.bench.%04d" % step,
                    "event_type": "external.delay",
                    "payload": {
                        "shipment_id": "shipment.88421",
                        "delay_hours": 1,
                        "cause": "benchmark",
                    },
                },
            )
            if inbound.get("status") not in {"completed", "duplicate"}:
                raise RuntimeError("unexpected inbound status: %s" % inbound.get("status"))

    def public_api_flow() -> None:
        for step in range(iterations):
            response = public_api.call_runtime("telemetry.summary")
            if not response.get("ok"):
                raise RuntimeError(response.get("error", "telemetry.summary failed"))

            out = public_api.run_connector_outbound(
                session_id=session_id,
                connector_id="connector.public.bench",
                action_type_map={"reroute_shipment": "dispatch.reroute"},
                action={
                    "action_id": "action.public.%04d" % step,
                    "action_type": "reroute_shipment",
                    "payload": {"shipment_id": "shipment.88421", "new_route": "route.public"},
                },
            )
            if out.get("status") not in {"completed", "duplicate"}:
                raise RuntimeError("unexpected public outbound status: %s" % out.get("status"))

    benchmark = {
        "replay": _metric(_timeit(replay_flow, samples), 1),
        "policy": _metric(_timeit(policy_flow, samples), iterations),
        "simulation": _metric(_timeit(simulation_flow, samples), iterations),
        "connectors": _metric(_timeit(connector_flow, samples), iterations * 2),
        "public_api": _metric(_timeit(public_api_flow, samples), iterations * 2),
        "store_last_offset": runtime["store"].last_offset(),
        "connector_state_backend": connector_runtime.state_store.__class__.__name__,
    }

    return benchmark


def main() -> int:
    parser = argparse.ArgumentParser(description="Run M23 performance benchmark harness")
    parser.add_argument("--profiles", nargs="+", default=["local", "dev"], choices=["local", "dev"])
    parser.add_argument("--iterations", type=int, default=25)
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--replay-events", type=int, default=1200)
    parser.add_argument("--output", default="tmp/diagnostics/m23_benchmarks.latest.json")
    args = parser.parse_args()

    if args.iterations < 1:
        raise SystemExit("--iterations must be >= 1")
    if args.samples < 1:
        raise SystemExit("--samples must be >= 1")
    if args.replay_events < 1:
        raise SystemExit("--replay-events must be >= 1")

    workload = {
        "iterations": args.iterations,
        "samples": args.samples,
        "replay_events": args.replay_events,
        "profiles": args.profiles,
    }

    results: Dict[str, Any] = {}
    for profile in args.profiles:
        results[profile] = run_profile_benchmark(
            profile=profile,
            replay_events=args.replay_events,
            iterations=args.iterations,
            samples=args.samples,
        )

    payload = {
        "benchmark_status": "passed",
        "workload": workload,
        "workload_fingerprint": _build_workload_fingerprint(workload),
        "results": results,
    }

    output_path = resolve_writable_repo_path(REPO_ROOT, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from core.eval_harness import EvalHarness
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine
from conftest import load_json


def build_harness(supply_network_scenario_dir, air_traffic_scenario_dir):
    store = InMemoryEventStore()
    supply_event = load_json(supply_network_scenario_dir / "events.json")[0]
    air_traffic_event = load_json(air_traffic_scenario_dir / "events.json")[0]
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


def test_eval_list_contains_required_categories(supply_network_scenario_dir, air_traffic_scenario_dir):
    harness = build_harness(supply_network_scenario_dir, air_traffic_scenario_dir)

    listed = harness.list_evals()
    categories = {item["category"] for item in listed}

    assert "functional" in categories
    assert "policy" in categories
    assert "simulation" in categories
    assert "reasoning" in categories
    assert "safety" in categories
    assert "regression" in categories


def test_single_eval_run_reports_status(supply_network_scenario_dir, air_traffic_scenario_dir):
    harness = build_harness(supply_network_scenario_dir, air_traffic_scenario_dir)

    result = harness.run_eval("eval.smoke.policy")

    assert result["eval_id"] == "eval.smoke.policy"
    assert result["status"] == "passed"
    assert result["details"]["final_outcome"] == "deny"


def test_suite_run_enforces_threshold(supply_network_scenario_dir, air_traffic_scenario_dir):
    harness = build_harness(supply_network_scenario_dir, air_traffic_scenario_dir)

    report = harness.run_suite(minimum_pass_rate=1.0)

    assert report["status"] == "passed"
    assert report["pass_rate"] == 1.0
    assert report["failed_eval_ids"] == []


def test_suite_selective_run(supply_network_scenario_dir, air_traffic_scenario_dir):
    harness = build_harness(supply_network_scenario_dir, air_traffic_scenario_dir)

    report = harness.run_suite(
        eval_ids=["eval.smoke.runtime", "eval.regression.replay_determinism"],
        minimum_pass_rate=1.0,
    )

    assert report["total"] == 2
    assert report["passed"] == 2
    assert report["status"] == "passed"


def test_eval_harness_emits_observability_signals(supply_network_scenario_dir, air_traffic_scenario_dir):
    harness = build_harness(supply_network_scenario_dir, air_traffic_scenario_dir)
    harness.run_eval("eval.smoke.policy")
    harness.run_suite(eval_ids=["eval.smoke.runtime"], minimum_pass_rate=1.0)

    summary = harness.observability.summary()
    assert summary["totals"]["events"] >= 2
    assert summary["totals"]["traces"] >= 2
    assert "eval_harness" in summary["events"]["by_component"]


def test_air_traffic_safety_eval_catches_regressions(supply_network_scenario_dir, air_traffic_scenario_dir):
    harness = build_harness(supply_network_scenario_dir, air_traffic_scenario_dir)
    result = harness.run_eval("eval.safety.air_traffic_constraints")

    assert result["status"] == "passed"
    assert result["details"]["unsafe_outcome"] == "deny"
    assert result["details"]["constrained_outcome"] == "require_approval"
    assert result["details"]["safe_outcome"] == "allow"

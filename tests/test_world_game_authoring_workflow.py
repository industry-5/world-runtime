import json
from pathlib import Path
import subprocess
import sys

from core.app_server import WorldRuntimeAppServer
from core.domains.world_game import initialize_baseline_state
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.reasoning_adapter import ReasoningAdapter
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = REPO_ROOT / "examples" / "world-game-authoring" / "template_bundle.multi-region.v1.json"
AUTHORING_SCRIPT = REPO_ROOT / "scripts" / "world_game_authoring.py"
EXPECTED_WG_M10_PACKS = {
    "wg.authoring.bundle.multi-region-stress.v1",
    "wg.authoring.bundle.resilience-first-regional-planning.v1",
}


def build_server():
    store = InMemoryEventStore()
    replay = ReplayEngine(store, SimpleProjector)
    sim_engine = SimulationEngine(replay, SimpleProjector)
    reasoning = ReasoningAdapter(replay)
    return WorldRuntimeAppServer(
        reasoning_adapter=reasoning,
        simulation_engine=sim_engine,
        replay_engine=replay,
        policy_engine=DeterministicPolicyEngine(),
    )


def test_world_game_authoring_runtime_workflow_round_trip():
    server = build_server()

    listed = server.handle_request("world_game.authoring.template.list")
    assert listed["ok"] is True
    assert listed["result"]["count"] >= 1
    listed_bundle_ids = {item["bundle_id"] for item in listed["result"]["bundles"]}
    assert EXPECTED_WG_M10_PACKS.issubset(listed_bundle_ids)

    draft_created = server.handle_request(
        "world_game.authoring.draft.create",
        {
            "source_bundle_path": str(BUNDLE_PATH),
            "bundle_id": "wg.authoring.bundle.workflow-test.v1",
            "label": "Workflow Test Draft",
            "deterministic_version_seed": "wg-m9-workflow-seed.v1",
            "updated_at": "2026-03-11T12:00:00Z",
            "created_at": "2026-03-11T12:00:00Z",
            "tags": ["wg-m9", "workflow"],
        },
    )
    assert draft_created["ok"] is True
    draft_bundle = draft_created["result"]["bundle"]
    assert draft_bundle["bundle_metadata"]["status"] == "draft"

    validated = server.handle_request(
        "world_game.authoring.draft.validate",
        {
            "draft_bundle": draft_bundle,
        },
    )
    assert validated["ok"] is True
    assert validated["result"]["valid"] is True
    assert validated["result"]["errors"] == []

    published = server.handle_request(
        "world_game.authoring.bundle.publish",
        {
            "draft_bundle": draft_bundle,
        },
    )
    assert published["ok"] is True
    publication = published["result"]["publication"]
    assert publication["status"] == "published"
    assert publication["published_bundle_id"].startswith("wg.authoring.bundle.workflow-test.v1@")

    published_again = server.handle_request(
        "world_game.authoring.bundle.publish",
        {
            "draft_bundle": draft_bundle,
        },
    )
    assert published_again["ok"] is True
    assert published_again["result"]["publication"]["published_bundle_id"] == publication["published_bundle_id"]

    instantiated = server.handle_request(
        "world_game.authoring.bundle.instantiate",
        {
            "bundle": published["result"]["bundle"],
            "template_id": "template.wg.multi-region.core.v1",
            "parameter_values": {
                "region_count": 2,
                "scenario_suffix": "wg-m9-runtime-workflow",
                "baseline_tag": "wg-m9",
            },
        },
    )
    assert instantiated["ok"] is True
    scenario = instantiated["result"]["scenario"]
    assert scenario["scenario_id"].endswith("wg-m9-runtime-workflow")
    assert len(scenario["regions"]) == 2

    baseline = initialize_baseline_state(scenario, branch_id="baseline")
    assert baseline["turn"] == 0


def test_world_game_authoring_cli_workflow_round_trip(tmp_path):
    draft_path = tmp_path / "draft.bundle.json"
    published_path = tmp_path / "published.bundle.json"
    scenario_path = tmp_path / "scenario.generated.json"

    scaffold = subprocess.run(
        [
            sys.executable,
            str(AUTHORING_SCRIPT),
            "scaffold",
            "--source-bundle",
            str(BUNDLE_PATH),
            "--output-path",
            str(draft_path),
            "--bundle-id",
            "wg.authoring.bundle.cli-test.v1",
            "--label",
            "CLI Test Draft",
            "--deterministic-version-seed",
            "wg-m9-cli-seed.v1",
            "--updated-at",
            "2026-03-11T12:30:00Z",
            "--created-at",
            "2026-03-11T12:30:00Z",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert scaffold.returncode == 0, scaffold.stderr
    assert draft_path.exists()

    validate = subprocess.run(
        [
            sys.executable,
            str(AUTHORING_SCRIPT),
            "validate",
            "--bundle-path",
            str(draft_path),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert validate.returncode == 0, validate.stderr
    validate_payload = json.loads(validate.stdout)
    assert validate_payload["valid"] is True

    publish = subprocess.run(
        [
            sys.executable,
            str(AUTHORING_SCRIPT),
            "publish",
            "--bundle-path",
            str(draft_path),
            "--output-path",
            str(published_path),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert publish.returncode == 0, publish.stderr
    publish_payload = json.loads(publish.stdout)
    assert publish_payload["publication"]["status"] == "published"
    assert published_path.exists()

    instantiate = subprocess.run(
        [
            sys.executable,
            str(AUTHORING_SCRIPT),
            "instantiate",
            "--bundle-path",
            str(published_path),
            "--template-id",
            "template.wg.multi-region.core.v1",
            "--param",
            "region_count=2",
            "--param",
            "scenario_suffix=wg-m9-cli-workflow",
            "--scenario-output-path",
            str(scenario_path),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert instantiate.returncode == 0, instantiate.stderr
    instantiate_payload = json.loads(instantiate.stdout)
    assert instantiate_payload["scenario_id"].endswith("wg-m9-cli-workflow")
    assert scenario_path.exists()

    generated = json.loads(scenario_path.read_text(encoding="utf-8"))
    assert generated["scenario_id"].endswith("wg-m9-cli-workflow")
    assert len(generated["regions"]) == 2

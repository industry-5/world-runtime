import runpy
from pathlib import Path

import pytest

from adapters.public_program import (
    implemented_public_adapter_tracks,
    public_adapter_tracks,
    validate_public_package_checklist,
)
from adapters.registry import AdapterRegistry
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.replay_engine import ReplayEngine
from conftest import load_json


REPO_ROOT = Path(__file__).resolve().parents[1]
WORLD_GAME_DIR = REPO_ROOT / "adapters" / ("world" + "_game")
WORLD_GAME_RULE = "adapters/" + ("world" + "_game/")


def test_default_registry_contains_domain_adapters():
    registry = AdapterRegistry.with_defaults()
    adapter_ids = {adapter.adapter_id for adapter in registry.list()}
    public_adapter_ids = {track.adapter_id for track in implemented_public_adapter_tracks()}

    assert public_adapter_ids.issubset(adapter_ids)
    assert "adapter-supply-ops" in adapter_ids
    if WORLD_GAME_DIR.exists():
        assert "adapter-world-game" in adapter_ids
    assert len(adapter_ids) >= len(public_adapter_ids) + 1


def test_public_adapter_program_package_checklist_exists():
    for track in public_adapter_tracks():
        assert validate_public_package_checklist(track, REPO_ROOT) == []


def test_public_export_rewrites_match_current_public_adapter_story(tmp_path):
    export_script = REPO_ROOT / "scripts" / "build_public_export.py"
    if not export_script.exists():
        pytest.skip("public export script is intentionally omitted from the sanitized public repo")

    export_module = runpy.run_path(str(export_script))
    for relative_path in (
        "README.md",
        "STATUS.md",
        "ROADMAP.md",
        "docs/README.md",
        "docs/what-you-can-build.md",
    ):
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("placeholder\n", encoding="utf-8")
    export_module["apply_export_rewrites"](tmp_path, [WORLD_GAME_RULE])

    readme_text = (tmp_path / "README.md").read_text(encoding="utf-8")
    status_text = (tmp_path / "STATUS.md").read_text(encoding="utf-8")
    roadmap_text = (tmp_path / "ROADMAP.md").read_text(encoding="utf-8")
    docs_readme_text = (tmp_path / "docs" / "README.md").read_text(encoding="utf-8")
    what_text = (tmp_path / "docs" / "what-you-can-build.md").read_text(encoding="utf-8")

    standalone_tracks = [track for track in implemented_public_adapter_tracks() if not track.overlay]
    for track in standalone_tracks:
        assert track.adapter_id in readme_text
        assert f"[adapters/{track.package_slug}/README.md]" in docs_readme_text
        assert f"[adapters/{track.package_slug}/README.md]" in what_text

    assert "adapter-digital-twin" in readme_text
    assert "[adapters/digital_twin/README.md]" in docs_readme_text
    assert "[adapters/digital_twin/README.md]" in what_text
    assert "digital-twin-mini" in what_text

    assert "DA-M1 through DA-M9 complete" in status_text
    assert "Additional adapter tracks may remain planned" not in status_text

    assert "execute `DA-M4`" not in roadmap_text
    assert "current supply-network, air-traffic, and semantic-system proofs" not in roadmap_text
    assert "downstream promotion/export follow-through" in roadmap_text

    assert "eleven standalone proof paths plus one host-bound overlay track" in what_text


def test_adapter_level_assets_exist():
    registry = AdapterRegistry.with_defaults()

    for adapter in registry.list():
        assert adapter.default_policy_path(REPO_ROOT).exists()
        schema_paths = adapter.adapter_schema_paths(REPO_ROOT)
        assert len(schema_paths) >= 2
        for schema_path in schema_paths:
            assert schema_path.exists()


def test_adapters_validate_their_own_scenario_types():
    registry = AdapterRegistry.with_defaults()

    for adapter in registry.list():
        scenario = adapter.scenario_dir(REPO_ROOT)
        entities = load_json(scenario / "entities.json")
        events = load_json(scenario / "events.json")

        assert adapter.validate_entities(entities) == []
        assert adapter.validate_events(events) == []


def test_adapter_policies_evaluate_without_kernel_changes():
    registry = AdapterRegistry.with_defaults()
    policy_engine = DeterministicPolicyEngine()

    expectations = {
        "adapter-supply-network": {"final_outcome": "warn", "requires_warn": False},
        "adapter-supply-ops": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-air-traffic": {"final_outcome": "require_approval", "requires_warn": False},
        "adapter-semantic-system": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-power-grid": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-city-ops": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-lab-science": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-market-micro": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-multiplayer-game": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-autonomous-vehicle": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-multi-agent-ai": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-open-agent-world": {"final_outcome": "require_approval", "requires_warn": True},
        "adapter-digital-twin": {"final_outcome": "require_approval", "requires_warn": True},
    }

    for adapter_id, expectation in expectations.items():
        adapter = registry.get(adapter_id)
        scenario = adapter.scenario_dir(REPO_ROOT)
        proposal = load_json(scenario / "proposal.json")
        policy = load_json(adapter.default_policy_path(REPO_ROOT))
        report = policy_engine.evaluate_policies([policy], proposal)

        assert report.final_outcome == expectation["final_outcome"]
        assert report.requires_approval is (
            expectation["final_outcome"] == "require_approval"
        )
        if expectation["requires_warn"]:
            assert any(e.outcome == "warn" for e in report.evaluations)

    world_game_adapter = registry.maybe_get("adapter-world-game")
    if world_game_adapter is not None:
        world_game_policy = load_json(world_game_adapter.default_policy_path(REPO_ROOT))
        world_game_report = policy_engine.evaluate_policies(
            [world_game_policy],
            {
                "proposal_id": "proposal.world-game-modern.seed",
                "proposed_action": {
                    "action_type": "apply_world_game_intervention",
                    "parameters": {
                        "projected_composite_score": 40,
                        "projected_water_security_floor": 24,
                        "projected_equity_gap": 20,
                    },
                },
            },
        )
        assert world_game_report.final_outcome in {"allow", "warn", "require_approval", "deny"}
        assert world_game_report.final_outcome == "warn"


def test_adapter_examples_run_on_shared_kernel():
    registry = AdapterRegistry.with_defaults()

    for adapter in registry.list():
        store = InMemoryEventStore()
        scenario = adapter.scenario_dir(REPO_ROOT)
        events = load_json(scenario / "events.json")

        for index, event in enumerate(events):
            store.append("%s.stream.%d" % (adapter.adapter_id, index), event)

        replay = ReplayEngine(store, SimpleProjector)
        rebuilt = replay.rebuild("world_state", use_snapshot=False)

        assert rebuilt.source_event_offset == len(events) - 1
        assert rebuilt.state["events_processed"] == len(events)

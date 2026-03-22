import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = REPO_ROOT / "schemas"
EXAMPLES_DIR = REPO_ROOT / "examples"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def schemas_dir() -> Path:
    return SCHEMAS_DIR


@pytest.fixture
def examples_dir() -> Path:
    return EXAMPLES_DIR


@pytest.fixture
def top_level_example_paths(examples_dir: Path):
    return {
        "entity": examples_dir / "entity.example.json",
        "relationship": examples_dir / "relationship.example.json",
        "event": examples_dir / "event.example.json",
        "proposal": examples_dir / "proposal.example.json",
        "decision": examples_dir / "decision.example.json",
        "simulation": examples_dir / "simulation.example.json",
        "policy": examples_dir / "policy.example.json",
        "rule": examples_dir / "rule.example.json",
        "projection": examples_dir / "projection.example.json",
    }


@pytest.fixture
def supply_network_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "supply-network-mini"


@pytest.fixture
def air_traffic_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "air-traffic-mini"


@pytest.fixture
def world_game_mini_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "world-game-mini"


@pytest.fixture
def world_game_multi_region_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "world-game-multi-region"

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
def service_manifest_paths() -> dict[str, Path]:
    return {
        "reference_http": REPO_ROOT / "infra" / "service_manifests" / "reference-http.json",
        "world_runtime_local": REPO_ROOT / "infra" / "service_manifests" / "world-runtime.local.json",
        "reference_local_ai_extraction": REPO_ROOT
        / "infra"
        / "service_manifests"
        / "reference-local-ai-extraction.json",
    }


@pytest.fixture
def provider_binding_paths() -> dict[str, Path]:
    return {
        "reference_local_chat_economy": REPO_ROOT
        / "infra"
        / "provider_bindings"
        / "reference-local-chat-economy.json",
        "reference_local_structured_balanced": REPO_ROOT
        / "infra"
        / "provider_bindings"
        / "reference-local-structured-balanced.json",
        "reference_network_structured_premium": REPO_ROOT
        / "infra"
        / "provider_bindings"
        / "reference-network-structured-premium.json",
        "reference_local_structured_extraction_high": REPO_ROOT
        / "infra"
        / "provider_bindings"
        / "reference-local-structured-extraction-high.json",
        "reference_local_structured_extraction_balanced": REPO_ROOT
        / "infra"
        / "provider_bindings"
        / "reference-local-structured-extraction-balanced.json",
    }


@pytest.fixture
def task_profile_paths() -> dict[str, Path]:
    return {
        "assistant_chat_default": REPO_ROOT / "infra" / "task_profiles" / "assistant-chat.default.json",
        "structured_extraction_strict": REPO_ROOT
        / "infra"
        / "task_profiles"
        / "structured-extraction.strict.json",
        "structured_extraction_local_reference": REPO_ROOT
        / "infra"
        / "task_profiles"
        / "structured-extraction.local-reference.json",
    }


@pytest.fixture
def supply_network_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "supply-network-mini"


@pytest.fixture
def air_traffic_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "air-traffic-mini"


@pytest.fixture
def semantic_system_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "semantic-system-mini"


@pytest.fixture
def power_grid_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "power-grid-mini"


@pytest.fixture
def city_ops_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "city-ops-mini"


@pytest.fixture
def lab_science_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "lab-science-mini"


@pytest.fixture
def market_micro_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "market-micro-mini"


@pytest.fixture
def multiplayer_game_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "multiplayer-game-mini"


@pytest.fixture
def autonomous_vehicle_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "autonomous-vehicle-mini"


@pytest.fixture
def multi_agent_ai_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "multi-agent-ai-mini"


@pytest.fixture
def open_agent_world_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "open-agent-world-mini"


@pytest.fixture
def digital_twin_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "digital-twin-mini"


@pytest.fixture
def supply_ops_scenario_dir(examples_dir: Path) -> Path:
    return examples_dir / "scenarios" / "supply-ops-mini"


@pytest.fixture
def world_game_mini_scenario_dir(examples_dir: Path) -> Path:
    path = examples_dir / "scenarios" / "world-game-mini"
    if not path.exists():
        pytest.skip("world_game mini scenario is not present in this repo build")
    return path


@pytest.fixture
def world_game_multi_region_scenario_dir(examples_dir: Path) -> Path:
    path = examples_dir / "scenarios" / "world-game-multi-region"
    if not path.exists():
        pytest.skip("world_game multi-region scenario is not present in this repo build")
    return path

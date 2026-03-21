from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"
SCENARIOS_DIR = EXAMPLES_DIR / "scenarios"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    top_level = [
        "entity.example.json",
        "relationship.example.json",
        "event.example.json",
        "proposal.example.json",
        "decision.example.json",
        "simulation.example.json",
        "policy.example.json",
        "rule.example.json",
        "projection.example.json",
    ]

    print("Top-level fixtures:")
    for name in top_level:
        data = load_json(EXAMPLES_DIR / name)
        key = next((k for k in data.keys() if k.endswith("_id")), "(no id)")
        print(f"  - {name}: {key}={data.get(key)}")

    print("\nScenario bundles:")
    for scenario in sorted(SCENARIOS_DIR.iterdir()):
        if scenario.is_dir():
            entities = load_json(scenario / "entities.json")
            events = load_json(scenario / "events.json")
            print(f"  - {scenario.name}: entities={len(entities)} events={len(events)}")


if __name__ == "__main__":
    main()

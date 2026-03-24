import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.registry import AdapterRegistry
from adapters.public_program import (
    implemented_public_adapter_tracks,
    public_adapter_tracks,
    validate_public_package_checklist,
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    failed = False

    for track in public_adapter_tracks():
        package_errors = validate_public_package_checklist(track, REPO_ROOT)
        if package_errors:
            failed = True
            print("[FAIL] public-package %s" % track.adapter_id)
            for err in package_errors:
                print("  - %s" % err)
        else:
            print("[OK]   public-package %s" % track.adapter_id)

    registry = AdapterRegistry.with_defaults()
    registered_adapter_ids = {adapter.adapter_id for adapter in registry.list()}
    for track in implemented_public_adapter_tracks():
        if track.adapter_id not in registered_adapter_ids:
            failed = True
            print("[FAIL] public-registry %s missing from AdapterRegistry.with_defaults()" % track.adapter_id)

    for adapter in registry.list():
        scenario_dir = adapter.scenario_dir(REPO_ROOT)
        policy_path = adapter.default_policy_path(REPO_ROOT)

        entities = load_json(scenario_dir / "entities.json")
        events = load_json(scenario_dir / "events.json")

        entity_errors = adapter.validate_entities(entities)
        event_errors = adapter.validate_events(events)

        for schema_path in adapter.adapter_schema_paths(REPO_ROOT):
            if not schema_path.exists():
                failed = True
                print("[FAIL] %s missing schema: %s" % (adapter.adapter_id, schema_path))

        if not policy_path.exists():
            failed = True
            print("[FAIL] %s missing policy: %s" % (adapter.adapter_id, policy_path))

        if entity_errors or event_errors:
            failed = True
            print("[FAIL] %s" % adapter.adapter_id)
            for err in entity_errors + event_errors:
                print("  - %s" % err)
        else:
            print("[OK]   %s" % adapter.adapter_id)

    if failed:
        raise SystemExit(1)

    print("\nAdapter checks passed.")


if __name__ == "__main__":
    main()

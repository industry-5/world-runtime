from pathlib import Path
import json
import sys

from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = REPO_ROOT / "schemas"
EXAMPLES_DIR = REPO_ROOT / "examples"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_validator(schema_path: Path):
    schema = load_json(schema_path)
    store = {}
    for local_schema_path in SCHEMAS_DIR.glob("*.schema.json"):
        local_schema = load_json(local_schema_path)
        schema_id = local_schema.get("$id")
        if schema_id:
            store[schema_id] = local_schema

    resolver = RefResolver(
        base_uri=f"{SCHEMAS_DIR.as_uri()}/",
        referrer=schema,
        store=store,
    )
    return Draft202012Validator(schema, resolver=resolver)


def validate_one(schema_file: str, example_file: str) -> list[str]:
    validator = build_validator(SCHEMAS_DIR / schema_file)
    instance = load_json(EXAMPLES_DIR / example_file)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    return [str(e) for e in errors]


def main():
    pairs = [
        ("entity.schema.json", "entity.example.json"),
        ("relationship.schema.json", "relationship.example.json"),
        ("event.schema.json", "event.example.json"),
        ("proposal.schema.json", "proposal.example.json"),
        ("decision.schema.json", "decision.example.json"),
        ("simulation.schema.json", "simulation.example.json"),
        ("policy.schema.json", "policy.example.json"),
        ("rule.schema.json", "rule.example.json"),
        ("projection.schema.json", "projection.example.json"),
    ]

    failed = False

    for schema_file, example_file in pairs:
        errors = validate_one(schema_file, example_file)
        if errors:
            failed = True
            print(f"[FAIL] {example_file} vs {schema_file}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"[OK]   {example_file} vs {schema_file}")

    if failed:
        sys.exit(1)

    print("\nSchema validation passed.")


if __name__ == "__main__":
    main()

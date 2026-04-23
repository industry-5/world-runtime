from pathlib import Path
import json
import sys

from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = REPO_ROOT / "schemas"
EXAMPLES_DIR = REPO_ROOT / "examples"
INFRA_DIR = REPO_ROOT / "infra"


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


def validate_one(schema_file: str, instance_path: Path) -> list[str]:
    validator = build_validator(SCHEMAS_DIR / schema_file)
    instance = load_json(instance_path)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    return [str(e) for e in errors]


def main():
    pairs = [
        ("entity.schema.json", EXAMPLES_DIR / "entity.example.json"),
        ("relationship.schema.json", EXAMPLES_DIR / "relationship.example.json"),
        ("event.schema.json", EXAMPLES_DIR / "event.example.json"),
        ("proposal.schema.json", EXAMPLES_DIR / "proposal.example.json"),
        ("decision.schema.json", EXAMPLES_DIR / "decision.example.json"),
        ("simulation.schema.json", EXAMPLES_DIR / "simulation.example.json"),
        ("policy.schema.json", EXAMPLES_DIR / "policy.example.json"),
        ("rule.schema.json", EXAMPLES_DIR / "rule.example.json"),
        ("projection.schema.json", EXAMPLES_DIR / "projection.example.json"),
        ("service_manifest.schema.json", INFRA_DIR / "service_manifests" / "reference-http.json"),
        ("service_manifest.schema.json", INFRA_DIR / "service_manifests" / "world-runtime.local.json"),
        (
            "provider_binding.schema.json",
            INFRA_DIR / "provider_bindings" / "reference-local-chat-economy.json",
        ),
        (
            "provider_binding.schema.json",
            INFRA_DIR / "provider_bindings" / "reference-local-structured-balanced.json",
        ),
        (
            "provider_binding.schema.json",
            INFRA_DIR / "provider_bindings" / "reference-network-structured-premium.json",
        ),
        ("task_profile.schema.json", INFRA_DIR / "task_profiles" / "assistant-chat.default.json"),
        ("task_profile.schema.json", INFRA_DIR / "task_profiles" / "structured-extraction.strict.json"),
    ]

    failed = False

    for schema_file, instance_path in pairs:
        errors = validate_one(schema_file, instance_path)
        if errors:
            failed = True
            print(f"[FAIL] {instance_path.relative_to(REPO_ROOT)} vs {schema_file}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"[OK]   {instance_path.relative_to(REPO_ROOT)} vs {schema_file}")

    if failed:
        sys.exit(1)

    print("\nSchema validation passed.")


if __name__ == "__main__":
    main()

from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, RefResolver

from conftest import load_json


def build_validator(schema_path: Path, schemas_dir: Path):
    schema = load_json(schema_path)
    store = {}
    for local_schema_path in schemas_dir.glob("*.schema.json"):
        local_schema = load_json(local_schema_path)
        schema_id = local_schema.get("$id")
        if schema_id:
            store[schema_id] = local_schema

    resolver = RefResolver(
        base_uri=f"{schemas_dir.as_uri()}/",
        referrer=schema,
        store=store,
    )
    return Draft202012Validator(schema, resolver=resolver)


@pytest.mark.parametrize(
    "schema_file, example_key",
    [
        ("entity.schema.json", "entity"),
        ("relationship.schema.json", "relationship"),
        ("event.schema.json", "event"),
        ("proposal.schema.json", "proposal"),
        ("decision.schema.json", "decision"),
        ("simulation.schema.json", "simulation"),
        ("policy.schema.json", "policy"),
        ("rule.schema.json", "rule"),
        ("projection.schema.json", "projection"),
    ],
)
def test_top_level_example_validates(schema_file, example_key, schemas_dir, top_level_example_paths):
    validator = build_validator(schemas_dir / schema_file, schemas_dir)
    instance = load_json(top_level_example_paths[example_key])
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    assert errors == [], "\n".join(str(e) for e in errors)

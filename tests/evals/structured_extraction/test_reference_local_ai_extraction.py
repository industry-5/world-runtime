import json
from pathlib import Path

from jsonschema import Draft202012Validator

from core.reference_local_ai_extraction import evaluate_extraction, extract_character_card


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_DIR = REPO_ROOT / "examples" / "evals" / "structured_extraction" / "fixtures"
SCHEMA_PATH = REPO_ROOT / "examples" / "evals" / "structured_extraction" / "reference.character-card.schema.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_reference_local_ai_extraction_matches_complete_fixture():
    schema = _load_json(SCHEMA_PATH)
    document_text = (FIXTURES_DIR / "character_complete.txt").read_text(encoding="utf-8")
    expected = _load_json(FIXTURES_DIR / "character_complete.expected.json")

    output = extract_character_card(document_text, source_id=expected["source_id"])
    validator = Draft202012Validator(schema)

    assert sorted(validator.iter_errors(output), key=lambda item: list(item.path)) == []
    assert output == expected


def test_reference_local_ai_extraction_handles_ambiguous_inputs_with_schema_valid_output():
    schema = _load_json(SCHEMA_PATH)
    document_text = (FIXTURES_DIR / "character_ambiguous.txt").read_text(encoding="utf-8")
    expected = _load_json(FIXTURES_DIR / "character_ambiguous.expected.json")

    output = extract_character_card(document_text, source_id=expected["source_id"])
    diagnostics = evaluate_extraction(output, schema)

    assert diagnostics["schema_valid"] is True
    assert diagnostics["field_completeness"] >= 0.25
    assert output == expected

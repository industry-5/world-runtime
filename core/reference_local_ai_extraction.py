from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator


FIELD_PATTERNS = {
    "name": re.compile(r"^\s*Name\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE),
    "role": re.compile(r"^\s*Role\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE),
    "affiliation": re.compile(r"^\s*Affiliation\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE),
    "origin_world": re.compile(r"^\s*Origin World\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE),
    "artifacts": re.compile(r"^\s*Artifacts\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE),
    "risk_flags": re.compile(r"^\s*Risk Flags\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE),
    "open_questions": re.compile(r"^\s*Open Questions\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE),
}

UNCERTAIN_MARKERS = (
    "?",
    "unknown",
    "unclear",
    "unspecified",
    "possibly",
    "maybe",
)
EMPTY_MARKERS = {
    "",
    "none",
    "none noted",
    "none recorded",
    "n/a",
    "na",
}
NULL_AMBIGUOUS_MARKERS = {
    "unknown",
    "unclear",
    "unspecified",
}


@dataclass(frozen=True)
class ExtractionDiagnostics:
    missing_required_fields: List[str]
    ambiguous_fields: List[str]
    field_completeness: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "missing_required_fields": list(self.missing_required_fields),
            "ambiguous_fields": list(self.ambiguous_fields),
            "field_completeness": self.field_completeness,
        }


def extract_character_card(document_text: str, *, source_id: str) -> Dict[str, Any]:
    name = _extract_scalar("name", document_text, required=True)
    role = _extract_scalar("role", document_text)
    affiliation = _extract_scalar("affiliation", document_text)
    origin_world = _extract_scalar("origin_world", document_text)
    artifacts = _extract_list("artifacts", document_text)
    risk_flags = _extract_list("risk_flags", document_text)
    open_questions = _extract_list("open_questions", document_text)

    ambiguities: List[str] = []
    if role.ambiguous:
        ambiguities.append("role is uncertain")
    if affiliation.ambiguous:
        ambiguities.append("affiliation is uncertain")
    if origin_world.ambiguous:
        ambiguities.append("origin_world is uncertain")
    if not role.value:
        open_questions.append("role not confidently established")
    if not affiliation.value:
        open_questions.append("affiliation not confidently established")
    if not origin_world.value:
        open_questions.append("origin_world not confidently established")

    return {
        "schema_id": "reference.character-card.v1",
        "source_id": source_id,
        "record_type": "character_card",
        "character": {
            "name": name.value or "unknown",
            "role": role.value,
            "affiliation": affiliation.value,
            "origin_world": origin_world.value,
        },
        "artifacts": artifacts,
        "risk_flags": risk_flags,
        "open_questions": sorted(set(open_questions)),
        "ambiguities": sorted(set(ambiguities)),
    }


def evaluate_extraction(payload: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
    diagnostics = extraction_diagnostics(payload)
    return {
        "schema_valid": not errors,
        "schema_errors": [error.message for error in errors],
        **diagnostics.as_dict(),
    }


def extraction_diagnostics(payload: Dict[str, Any]) -> ExtractionDiagnostics:
    character = dict(payload.get("character", {}))
    required_scalar_fields = ("name", "role", "affiliation", "origin_world")
    missing = [field for field in required_scalar_fields if not character.get(field)]
    ambiguous_fields = []

    ambiguities = {
        str(item).strip().lower()
        for item in payload.get("ambiguities", [])
        if str(item).strip()
    }
    for field in ("role", "affiliation", "origin_world"):
        if "%s is uncertain" % field in ambiguities:
            ambiguous_fields.append(field)

    total_fields = len(required_scalar_fields)
    populated = total_fields - len(missing)
    completeness = round(populated / total_fields, 4) if total_fields else 1.0
    return ExtractionDiagnostics(
        missing_required_fields=missing,
        ambiguous_fields=ambiguous_fields,
        field_completeness=completeness,
    )


@dataclass(frozen=True)
class _ScalarField:
    value: Optional[str]
    ambiguous: bool = False


def _extract_scalar(field_name: str, document_text: str, *, required: bool = False) -> _ScalarField:
    pattern = FIELD_PATTERNS[field_name]
    match = pattern.search(document_text)
    if match is None:
        return _ScalarField(value=None, ambiguous=required)

    raw = _normalize_whitespace(match.group(1))
    lowered = raw.lower()
    if lowered in EMPTY_MARKERS:
        return _ScalarField(value=None, ambiguous=False)
    if lowered in NULL_AMBIGUOUS_MARKERS:
        return _ScalarField(value=None, ambiguous=True)

    ambiguous = any(marker in lowered for marker in UNCERTAIN_MARKERS)
    cleaned = raw.replace("?", "").strip()
    if lowered.startswith("possibly "):
        cleaned = cleaned[len("possibly ") :].strip()
    if lowered.startswith("maybe "):
        cleaned = cleaned[len("maybe ") :].strip()

    if not cleaned:
        return _ScalarField(value=None, ambiguous=ambiguous)
    return _ScalarField(value=cleaned, ambiguous=ambiguous)


def _extract_list(field_name: str, document_text: str) -> List[str]:
    pattern = FIELD_PATTERNS[field_name]
    match = pattern.search(document_text)
    if match is None:
        return []

    raw = _normalize_whitespace(match.group(1))
    lowered = raw.lower()
    if lowered in EMPTY_MARKERS:
        return []

    normalized = raw.replace("/", ";")
    items = []
    for chunk in normalized.split(";"):
        for item in chunk.split(","):
            cleaned = item.replace("?", "").strip()
            if cleaned and cleaned.lower() not in EMPTY_MARKERS:
                items.append(cleaned)
    return sorted(set(items))


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.strip().split())

import hashlib
import json
from copy import deepcopy
from typing import Any, Dict, List, Optional, Set, Tuple

REDACTION_TOKEN = "[REDACTED]"
DEFAULT_SENSITIVE_FIELD_TOKENS = {
    "api_key",
    "authorization",
    "password",
    "secret",
    "secret_access_key",
    "token",
}


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_fingerprint(payload: Any) -> str:
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return "sha256:%s" % digest


def normalize_evidence_ref(
    evidence_type: str,
    ref_id: str,
    summary: str,
    stage: str,
    attributes: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = {
        "evidence_type": str(evidence_type),
        "ref_id": str(ref_id),
        "summary": str(summary),
        "stage": str(stage),
    }
    if attributes:
        payload["attributes"] = deepcopy(attributes)
    return payload


def redact_sensitive_payload(
    payload: Any,
    sensitive_field_tokens: Optional[Set[str]] = None,
    redaction_token: str = REDACTION_TOKEN,
) -> Tuple[Any, Dict[str, Any]]:
    tokens = {item.lower() for item in (sensitive_field_tokens or DEFAULT_SENSITIVE_FIELD_TOKENS)}
    redacted_paths: List[str] = []
    redacted_fields: Set[str] = set()

    def _visit(value: Any, path: str) -> Any:
        if isinstance(value, dict):
            sanitized: Dict[str, Any] = {}
            for key, item in value.items():
                lowered = str(key).lower()
                child_path = "%s.%s" % (path, key) if path else str(key)
                if any(token in lowered for token in tokens):
                    sanitized[key] = redaction_token
                    redacted_paths.append(child_path)
                    redacted_fields.add(str(key))
                    continue
                sanitized[key] = _visit(item, child_path)
            return sanitized
        if isinstance(value, list):
            return [_visit(item, "%s[%d]" % (path, index)) for index, item in enumerate(value)]
        return deepcopy(value)

    sanitized = _visit(payload, "")
    report = {
        "redacted": bool(redacted_paths),
        "redaction_token": redaction_token,
        "redacted_field_names": sorted(redacted_fields),
        "redacted_paths": sorted(redacted_paths),
        "redaction_rule_tokens": sorted(tokens),
    }
    return sanitized, report

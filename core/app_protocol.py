from typing import Any, Dict, Optional, Tuple

PROTOCOL_VERSION = "1.0"
COMPATIBILITY_POLICY = "major-compatible"


def protocol_major(version: str) -> str:
    return version.split(".", 1)[0]


def is_compatible(client_version: str, server_version: str = PROTOCOL_VERSION) -> bool:
    return protocol_major(client_version) == protocol_major(server_version)


def validate_request_envelope(message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    if not isinstance(message, dict):
        return False, "request must be an object"

    required = ["protocol_version", "id", "method"]
    for field in required:
        if field not in message:
            return False, "missing required field: %s" % field

    if not isinstance(message.get("protocol_version"), str):
        return False, "protocol_version must be a string"

    if not isinstance(message.get("method"), str) or not message.get("method"):
        return False, "method must be a non-empty string"

    if "params" in message and not isinstance(message.get("params"), dict):
        return False, "params must be an object"

    return True, None


def build_response_envelope(
    request_id: Any,
    result: Dict[str, Any],
    protocol_version: str = PROTOCOL_VERSION,
) -> Dict[str, Any]:
    return {
        "wire_type": "response",
        "protocol_version": protocol_version,
        "compatibility": {
            "policy": COMPATIBILITY_POLICY,
            "server_version": PROTOCOL_VERSION,
        },
        "id": request_id,
        "ok": True,
        "result": result,
    }


def build_error_envelope(
    request_id: Any,
    code: str,
    message: str,
    protocol_version: str = PROTOCOL_VERSION,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = {
        "wire_type": "response",
        "protocol_version": protocol_version,
        "compatibility": {
            "policy": COMPATIBILITY_POLICY,
            "server_version": PROTOCOL_VERSION,
        },
        "id": request_id,
        "ok": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload


def build_notification(
    method: str,
    params: Dict[str, Any],
    protocol_version: str = PROTOCOL_VERSION,
) -> Dict[str, Any]:
    return {
        "wire_type": "notification",
        "protocol_version": protocol_version,
        "method": method,
        "params": params,
    }

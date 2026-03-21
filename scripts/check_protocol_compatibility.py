import json
import re
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.app_protocol import COMPATIBILITY_POLICY, PROTOCOL_VERSION

SCHEMAS_DIR = REPO_ROOT / "schemas"
PROTOCOL_DOC = REPO_ROOT / "APP_SERVER_PROTOCOL.md"

SCHEMA_EXPECTATIONS = {
    "app_server.request.schema.json": {
        "required": {"protocol_version", "id", "method"},
        "wire_const": "request",
    },
    "app_server.response.schema.json": {
        "required": {"wire_type", "protocol_version", "compatibility", "id", "ok"},
        "wire_const": "response",
    },
    "app_server.notification.schema.json": {
        "required": {"wire_type", "protocol_version", "method", "params"},
        "wire_const": "notification",
    },
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_schema_shape(schema_name: str, expectation: dict) -> list[str]:
    errors = []
    path = SCHEMAS_DIR / schema_name
    if not path.exists():
        return [f"missing schema file: {schema_name}"]

    schema = load_json(path)
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    expected_required = expectation["required"]

    missing_required = sorted(expected_required - required)
    if missing_required:
        errors.append(f"{schema_name}: missing required fields {missing_required}")

    wire_const = properties.get("wire_type", {}).get("const")
    if wire_const != expectation["wire_const"]:
        errors.append(
            f"{schema_name}: wire_type const mismatch "
            f"(expected {expectation['wire_const']}, got {wire_const})"
        )

    protocol_pattern = properties.get("protocol_version", {}).get("pattern")
    if protocol_pattern != r"^[0-9]+\.[0-9]+$":
        errors.append(
            f"{schema_name}: protocol_version pattern mismatch "
            f"(expected ^[0-9]+\\.[0-9]+$, got {protocol_pattern})"
        )

    return errors


def check_protocol_doc() -> list[str]:
    if not PROTOCOL_DOC.exists():
        return ["missing APP_SERVER_PROTOCOL.md"]

    text = PROTOCOL_DOC.read_text(encoding="utf-8")
    errors = []

    expected_version_line = f"Server protocol version: `{PROTOCOL_VERSION}`"
    if expected_version_line not in text:
        errors.append(
            "APP_SERVER_PROTOCOL.md missing server protocol version line for "
            f"{PROTOCOL_VERSION}"
        )

    expected_policy_line = f"Policy: **{COMPATIBILITY_POLICY}**"
    if expected_policy_line not in text:
        errors.append(
            "APP_SERVER_PROTOCOL.md missing compatibility policy line for "
            f"{COMPATIBILITY_POLICY}"
        )

    if not re.match(r"^[0-9]+\.[0-9]+$", PROTOCOL_VERSION):
        errors.append(f"invalid core.app_protocol.PROTOCOL_VERSION format: {PROTOCOL_VERSION}")

    return errors


def run_checks() -> list[str]:
    errors = []
    for schema_name, expectation in SCHEMA_EXPECTATIONS.items():
        errors.extend(check_schema_shape(schema_name, expectation))
    errors.extend(check_protocol_doc())
    return errors


def main() -> int:
    errors = run_checks()
    if errors:
        print("Protocol compatibility check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    print("Protocol compatibility check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import inspect
from pathlib import Path
import sys
from typing import Any, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.base import DomainAdapter
from core.connector_transports import TransportPlugin

REQUIRED_DOCS = [
    REPO_ROOT / "docs" / "EXTENSION_CONTRACTS.md",
    REPO_ROOT / "docs" / "PARTNER_ONBOARDING.md",
    REPO_ROOT / "docs" / "COMPATIBILITY_MATRIX.md",
    REPO_ROOT / "playbooks" / "partner-onboarding.md",
]

REQUIRED_TEMPLATE_FILES = [
    REPO_ROOT / "templates" / "adapter_starter" / "adapter.py",
    REPO_ROOT / "templates" / "adapter_starter" / "policies" / "default_policy.json",
    REPO_ROOT / "templates" / "adapter_starter" / "schemas" / "entity_types.schema.json",
    REPO_ROOT / "templates" / "adapter_starter" / "schemas" / "event_types.schema.json",
    REPO_ROOT / "templates" / "connector_plugin_starter" / "plugin.py",
]

REQUIRED_ADAPTER_MEMBERS = {
    "adapter_id",
    "domain_name",
    "entity_types",
    "event_types",
    "scenario_dir",
    "default_policy_path",
    "adapter_schema_paths",
}

REQUIRED_TRANSPORT_METHODS = ["send"]



def _has_required_protocol_fields(protocol: Any) -> bool:
    annotations = getattr(protocol, "__annotations__", {})
    if "provider" not in annotations:
        return False

    send = getattr(protocol, "send", None)
    if send is None:
        return False
    signature = inspect.signature(send)
    return list(signature.parameters.keys()) == ["self", "payload", "attempt", "auth", "options"]


def main() -> int:
    errors: List[str] = []

    for path in REQUIRED_DOCS:
        if not path.exists():
            errors.append(f"missing documentation file: {path.relative_to(REPO_ROOT)}")

    for path in REQUIRED_TEMPLATE_FILES:
        if not path.exists():
            errors.append(f"missing template file: {path.relative_to(REPO_ROOT)}")

    abstract_methods = getattr(DomainAdapter, "__abstractmethods__", set())
    missing_adapter_members = sorted(REQUIRED_ADAPTER_MEMBERS - set(abstract_methods))
    if missing_adapter_members:
        errors.append("DomainAdapter missing abstract members: " + ", ".join(missing_adapter_members))

    if not _has_required_protocol_fields(TransportPlugin):
        errors.append(
            "TransportPlugin contract changed; expected provider attribute and send(self, payload, attempt, auth, options)."
        )

    if errors:
        print("Extension contract check failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Extension contract check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

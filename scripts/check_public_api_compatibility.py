import inspect
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from api.runtime_api import API_VERSION, PUBLIC_ENDPOINTS
from world_runtime.sdk import DEFAULT_API_VERSION, WorldRuntimeSDKClient

PUBLIC_API_DOC = REPO_ROOT / "api" / "PUBLIC_API_V1.md"
SDK_DOC = REPO_ROOT / "sdk" / "README.md"
CONSUMER_DOC = REPO_ROOT / "docs" / "CONSUMER_INTEGRATION.md"

REQUIRED_SDK_METHODS = {
    "create_session",
    "runtime_inventory",
    "list_runtime_services",
    "get_runtime_service",
    "reconcile_runtime_services",
    "list_runtime_providers",
    "get_runtime_provider",
    "resolve_runtime_task",
    "submit_proposal",
    "run_simulation",
    "respond_approval",
    "run_connector_inbound",
    "run_connector_outbound",
    "telemetry_summary",
    "call_runtime",
}


def check_docs() -> list[str]:
    errors: list[str] = []
    if not PUBLIC_API_DOC.exists():
        return ["missing api/PUBLIC_API_V1.md"]

    text = PUBLIC_API_DOC.read_text(encoding="utf-8")
    if "Public API version: `%s`" % API_VERSION not in text:
        errors.append("api/PUBLIC_API_V1.md missing expected API version line")

    for endpoint in PUBLIC_ENDPOINTS.values():
        if endpoint not in text:
            errors.append("api/PUBLIC_API_V1.md missing endpoint %s" % endpoint)

    if not SDK_DOC.exists():
        errors.append("missing sdk/README.md")
    elif "from world_runtime.sdk import WorldRuntimeSDKClient" not in SDK_DOC.read_text(encoding="utf-8"):
        errors.append("sdk/README.md missing supported world_runtime.sdk import example")

    if "python -m world_runtime serve --profile local" not in text:
        errors.append("api/PUBLIC_API_V1.md missing supported module serve entrypoint")

    if not CONSUMER_DOC.exists():
        errors.append("missing docs/CONSUMER_INTEGRATION.md")

    return errors


def check_sdk_surface() -> list[str]:
    errors: list[str] = []
    if DEFAULT_API_VERSION != API_VERSION:
        errors.append(
            "SDK/API version mismatch: sdk=%s api=%s" % (DEFAULT_API_VERSION, API_VERSION)
        )

    methods = {
        name
        for name, member in inspect.getmembers(WorldRuntimeSDKClient)
        if callable(member) and not name.startswith("_")
    }
    for method_name in sorted(REQUIRED_SDK_METHODS):
        if method_name not in methods:
            errors.append("WorldRuntimeSDKClient missing method: %s" % method_name)

    return errors


def run_checks() -> list[str]:
    errors: list[str] = []
    errors.extend(check_docs())
    errors.extend(check_sdk_surface())
    return errors


def main() -> int:
    errors = run_checks()
    if errors:
        print("Public API compatibility check failed:")
        for item in errors:
            print("  - %s" % item)
        return 1

    print("Public API compatibility check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

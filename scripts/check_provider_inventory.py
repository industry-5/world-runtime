import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.provider_registry import ProviderRegistryLoader
from core.task_profiles import TaskProfileLoader


def _load_service_manifest_ids(service_manifest_dir: Path) -> list[str]:
    service_ids: list[str] = []
    for manifest_path in sorted(service_manifest_dir.glob("*.json")):
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        service_id = str(payload.get("service_id", "")).strip()
        if service_id:
            service_ids.append(service_id)
    return sorted(set(service_ids))


def main() -> int:
    provider_registry = ProviderRegistryLoader(REPO_ROOT).load_all()
    task_catalog = TaskProfileLoader(REPO_ROOT).load_all()
    service_manifest_ids = _load_service_manifest_ids(REPO_ROOT / "infra" / "service_manifests")

    errors: list[str] = []
    providers = []

    for binding in provider_registry.bindings():
        missing_services = sorted(set(binding.service_dependency_ids) - set(service_manifest_ids))
        if missing_services:
            errors.append(
                "provider %s references unknown service dependencies: %s"
                % (binding.provider_id, ", ".join(missing_services))
            )
        providers.append(binding.as_dict())

    payload = {
        "milestone": "M28",
        "gate": "provider-inventory",
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "service_manifest_ids": service_manifest_ids,
        "providers": providers,
        "task_profiles": [profile.as_dict() for profile in task_catalog.profiles()],
    }

    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

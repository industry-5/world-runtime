import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.migrations import apply_sqlite_migrations
from core.deployment import DeploymentLoader


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply persistence migrations for a deployment profile")
    parser.add_argument("--profile", choices=["local", "dev"], default="local")
    args = parser.parse_args()

    loader = DeploymentLoader(REPO_ROOT)
    profile = loader.load_profile(args.profile)
    config = loader.load_persistence_config(profile)

    if config.get("event_store") != "sqlite":
        print("No sqlite migrations required for event_store=%s" % config.get("event_store"))
        return

    database_path = Path(config["database_path"])
    if not database_path.is_absolute():
        database_path = REPO_ROOT / database_path

    migrations_dir = REPO_ROOT / "infra" / "migrations" / "persistence"
    result = apply_sqlite_migrations(database_path, migrations_dir)
    print("Applied:", ", ".join(result["applied"]) if result["applied"] else "none")
    print("Skipped:", ", ".join(result["skipped"]) if result["skipped"] else "none")


if __name__ == "__main__":
    main()

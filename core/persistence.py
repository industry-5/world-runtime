import tempfile
from pathlib import Path
from typing import Any, Dict

from core.event_store import InMemoryEventStore
from core.path_utils import is_repo_relative, resolve_writable_repo_path
from core.sqlite_event_store import SQLiteEventStore


def build_event_store_from_config(repo_root: Path, persistence_config: Dict[str, Any]):
    event_store = persistence_config.get("event_store", "in_memory")

    if event_store == "in_memory":
        return InMemoryEventStore()

    if event_store == "sqlite":
        database_path = persistence_config.get("database_path")
        if not database_path:
            raise ValueError("database_path is required for sqlite event_store")
        original_db_path = Path(database_path)
        db_path = resolve_writable_repo_path(repo_root, original_db_path)

        if persistence_config.get("reset_on_bootstrap"):
            if not is_repo_relative(db_path, repo_root):
                unique_dir = Path(tempfile.mkdtemp(prefix="world-runtime-db-"))
                db_path = unique_dir / original_db_path.name
            elif db_path.exists():
                db_path.unlink()

        migrations_dir = repo_root / "infra" / "migrations" / "persistence"
        return SQLiteEventStore(database_path=db_path, migrations_dir=migrations_dir)

    raise ValueError("unsupported event_store: %s" % event_store)

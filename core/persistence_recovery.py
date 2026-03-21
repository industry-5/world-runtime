import sqlite3
from pathlib import Path
from typing import Dict


def backup_sqlite_database(database_path: Path, backup_path: Path) -> Dict[str, int]:
    source_path = Path(database_path)
    destination_path = Path(backup_path)

    if not source_path.exists():
        raise ValueError("database file not found: %s" % source_path)

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    if destination_path.exists():
        destination_path.unlink()

    with sqlite3.connect(str(source_path)) as source:
        with sqlite3.connect(str(destination_path)) as destination:
            source.backup(destination)

    return {
        "bytes": destination_path.stat().st_size,
    }


def restore_sqlite_database(backup_path: Path, database_path: Path) -> Dict[str, int]:
    source_path = Path(backup_path)
    destination_path = Path(database_path)

    if not source_path.exists():
        raise ValueError("backup file not found: %s" % source_path)

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    if destination_path.exists():
        destination_path.unlink()

    with sqlite3.connect(str(source_path)) as source:
        with sqlite3.connect(str(destination_path)) as destination:
            source.backup(destination)

    return {
        "bytes": destination_path.stat().st_size,
    }


def sqlite_table_counts(database_path: Path) -> Dict[str, int]:
    path = Path(database_path)
    if not path.exists():
        raise ValueError("database file not found: %s" % path)

    table_names = [
        "events",
        "snapshots",
        "connector_idempotency",
        "connector_dead_letters",
        "connector_policy_decisions",
        "schema_migrations",
    ]

    counts: Dict[str, int] = {}
    with sqlite3.connect(str(path)) as conn:
        for table_name in table_names:
            row = conn.execute("SELECT COUNT(*) FROM %s" % table_name).fetchone()
            counts[table_name] = int(row[0]) if row is not None else 0

    return counts

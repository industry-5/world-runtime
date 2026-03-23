import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_sqlite_migrations(database_path: Path, migrations_dir: Path) -> Dict[str, List[str]]:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    migrations_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(database_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
          version TEXT PRIMARY KEY,
          checksum TEXT NOT NULL,
          applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )

    rows = conn.execute("SELECT version, checksum FROM schema_migrations").fetchall()
    applied = {row[0]: row[1] for row in rows}

    applied_now = []
    skipped = []

    migration_files = sorted(migrations_dir.glob("*.sql"))
    for migration_path in migration_files:
        version = migration_path.name
        sql_text = migration_path.read_text(encoding="utf-8")
        checksum = _sha256(sql_text)

        existing = applied.get(version)
        if existing is not None:
            if existing != checksum:
                conn.close()
                raise ValueError(
                    "migration checksum mismatch for %s" % version
                )
            skipped.append(version)
            continue

        conn.executescript(sql_text)
        conn.execute(
            "INSERT INTO schema_migrations(version, checksum) VALUES(?, ?)",
            (version, checksum),
        )
        conn.commit()
        applied_now.append(version)

    conn.close()
    return {"applied": applied_now, "skipped": skipped}

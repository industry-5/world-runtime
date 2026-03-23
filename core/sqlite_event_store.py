import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.migrations import apply_sqlite_migrations


class SQLiteEventStore:
    def __init__(self, database_path: Path, migrations_dir: Optional[Path] = None) -> None:
        self.database_path = Path(database_path)
        self.migrations_dir = migrations_dir or (
            Path(__file__).resolve().parents[1] / "infra" / "migrations" / "persistence"
        )
        apply_sqlite_migrations(self.database_path, self.migrations_dir)

    def append(
        self,
        stream_id: str,
        event: dict,
        expected_sequence: Optional[int] = None,
    ) -> dict:
        with self._connect() as conn:
            next_offset = self._next_offset(conn)
            next_sequence = self._next_sequence(conn, stream_id)

            if expected_sequence is not None and expected_sequence != next_sequence:
                raise ValueError(
                    "sequence_conflict: expected %d got %d"
                    % (expected_sequence, next_sequence)
                )

            event_record = dict(event)
            event_record["stream_id"] = stream_id
            event_record["offset"] = next_offset
            if "sequence" not in event_record:
                event_record["sequence"] = next_sequence

            conn.execute(
                """
                INSERT INTO events(offset, stream_id, sequence, event_json)
                VALUES(?, ?, ?, ?)
                """,
                (
                    next_offset,
                    stream_id,
                    event_record["sequence"],
                    json.dumps(event_record, separators=(",", ":")),
                ),
            )
            conn.commit()
        return dict(event_record)

    def read_stream(self, stream_id: str) -> List[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT event_json FROM events WHERE stream_id = ? ORDER BY offset ASC",
                (stream_id,),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def all_events(self) -> List[dict]:
        return self.read_all()

    def read_all(self, from_offset: int = 0, to_offset: Optional[int] = None) -> List[dict]:
        if from_offset < 0:
            from_offset = 0

        with self._connect() as conn:
            if to_offset is None:
                rows = conn.execute(
                    "SELECT event_json FROM events WHERE offset >= ? ORDER BY offset ASC",
                    (from_offset,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT event_json
                    FROM events
                    WHERE offset >= ? AND offset <= ?
                    ORDER BY offset ASC
                    """,
                    (from_offset, to_offset),
                ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def last_offset(self) -> Optional[int]:
        with self._connect() as conn:
            row = conn.execute("SELECT MAX(offset) FROM events").fetchone()
        if row is None or row[0] is None:
            return None
        return int(row[0])

    def create_snapshot(
        self,
        projection_name: str,
        source_event_offset: int,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> dict:
        snapshot = {
            "projection_name": projection_name,
            "source_event_offset": source_event_offset,
            "state": state,
            "metadata": metadata or {},
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO snapshots(projection_name, source_event_offset, state_json, metadata_json)
                VALUES(?, ?, ?, ?)
                """,
                (
                    projection_name,
                    source_event_offset,
                    json.dumps(state, separators=(",", ":")),
                    json.dumps(snapshot["metadata"], separators=(",", ":")),
                ),
            )
            conn.commit()
        return snapshot

    def latest_snapshot(self, projection_name: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT projection_name, source_event_offset, state_json, metadata_json
                FROM snapshots
                WHERE projection_name = ?
                ORDER BY source_event_offset DESC, id DESC
                LIMIT 1
                """,
                (projection_name,),
            ).fetchone()
        return self._snapshot_row_to_dict(row)

    def latest_snapshot_at_or_before(
        self,
        projection_name: str,
        offset: int,
    ) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT projection_name, source_event_offset, state_json, metadata_json
                FROM snapshots
                WHERE projection_name = ? AND source_event_offset <= ?
                ORDER BY source_event_offset DESC, id DESC
                LIMIT 1
                """,
                (projection_name, offset),
            ).fetchone()
        return self._snapshot_row_to_dict(row)

    def _snapshot_row_to_dict(self, row: Optional[sqlite3.Row]) -> Optional[dict]:
        if row is None:
            return None
        return {
            "projection_name": row[0],
            "source_event_offset": int(row[1]),
            "state": json.loads(row[2]),
            "metadata": json.loads(row[3]) if row[3] else {},
        }

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.database_path))
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _next_offset(self, conn: sqlite3.Connection) -> int:
        row = conn.execute("SELECT MAX(offset) FROM events").fetchone()
        if row is None or row[0] is None:
            return 0
        return int(row[0]) + 1

    def _next_sequence(self, conn: sqlite3.Connection, stream_id: str) -> int:
        row = conn.execute(
            "SELECT MAX(sequence) FROM events WHERE stream_id = ?",
            (stream_id,),
        ).fetchone()
        if row is None or row[0] is None:
            return 0
        return int(row[0]) + 1

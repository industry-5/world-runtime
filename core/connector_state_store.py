import json
import sqlite3
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.migrations import apply_sqlite_migrations


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class DeadLetterRecord:
    dead_letter_id: str
    connector_id: str
    direction: str
    idempotency_key: str
    reason: str
    payload: Dict[str, Any]
    attempts: int
    last_error: str
    created_at: str
    replay_status: Optional[str] = None
    replayed_at: Optional[str] = None
    replay_result: Optional[Dict[str, Any]] = None


@dataclass
class ConnectorPolicyDecisionRecord:
    decision_id: str
    connector_id: str
    direction: str
    idempotency_key: str
    final_outcome: str
    status: str
    policy_report: Dict[str, Any]
    created_at: str
    provider: Optional[str] = None
    source: Optional[str] = None
    approval_id: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None


class BaseConnectorStateStore:
    def get_idempotency(self, key: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def put_idempotency(self, key: str, direction: str, connector_id: str, result: Dict[str, Any]) -> None:
        raise NotImplementedError

    def append_dead_letter(self, record: DeadLetterRecord) -> None:
        raise NotImplementedError

    def list_dead_letters(
        self,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_dead_letter(self, dead_letter_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def mark_dead_letter_replay(
        self,
        dead_letter_id: str,
        replay_status: str,
        replay_result: Dict[str, Any],
    ) -> None:
        raise NotImplementedError

    def append_policy_decision(self, record: ConnectorPolicyDecisionRecord) -> None:
        raise NotImplementedError

    def list_policy_decisions(
        self,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_policy_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class InMemoryConnectorStateStore(BaseConnectorStateStore):
    def __init__(self) -> None:
        self._idempotency: Dict[str, Dict[str, Any]] = {}
        self._dead_letters: List[DeadLetterRecord] = []
        self._policy_decisions: List[ConnectorPolicyDecisionRecord] = []

    def get_idempotency(self, key: str) -> Optional[Dict[str, Any]]:
        payload = self._idempotency.get(key)
        if payload is None:
            return None
        return deepcopy(payload)

    def put_idempotency(self, key: str, direction: str, connector_id: str, result: Dict[str, Any]) -> None:
        self._idempotency[key] = deepcopy(result)

    def append_dead_letter(self, record: DeadLetterRecord) -> None:
        self._dead_letters.append(record)

    def list_dead_letters(
        self,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for entry in self._dead_letters:
            if connector_id and entry.connector_id != connector_id:
                continue
            if direction and entry.direction != direction:
                continue
            rows.append(_record_to_payload(entry))
        return rows

    def get_dead_letter(self, dead_letter_id: str) -> Optional[Dict[str, Any]]:
        for entry in self._dead_letters:
            if entry.dead_letter_id == dead_letter_id:
                return _record_to_payload(entry)
        return None

    def mark_dead_letter_replay(
        self,
        dead_letter_id: str,
        replay_status: str,
        replay_result: Dict[str, Any],
    ) -> None:
        for entry in self._dead_letters:
            if entry.dead_letter_id != dead_letter_id:
                continue
            entry.replay_status = replay_status
            entry.replayed_at = _utc_now()
            entry.replay_result = deepcopy(replay_result)
            return

    def append_policy_decision(self, record: ConnectorPolicyDecisionRecord) -> None:
        self._policy_decisions.append(record)

    def list_policy_decisions(
        self,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for entry in self._policy_decisions:
            if connector_id and entry.connector_id != connector_id:
                continue
            if direction and entry.direction != direction:
                continue
            rows.append(_policy_decision_to_payload(entry))
        return rows

    def get_policy_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        for entry in self._policy_decisions:
            if entry.decision_id == decision_id:
                return _policy_decision_to_payload(entry)
        return None


class SQLiteConnectorStateStore(BaseConnectorStateStore):
    def __init__(self, database_path: Path, migrations_dir: Optional[Path] = None) -> None:
        self.database_path = Path(database_path)
        self.migrations_dir = migrations_dir or (
            Path(__file__).resolve().parents[1] / "infra" / "migrations" / "persistence"
        )
        apply_sqlite_migrations(self.database_path, self.migrations_dir)

    def get_idempotency(self, key: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT result_json
                FROM connector_idempotency
                WHERE key = ?
                """,
                (key,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def put_idempotency(self, key: str, direction: str, connector_id: str, result: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO connector_idempotency(key, direction, connector_id, result_json, created_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (
                    key,
                    direction,
                    connector_id,
                    json.dumps(result, separators=(",", ":")),
                    _utc_now(),
                ),
            )
            conn.commit()

    def append_dead_letter(self, record: DeadLetterRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO connector_dead_letters(
                    dead_letter_id,
                    connector_id,
                    direction,
                    idempotency_key,
                    reason,
                    payload_json,
                    attempts,
                    last_error,
                    created_at,
                    replay_status,
                    replayed_at,
                    replay_result_json
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.dead_letter_id,
                    record.connector_id,
                    record.direction,
                    record.idempotency_key,
                    record.reason,
                    json.dumps(record.payload, separators=(",", ":")),
                    record.attempts,
                    record.last_error,
                    record.created_at,
                    record.replay_status,
                    record.replayed_at,
                    json.dumps(record.replay_result, separators=(",", ":")) if record.replay_result else None,
                ),
            )
            conn.commit()

    def list_dead_letters(
        self,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses: List[str] = []
        params: List[Any] = []
        if connector_id:
            clauses.append("connector_id = ?")
            params.append(connector_id)
        if direction:
            clauses.append("direction = ?")
            params.append(direction)

        where_sql = ""
        if clauses:
            where_sql = "WHERE " + " AND ".join(clauses)

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT dead_letter_id, connector_id, direction, idempotency_key, reason, payload_json,
                       attempts, last_error, created_at, replay_status, replayed_at, replay_result_json
                FROM connector_dead_letters
                %s
                ORDER BY created_at ASC, dead_letter_id ASC
                """
                % where_sql,
                tuple(params),
            ).fetchall()
        return [self._row_to_payload(row) for row in rows]

    def get_dead_letter(self, dead_letter_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT dead_letter_id, connector_id, direction, idempotency_key, reason, payload_json,
                       attempts, last_error, created_at, replay_status, replayed_at, replay_result_json
                FROM connector_dead_letters
                WHERE dead_letter_id = ?
                """,
                (dead_letter_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_payload(row)

    def mark_dead_letter_replay(
        self,
        dead_letter_id: str,
        replay_status: str,
        replay_result: Dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE connector_dead_letters
                SET replay_status = ?, replayed_at = ?, replay_result_json = ?
                WHERE dead_letter_id = ?
                """,
                (
                    replay_status,
                    _utc_now(),
                    json.dumps(replay_result, separators=(",", ":")),
                    dead_letter_id,
                ),
            )
            conn.commit()

    def append_policy_decision(self, record: ConnectorPolicyDecisionRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO connector_policy_decisions(
                    decision_id,
                    connector_id,
                    direction,
                    idempotency_key,
                    final_outcome,
                    status,
                    provider,
                    source,
                    approval_id,
                    policy_report_json,
                    execution_result_json,
                    created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.decision_id,
                    record.connector_id,
                    record.direction,
                    record.idempotency_key,
                    record.final_outcome,
                    record.status,
                    record.provider,
                    record.source,
                    record.approval_id,
                    json.dumps(record.policy_report, separators=(",", ":")),
                    (
                        json.dumps(record.execution_result, separators=(",", ":"))
                        if record.execution_result is not None
                        else None
                    ),
                    record.created_at,
                ),
            )
            conn.commit()

    def list_policy_decisions(
        self,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses: List[str] = []
        params: List[Any] = []
        if connector_id:
            clauses.append("connector_id = ?")
            params.append(connector_id)
        if direction:
            clauses.append("direction = ?")
            params.append(direction)

        where_sql = ""
        if clauses:
            where_sql = "WHERE " + " AND ".join(clauses)

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT decision_id, connector_id, direction, idempotency_key, final_outcome, status,
                       provider, source, approval_id, policy_report_json, execution_result_json, created_at
                FROM connector_policy_decisions
                %s
                ORDER BY created_at ASC, decision_id ASC
                """
                % where_sql,
                tuple(params),
            ).fetchall()
        return [self._policy_decision_row_to_payload(row) for row in rows]

    def get_policy_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT decision_id, connector_id, direction, idempotency_key, final_outcome, status,
                       provider, source, approval_id, policy_report_json, execution_result_json, created_at
                FROM connector_policy_decisions
                WHERE decision_id = ?
                """,
                (decision_id,),
            ).fetchone()
        if row is None:
            return None
        return self._policy_decision_row_to_payload(row)

    def _policy_decision_row_to_payload(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "decision_id": row[0],
            "connector_id": row[1],
            "direction": row[2],
            "idempotency_key": row[3],
            "final_outcome": row[4],
            "status": row[5],
            "provider": row[6],
            "source": row[7],
            "approval_id": row[8],
            "policy_report": json.loads(row[9]),
            "execution_result": json.loads(row[10]) if row[10] else None,
            "created_at": row[11],
        }

    def _row_to_payload(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "dead_letter_id": row[0],
            "connector_id": row[1],
            "direction": row[2],
            "idempotency_key": row[3],
            "reason": row[4],
            "payload": json.loads(row[5]),
            "attempts": int(row[6]),
            "last_error": row[7],
            "created_at": row[8],
            "replay_status": row[9],
            "replayed_at": row[10],
            "replay_result": json.loads(row[11]) if row[11] else None,
        }

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.database_path))
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def _record_to_payload(entry: DeadLetterRecord) -> Dict[str, Any]:
    return {
        "dead_letter_id": entry.dead_letter_id,
        "connector_id": entry.connector_id,
        "direction": entry.direction,
        "idempotency_key": entry.idempotency_key,
        "reason": entry.reason,
        "payload": deepcopy(entry.payload),
        "attempts": entry.attempts,
        "last_error": entry.last_error,
        "created_at": entry.created_at,
        "replay_status": entry.replay_status,
        "replayed_at": entry.replayed_at,
        "replay_result": deepcopy(entry.replay_result) if entry.replay_result else None,
    }


def _policy_decision_to_payload(entry: ConnectorPolicyDecisionRecord) -> Dict[str, Any]:
    return {
        "decision_id": entry.decision_id,
        "connector_id": entry.connector_id,
        "direction": entry.direction,
        "idempotency_key": entry.idempotency_key,
        "final_outcome": entry.final_outcome,
        "status": entry.status,
        "provider": entry.provider,
        "source": entry.source,
        "approval_id": entry.approval_id,
        "policy_report": deepcopy(entry.policy_report),
        "execution_result": deepcopy(entry.execution_result) if entry.execution_result is not None else None,
        "created_at": entry.created_at,
    }

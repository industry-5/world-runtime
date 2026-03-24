import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.connectors import ConnectorRuntime, OutboundConnectorConfig, RetryPolicy
from core.migrations import apply_sqlite_migrations
from core.path_utils import display_repo_path, resolve_writable_repo_path
from core.persistence_recovery import backup_sqlite_database, restore_sqlite_database, sqlite_table_counts
from core.sqlite_event_store import SQLiteEventStore

MIGRATIONS_DIR = REPO_ROOT / "infra" / "migrations" / "persistence"


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _seed_events(store: SQLiteEventStore, event_count: int) -> None:
    for index in range(event_count):
        store.append(
            "recovery.events",
            {
                "event_id": "evt.recovery.%05d" % index,
                "event_type": "shipment_delayed",
                "payload": {
                    "shipment_id": "shipment.%05d" % index,
                    "delay_hours": (index % 7) + 1,
                    "cause": "stress",
                },
            },
        )

    if event_count > 0:
        store.create_snapshot(
            "world_state",
            source_event_offset=event_count - 1,
            state={"events_processed": event_count},
            metadata={"generated_by": "check_persistence_recovery"},
        )


def _restart_idempotency_check(database_path: Path) -> Dict[str, Any]:
    store = SQLiteEventStore(database_path, MIGRATIONS_DIR)
    runtime_one = ConnectorRuntime(store)

    config = OutboundConnectorConfig(
        connector_id="connector.recovery.egress",
        action_type_map={"reroute_shipment": "dispatch.reroute"},
        retry=RetryPolicy(max_attempts=2),
    )

    action = {
        "action_id": "act.recovery.0001",
        "action_type": "reroute_shipment",
        "payload": {"shipment_id": "shipment.88421", "new_route": "route.recovery"},
    }

    def _transport(payload: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        return {"ack": "delivered", "attempt": attempt, "external_action_type": payload["external_action_type"]}
    
    first = runtime_one.run_outbound(
        config=config,
        action=action,
        idempotency_key="stable-key",
        transport=_transport,
    )

    store_after_restart = SQLiteEventStore(database_path, MIGRATIONS_DIR)
    runtime_two = ConnectorRuntime(store_after_restart)
    second = runtime_two.run_outbound(
        config=config,
        action=action,
        idempotency_key="stable-key",
        transport=_transport,
    )

    _assert(first["status"] == "completed", "first outbound should complete")
    _assert(second["status"] == "duplicate", "second outbound should be duplicate after restart")

    return {
        "first_status": first["status"],
        "second_status": second["status"],
        "idempotency_key": second["idempotency_key"],
    }


def _backup_restore_check(database_path: Path, workspace: Path) -> Dict[str, Any]:
    backup_path = workspace / "backup" / "world-runtime.sqlite.bak"
    restored_path = workspace / "restore" / "world-runtime.sqlite"

    before_counts = sqlite_table_counts(database_path)
    backup_info = backup_sqlite_database(database_path, backup_path)
    restore_info = restore_sqlite_database(backup_path, restored_path)
    restored_counts = sqlite_table_counts(restored_path)

    _assert(before_counts == restored_counts, "backup/restore table counts mismatch")

    return {
        "before_counts": before_counts,
        "restored_counts": restored_counts,
        "backup_bytes": backup_info["bytes"],
        "restored_bytes": restore_info["bytes"],
        "backup_path": display_repo_path(REPO_ROOT, backup_path),
        "restored_path": display_repo_path(REPO_ROOT, restored_path),
    }


def _migration_volume_check(workspace: Path, event_count: int) -> Dict[str, Any]:
    volume_db_path = workspace / "volume" / "volume-check.sqlite"
    if volume_db_path.exists():
        volume_db_path.unlink()

    first = apply_sqlite_migrations(volume_db_path, MIGRATIONS_DIR)
    store = SQLiteEventStore(volume_db_path, MIGRATIONS_DIR)
    _seed_events(store, event_count)

    runtime = ConnectorRuntime(store)
    runtime.record_policy_decision(
        decision_id="decision.recovery.volume.0001",
        connector_id="connector.recovery.egress",
        direction="outbound",
        idempotency_key="outbound:connector.recovery.egress:volume",
        final_outcome="allow",
        status="completed",
        policy_report={
            "proposal_id": "proposal.volume.0001",
            "final_outcome": "allow",
            "requires_approval": False,
            "denied": False,
            "evaluations": [],
        },
        provider="mock.webhook",
        source="volume_check",
    )

    second = apply_sqlite_migrations(volume_db_path, MIGRATIONS_DIR)
    counts = sqlite_table_counts(volume_db_path)

    _assert(len(first["applied"]) >= 1, "initial migration run should apply migrations")
    _assert(len(second["applied"]) == 0, "second migration run must be idempotent")
    _assert(counts["events"] == event_count, "event count mismatch after volume load")
    _assert(counts["connector_policy_decisions"] == 1, "expected one policy decision record")

    return {
        "event_count": event_count,
        "migration_first": first,
        "migration_second": second,
        "counts": counts,
        "database_path": display_repo_path(REPO_ROOT, volume_db_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run M23 persistence recovery and migration-volume checks")
    parser.add_argument("--event-count", type=int, default=5000)
    parser.add_argument("--output", default="tmp/diagnostics/m23_recovery.latest.json")
    args = parser.parse_args()

    if args.event_count < 100:
        raise SystemExit("--event-count must be >= 100")

    workspace = resolve_writable_repo_path(REPO_ROOT, Path("tmp/m23"))
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    runtime_db_path = workspace / "runtime" / "world-runtime.sqlite"
    runtime_db_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_store = SQLiteEventStore(runtime_db_path, MIGRATIONS_DIR)
    _seed_events(runtime_store, args.event_count)

    restart_check = _restart_idempotency_check(runtime_db_path)
    backup_restore = _backup_restore_check(runtime_db_path, workspace)
    migration_volume = _migration_volume_check(workspace, args.event_count)

    payload = {
        "check_status": "passed",
        "event_count": args.event_count,
        "restart_idempotency": restart_check,
        "backup_restore": backup_restore,
        "migration_volume": migration_volume,
    }

    output_path = resolve_writable_repo_path(REPO_ROOT, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

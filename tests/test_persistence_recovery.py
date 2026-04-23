import json
from pathlib import Path
import subprocess
import sys

from core.persistence_recovery import backup_sqlite_database, restore_sqlite_database, sqlite_table_counts
from core.sqlite_event_store import SQLiteEventStore

REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = REPO_ROOT / "infra" / "migrations" / "persistence"


def test_backup_restore_roundtrip_preserves_table_counts(tmp_path: Path):
    db_path = tmp_path / "source.sqlite"
    store = SQLiteEventStore(db_path, MIGRATIONS_DIR)

    for index in range(25):
        store.append(
            "stream.backup",
            {
                "event_id": "evt.%03d" % index,
                "event_type": "shipment_delayed",
                "payload": {"shipment_id": "shipment.%03d" % index, "delay_hours": 2, "cause": "test"},
            },
        )

    store.create_snapshot("world_state", 24, {"events_processed": 25})

    backup_path = tmp_path / "backup" / "source.sqlite.bak"
    restored_path = tmp_path / "restore" / "restored.sqlite"

    before = sqlite_table_counts(db_path)
    backup_sqlite_database(db_path, backup_path)
    restore_sqlite_database(backup_path, restored_path)
    after = sqlite_table_counts(restored_path)

    assert before == after
    assert after["events"] == 25
    assert after["snapshots"] == 1


def test_m23_recovery_script_passes_with_reduced_volume(tmp_path: Path):
    output_rel = "tmp/diagnostics/test_m23_recovery.json"
    output_path = REPO_ROOT / output_rel
    if output_path.exists():
        output_path.unlink()
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_persistence_recovery.py",
            "--event-count",
            "200",
            "--output",
            output_rel,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["check_status"] == "passed"
    assert payload["migration_volume"]["counts"]["events"] == 200


def test_m23_benchmark_script_passes_with_reduced_samples(tmp_path: Path):
    output_rel = "tmp/diagnostics/test_m23_benchmarks.json"
    output_path = REPO_ROOT / output_rel
    if output_path.exists():
        output_path.unlink()
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_performance_benchmarks.py",
            "--profiles",
            "local",
            "--iterations",
            "3",
            "--samples",
            "2",
            "--replay-events",
            "60",
            "--output",
            output_rel,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["benchmark_status"] == "passed"
    assert payload["workload"]["replay_events"] == 60
    assert payload["results"]["local"]["replay"]["sample_count"] == 2

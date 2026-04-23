import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_service_host_smoke_fast_mode_passes():
    output_rel = "tmp/diagnostics/test_m27_service_host.json"
    output_path = REPO_ROOT / output_rel
    if output_path.exists():
        output_path.unlink()

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_service_host.py",
            "--fast",
            "--output",
            output_rel,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["milestone"] == "M27"
    assert payload["status"] == "passed"
    assert payload["mode"] == "fast"
    assert payload["errors"] == []
    assert payload["scenarios"]["reference_ready"]["lifecycle_state"] == "ready"
    assert payload["scenarios"]["failed_start"]["lifecycle_state"] == "failed"

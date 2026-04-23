import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_release_candidate_gate_fast_mode_passes():
    output_rel = "tmp/diagnostics/test_m25_release_candidate_gate.json"
    output_path = REPO_ROOT / output_rel
    if output_path.exists():
        output_path.unlink()

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_release_candidate_gate.py",
            "--fast",
            "--release-version",
            "1.1.0-test",
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
    assert payload["milestone"] == "M25"
    assert payload["status"] == "passed"
    assert payload["mode"] == "fast"
    assert payload["release_version"] == "1.1.0-test"
    assert payload["errors"] == []
    assert len(payload["command_results"]) >= 5

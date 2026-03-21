import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_protocol_compatibility_script_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_protocol_compatibility.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Protocol compatibility check passed." in result.stdout

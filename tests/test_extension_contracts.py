import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_extension_contract_script_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_extension_contracts.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Extension contract check passed." in result.stdout

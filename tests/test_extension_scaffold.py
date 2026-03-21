import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_scaffold_extension_generates_adapter_and_connector(tmp_path):
    adapter_dir = tmp_path / "adapter"
    connector_dir = tmp_path / "connector"

    adapter_result = subprocess.run(
        [
            sys.executable,
            "scripts/scaffold_extension.py",
            "adapter",
            "--name",
            "Acme Ops",
            "--output-dir",
            str(adapter_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert adapter_result.returncode == 0
    assert (adapter_dir / "adapter.py").exists()
    assert "adapter-acme-ops" in (adapter_dir / "adapter.py").read_text(encoding="utf-8")

    connector_result = subprocess.run(
        [
            sys.executable,
            "scripts/scaffold_extension.py",
            "connector-plugin",
            "--name",
            "Acme Queue",
            "--provider",
            "acme.queue",
            "--output-dir",
            str(connector_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert connector_result.returncode == 0
    assert (connector_dir / "plugin.py").exists()
    assert "acme.queue" in (connector_dir / "plugin.py").read_text(encoding="utf-8")

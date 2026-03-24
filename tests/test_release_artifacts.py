import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_release_artifact_builder_outputs_manifest_and_archive(tmp_path):
    output_dir = tmp_path / "releases"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_release_artifacts.py",
            "--version",
            "0.1.0-test",
            "--output-dir",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0

    release_dir = output_dir / "v0.1.0-test"
    assert release_dir.exists()
    assert (release_dir / "release.manifest.json").exists()
    assert (release_dir / "SHA256SUMS").exists()
    assert (output_dir / "v0.1.0-test.tar.gz").exists()

    manifest = json.loads((release_dir / "release.manifest.json").read_text(encoding="utf-8"))
    assert manifest["release_version"] == "0.1.0-test"
    assert manifest["protocol"]["version"] == "1.0"
    assert manifest["protocol"]["compatibility_policy"] == "major-compatible"
    assert len(manifest["files"]) >= 10
    manifest_paths = {item["path"] for item in manifest["files"]}
    assert "docs/EXTENSION_CONTRACTS.md" in manifest_paths
    assert "docs/PARTNER_ONBOARDING.md" in manifest_paths
    assert "docs/COMPATIBILITY_MATRIX.md" in manifest_paths
    assert "docs/RELEASE_READINESS_CHECKLIST.md" in manifest_paths
    assert "docs/SECURITY_TRUST_BOUNDARY_REVIEW.md" in manifest_paths
    assert "docs/SUPPORT_POLICY.md" in manifest_paths
    assert "playbooks/ci-cd-release.md" in manifest_paths
    assert "CHANGELOG.md" in manifest_paths
    assert "templates/adapter_starter/adapter.py" in manifest_paths
    assert "templates/connector_plugin_starter/plugin.py" in manifest_paths

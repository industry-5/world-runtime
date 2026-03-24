import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.app_protocol import COMPATIBILITY_POLICY, PROTOCOL_VERSION

DEFAULT_RELEASES_DIR = REPO_ROOT / "dist" / "releases"
DEFAULT_VERSION_FILE = REPO_ROOT / "VERSION"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_version(version_file: Path) -> str:
    if not version_file.exists():
        raise ValueError(f"missing version file: {version_file}")
    version = version_file.read_text(encoding="utf-8").strip()
    if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$", version):
        raise ValueError(f"invalid semantic version in {version_file}: {version}")
    return version


def git_commit_sha() -> str:
    try:
        output = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"
    return output or "unknown"


def collect_release_inputs() -> list[Path]:
    required_files = [
        Path("README.md"),
        Path("ARCHITECTURE.md"),
        Path("APP_SERVER_PROTOCOL.md"),
        Path("VERSION"),
        Path("evals/suites.manifest.json"),
        Path("docs/EXTENSION_CONTRACTS.md"),
        Path("docs/PARTNER_ONBOARDING.md"),
        Path("docs/COMPATIBILITY_MATRIX.md"),
        Path("docs/RELEASE_READINESS_CHECKLIST.md"),
        Path("docs/SECURITY_TRUST_BOUNDARY_REVIEW.md"),
        Path("docs/SUPPORT_POLICY.md"),
        Path("playbooks/partner-onboarding.md"),
        Path("playbooks/ci-cd-release.md"),
        Path("scripts/scaffold_extension.py"),
        Path("scripts/check_extension_contracts.py"),
    ]

    inputs = []
    for rel_path in required_files:
        path = REPO_ROOT / rel_path
        if not path.exists():
            raise ValueError(f"required release input missing: {rel_path}")
        inputs.append(path)

    for schema_path in sorted((REPO_ROOT / "schemas").glob("*.json")):
        inputs.append(schema_path)

    for template_path in sorted((REPO_ROOT / "templates").rglob("*")):
        if template_path.is_file():
            inputs.append(template_path)

    return inputs


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 64)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def copy_inputs(input_paths: list[Path], artifact_dir: Path) -> list[dict]:
    copied = []
    for source in input_paths:
        rel_path = source.relative_to(REPO_ROOT)
        destination = artifact_dir / rel_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(
            {
                "path": rel_path.as_posix(),
                "size_bytes": destination.stat().st_size,
                "sha256": file_sha256(destination),
            }
        )
    copied.sort(key=lambda item: item["path"])
    return copied


def write_checksums(artifact_dir: Path, files: list[dict]) -> None:
    sums_path = artifact_dir / "SHA256SUMS"
    with sums_path.open("w", encoding="utf-8") as f:
        for item in files:
            f.write(f"{item['sha256']}  {item['path']}\n")


def write_manifest(artifact_dir: Path, version: str, files: list[dict]) -> dict:
    manifest = {
        "release_version": version,
        "created_at": utc_now(),
        "git_commit": git_commit_sha(),
        "protocol": {
            "version": PROTOCOL_VERSION,
            "compatibility_policy": COMPATIBILITY_POLICY,
        },
        "eval_suite": load_json(REPO_ROOT / "evals" / "suites.manifest.json"),
        "files": files,
    }
    manifest_path = artifact_dir / "release.manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def build_release_artifacts(version: str, output_dir: Path) -> Path:
    artifact_dir = output_dir / f"v{version}"
    if artifact_dir.exists():
        shutil.rmtree(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    files = copy_inputs(collect_release_inputs(), artifact_dir)
    write_checksums(artifact_dir, files)
    write_manifest(artifact_dir, version, files)

    archive_path = output_dir / f"v{version}"
    shutil.make_archive(str(archive_path), "gztar", root_dir=artifact_dir)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build versioned release artifacts.")
    parser.add_argument(
        "--version",
        help="Release semantic version (defaults to VERSION file).",
    )
    parser.add_argument(
        "--version-file",
        type=Path,
        default=DEFAULT_VERSION_FILE,
        help="Path to version file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_RELEASES_DIR,
        help="Directory where release artifacts are written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        version = args.version or read_version(args.version_file)
        if args.version and not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$", args.version):
            raise ValueError(f"invalid semantic version provided: {args.version}")
        artifact_dir = build_release_artifacts(version=version, output_dir=args.output_dir)
    except ValueError as exc:
        print(f"Release artifact build failed: {exc}")
        return 1

    print(f"Release artifacts built in {artifact_dir}")
    print(f"Release archive built in {args.output_dir / ('v' + version + '.tar.gz')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import json
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "tmp" / "diagnostics" / "m25_release_candidate_gate.latest.json"

REQUIRED_DOCS = {
    "docs/RELEASE_READINESS_CHECKLIST.md": [
        "# v1.0 Release Readiness Checklist",
        "## Go/No-Go Criteria",
        "## Aggregate Release Gate Matrix",
    ],
    "docs/SECURITY_TRUST_BOUNDARY_REVIEW.md": [
        "# Security and Trust-Boundary Review",
        "## Findings Register",
        "## Waivers",
    ],
    "docs/SUPPORT_POLICY.md": [
        "# Support Policy",
        "## Compatibility Commitments",
    ],
    "CHANGELOG.md": [
        "# Changelog",
        "## [1.0.0] - 2026-03-22",
    ],
}


@dataclass(frozen=True)
class CommandSpec:
    group: str
    label: str
    command: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_command_matrix(release_version: str, fast: bool) -> List[CommandSpec]:
    if fast:
        return [
            CommandSpec("milestone", "schema-check", "make schemas"),
            CommandSpec("milestone", "protocol-compat", "make protocol-compat"),
            CommandSpec("milestone", "public-api-compat", "make public-api-compat"),
            CommandSpec("milestone", "extension-contracts", "make extension-contracts"),
            CommandSpec(
                "milestone",
                "release-artifacts",
                f"python3 scripts/build_release_artifacts.py --version {shlex.quote(release_version)} --output-dir tmp/releases_fast",
            ),
        ]

    return [
        CommandSpec("baseline", "test", "make test"),
        CommandSpec("baseline", "validate", "make validate"),
        CommandSpec("milestone", "evals", "make evals"),
        CommandSpec("milestone", "benchmark", "make benchmark"),
        CommandSpec("milestone", "recovery-check", "make recovery-check"),
        CommandSpec("milestone", "provenance-audit", "make provenance-audit"),
        CommandSpec("milestone", "release-artifacts", f"make release-artifacts RELEASE_VERSION={shlex.quote(release_version)}"),
        CommandSpec("regression", "examples", "make examples"),
        CommandSpec("regression", "adapters", "make adapters"),
        CommandSpec("regression", "connectors", "make connectors"),
        CommandSpec("regression", "connector-plugins", "make connector-plugins"),
        CommandSpec("regression", "integration-stacks", "make integration-stacks"),
        CommandSpec("regression", "protocol-compat", "make protocol-compat"),
        CommandSpec("regression", "public-api-compat", "make public-api-compat"),
        CommandSpec("regression", "extension-contracts", "make extension-contracts"),
    ]


def _check_required_docs() -> List[str]:
    errors: List[str] = []
    for rel_path, required_strings in REQUIRED_DOCS.items():
        path = REPO_ROOT / rel_path
        if not path.exists():
            errors.append(f"missing required document: {rel_path}")
            continue
        content = path.read_text(encoding="utf-8")
        for marker in required_strings:
            if marker not in content:
                errors.append(f"document marker missing in {rel_path}: {marker}")
    return errors


def _evaluate_security_findings() -> tuple[List[dict], List[str]]:
    review_path = REPO_ROOT / "docs" / "SECURITY_TRUST_BOUNDARY_REVIEW.md"
    if not review_path.exists():
        return [], ["missing security review document"]

    findings: List[dict] = []
    errors: List[str] = []

    for raw_line in review_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("| STB-"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 8:
            errors.append(f"malformed findings row: {line}")
            continue

        finding = {
            "id": cells[0],
            "boundary": cells[1],
            "severity": cells[2].lower(),
            "status": cells[3].lower(),
            "disposition": cells[4].lower(),
            "owner": cells[5],
            "evidence": cells[6],
            "notes": cells[7],
        }
        findings.append(finding)

    if not findings:
        errors.append("no security findings rows found in review register")

    for finding in findings:
        status = finding["status"]
        disposition = finding["disposition"]
        if status == "open" and disposition != "waived":
            errors.append(
                f"{finding['id']} is open and not waived (status={status}, disposition={disposition})"
            )

    return findings, errors


def _run_command(spec: CommandSpec) -> dict:
    result = subprocess.run(
        spec.command,
        cwd=REPO_ROOT,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "group": spec.group,
        "label": spec.label,
        "command": spec.command,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
        "status": "passed" if result.returncode == 0 else "failed",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run M25 v1.0 release gate checks")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--release-version", default="1.0.0")
    parser.add_argument("--rc-version", dest="release_version_legacy")
    parser.add_argument("--fast", action="store_true", help="Run reduced gate matrix for smoke/test environments")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    payload = {
        "milestone": "M25",
        "gate": "v1.0-release",
        "started_at": utc_now(),
        "mode": "fast" if args.fast else "full",
    }
    release_version = args.release_version_legacy or args.release_version
    payload["release_version"] = release_version

    errors = _check_required_docs()
    findings, security_errors = _evaluate_security_findings()
    errors.extend(security_errors)

    command_results = []
    for spec in _build_command_matrix(release_version=release_version, fast=args.fast):
        result = _run_command(spec)
        command_results.append(result)
        if result["returncode"] != 0:
            errors.append(f"command failed ({result['label']}): {result['command']}")

    payload["security_findings"] = findings
    payload["command_results"] = command_results
    payload["completed_at"] = utc_now()
    payload["status"] = "passed" if not errors else "failed"
    payload["errors"] = errors

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

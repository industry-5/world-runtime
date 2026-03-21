from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/test_connectors.py",
        "tests/test_connector_policy_guardrails.py",
        "tests/test_app_server.py",
        "tests/test_integration_reference_stacks.py",
        "tests/test_persistence_adapters.py",
        "-k",
        "connector or integration_stack or connector_state",
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

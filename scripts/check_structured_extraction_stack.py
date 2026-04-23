import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.local_ai_reference_stack import run_local_ai_reference_stack


DEFAULT_OUTPUT = REPO_ROOT / "tmp" / "diagnostics" / "m30_local_ai_structured_extraction.latest.json"
DEFAULT_STACK = REPO_ROOT / "infra" / "integration_stacks" / "local_ai_structured_extraction.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run M30 structured extraction stack validation")
    parser.add_argument("--stack", type=Path, default=DEFAULT_STACK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-eval", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_local_ai_reference_stack(
        REPO_ROOT,
        stack_path=args.stack,
        include_eval=not args.skip_eval,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

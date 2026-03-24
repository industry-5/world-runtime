import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.integration_stacks import IntegrationStackLoader


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and smoke test integration reference stacks")
    parser.add_argument("--skip-smoke", action="store_true", help="only validate stack manifests")
    args = parser.parse_args()

    loader = IntegrationStackLoader(REPO_ROOT)
    stack_names = loader.list_stack_names()

    if not stack_names:
        raise SystemExit("no integration stacks found under infra/integration_stacks")

    failed = False
    results = []

    for stack_name in stack_names:
        stack = loader.load_stack(stack_name)
        errors = loader.validate_stack(stack)
        if errors:
            failed = True
            print("[FAIL] %s" % stack_name)
            for error in errors:
                print("  - %s" % error)
            continue

        if args.skip_smoke:
            print("[OK]   %s (validated)" % stack_name)
            continue

        try:
            result = loader.smoke_check(stack_name, run_eval=True)
        except Exception as exc:
            failed = True
            print("[FAIL] %s" % stack_name)
            print("  - %s" % exc)
            continue

        results.append(result)
        print(
            "[OK]   %s (%s -> %s, policy=%s)"
            % (stack_name, result["query_type"], result["task_status"], result["policy_outcome"])
        )

    if failed:
        raise SystemExit(1)

    if results:
        print("\nIntegration stack smoke checks passed.")
        print(json.dumps(results, indent=2))
    else:
        print("\nIntegration stack manifest checks passed.")


if __name__ == "__main__":
    main()

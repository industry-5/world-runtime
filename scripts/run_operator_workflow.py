import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.operator_workflows import OperatorWorkflowRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run World Runtime operator workflows")
    parser.add_argument(
        "workflow",
        choices=[
            "quickstart",
            "failure-recovery",
            "proposal-review",
            "simulation-analysis",
        ],
    )
    parser.add_argument(
        "--adapter-id",
        default="adapter-supply-network",
        choices=[
            "adapter-supply-network",
            "adapter-air-traffic",
            "adapter-world-game",
        ],
    )
    parser.add_argument("--no-auto-approve", action="store_true")
    args = parser.parse_args()

    runner = OperatorWorkflowRunner(REPO_ROOT)

    if args.workflow == "quickstart":
        result = runner.run_quickstart(adapter_id=args.adapter_id)
    elif args.workflow == "failure-recovery":
        result = runner.run_failure_recovery(adapter_id=args.adapter_id)
    elif args.workflow == "proposal-review":
        result = runner.run_proposal_review(
            adapter_id=args.adapter_id,
            auto_approve=not args.no_auto_approve,
        )
    elif args.workflow == "simulation-analysis":
        result = runner.run_simulation_analysis(adapter_id=args.adapter_id)
    else:
        raise RuntimeError("unsupported workflow")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

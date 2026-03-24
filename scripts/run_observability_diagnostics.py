import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.operator_workflows import OperatorWorkflowRunner


def write_report(report: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    dashboard_path = out_dir / "dashboard.latest.json"
    summary_path = out_dir / "summary.latest.json"
    audit_path = out_dir / "audit_export.latest.json"

    with dashboard_path.open("w", encoding="utf-8") as f:
        json.dump(report["dashboard"], f, indent=2)
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(report["summary"], f, indent=2)
    if report.get("audit_export") is not None:
        with audit_path.open("w", encoding="utf-8") as f:
            json.dump(report["audit_export"], f, indent=2)

    paths = {
        "dashboard": str(dashboard_path),
        "summary": str(summary_path),
    }
    if report.get("audit_export") is not None:
        paths["audit_export"] = str(audit_path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate observability diagnostics dashboard")
    parser.add_argument(
        "--workflow",
        choices=["quickstart", "failure-recovery", "proposal-review", "simulation-analysis"],
        default="quickstart",
    )
    parser.add_argument("--include-audit-export", action="store_true")
    parser.add_argument("--adapter-id", default="adapter-supply-network")
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "tmp" / "diagnostics"))
    args = parser.parse_args()

    runner = OperatorWorkflowRunner(REPO_ROOT)

    if args.workflow == "quickstart":
        result = runner.run_quickstart(adapter_id=args.adapter_id)
    elif args.workflow == "failure-recovery":
        result = runner.run_failure_recovery(adapter_id=args.adapter_id)
    elif args.workflow == "proposal-review":
        result = runner.run_proposal_review(adapter_id=args.adapter_id)
    else:
        result = runner.run_simulation_analysis(adapter_id=args.adapter_id)

    audit_export = None
    if args.include_audit_export and result.get("session_id"):
        decision_id = None
        if isinstance(result.get("decision"), dict):
            decision_id = result["decision"].get("decision_id")
        audit_export = runner.app_server.audit_export(
            session_id=result["session_id"],
            decision_id=decision_id,
        )

    report = {
        "workflow": result["workflow"],
        "adapter_id": result["adapter_id"],
        "summary": runner.observability.summary(),
        "dashboard": runner.observability.dashboard(),
        "audit_export": audit_export,
    }
    paths = write_report(report, Path(args.out_dir))

    print("Workflow:", report["workflow"])
    print("Events:", report["summary"]["totals"]["events"])
    print("Traces:", report["summary"]["totals"]["traces"])
    print("Errors:", report["summary"]["totals"]["errors"])
    print("Dashboard:", paths["dashboard"])
    print("Summary:", paths["summary"])
    if paths.get("audit_export"):
        print("Audit export:", paths["audit_export"])


if __name__ == "__main__":
    main()

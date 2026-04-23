import runpy
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_milestone_docs.py"


def _script_module():
    return runpy.run_path(str(SCRIPT))


def _write_train_tree(
    base_dir: Path,
    train_id: str,
    milestone_id: str,
    handoff_text: str,
    include_prompt: bool = False,
) -> Path:
    train_dir = base_dir / "docs" / "milestones" / train_id
    milestone_dir = train_dir / milestone_id
    milestone_dir.mkdir(parents=True, exist_ok=True)
    (train_dir / "README.md").write_text(f"# {train_id}\n", encoding="utf-8")
    for filename in (
        "README.md",
        "REQUIREMENTS.md",
        "DESIGN.md",
        "VALIDATION.md",
        "OPEN_QUESTIONS.md",
    ):
        (milestone_dir / filename).write_text(f"# {filename}\n", encoding="utf-8")
    (milestone_dir / "HANDOFF.md").write_text(handoff_text, encoding="utf-8")
    if include_prompt:
        (milestone_dir / "PROMPT.md").write_text("# prompt\n", encoding="utf-8")
    return milestone_dir


def test_milestone_docs_script_passes_for_all_archived_trains():
    if not SCRIPT.exists() or not (REPO_ROOT / "docs" / "milestones").exists():
        pytest.skip("private milestone archive is intentionally omitted from the curated public export")

    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Milestone docs check passed for:" in result.stdout
    assert "WR-v1.1" in result.stdout
    assert "SO-P" in result.stdout


def test_missing_required_file_is_reported(tmp_path):
    module = _script_module()
    milestone_dir = _write_train_tree(
        tmp_path,
        "TEST",
        "M31",
        "## Risk Harvest And Disposition\n\nNone pulled forward.\n",
    )
    (milestone_dir / "DESIGN.md").unlink()

    errors = module["check_milestone_dir"](milestone_dir, "TEST", "M31", False)

    assert "TEST:M31: missing required file DESIGN.md" in errors


def test_missing_prompt_is_reported_for_prompt_train(tmp_path):
    module = _script_module()
    milestone_dir = _write_train_tree(
        tmp_path,
        "SO-P",
        "SO-P9",
        "## Risk Harvest And Disposition\n\nNone pulled forward.\n",
        include_prompt=False,
    )

    errors = module["check_milestone_dir"](milestone_dir, "SO-P", "SO-P9", True)

    assert "SO-P:SO-P9: missing archived PROMPT.md" in errors


def test_missing_risk_harvest_section_is_reported(tmp_path):
    module = _script_module()
    milestone_dir = _write_train_tree(tmp_path, "TEST", "M31", "# Handoff\n")

    errors = module["check_milestone_dir"](milestone_dir, "TEST", "M31", False)

    assert "TEST:M31: HANDOFF.md missing 'Risk Harvest And Disposition' section" in errors


def test_invalid_disposition_is_reported(tmp_path):
    module = _script_module()
    milestone_dir = _write_train_tree(
        tmp_path,
        "TEST",
        "M31",
        "\n".join(
            [
                "## Risk Harvest And Disposition",
                "",
                "### Item 1",
                "- Source: `STATUS.md` -> `M30 unresolved risks / deferred follow-ups`",
                "- Item: Example carry-forward risk.",
                "- Disposition: `punt-later`",
                "- Evidence / Rationale: Example rationale.",
                "- Follow-up Target: Example backlog item.",
                "",
            ]
        ),
    )

    errors = module["check_milestone_dir"](milestone_dir, "TEST", "M31", False)

    assert "TEST:M31: HANDOFF.md contains invalid disposition 'punt-later'" in errors


def test_none_pulled_forward_is_accepted(tmp_path):
    module = _script_module()
    milestone_dir = _write_train_tree(
        tmp_path,
        "TEST",
        "M31",
        "## Risk Harvest And Disposition\n\nNone pulled forward.\n",
    )

    errors = module["check_milestone_dir"](milestone_dir, "TEST", "M31", False)

    assert errors == []

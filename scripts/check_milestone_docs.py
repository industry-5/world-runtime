#!/usr/bin/env python3
"""Validate the centralized private/internal milestone archive."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "REQUIREMENTS.md",
    "DESIGN.md",
    "VALIDATION.md",
    "HANDOFF.md",
    "OPEN_QUESTIONS.md",
)
ALLOWED_DISPOSITIONS = {
    "addressed-now",
    "deferred-again",
    "converted-to-backlog",
}
CURRENT_ROOT_MILESTONE_PATTERN = re.compile(
    r"Most recently completed milestone:\s+\*\*(M\d{2})\b"
)
DISPOSITION_PATTERN = re.compile(r"^- Disposition:\s+`([^`]+)`\s*$", re.MULTILINE)

ARCHIVED_TRAINS = {
    "WR-v1.1": {
        "milestones": ["M26", "M27", "M28", "M29", "M30"],
        "require_prompt": False,
        "local_kickoffs": {
            "NEW_THREAD_KICKOFF_PROMPT.md": [
                "docs/milestones/WR-v1.1/README.md",
                "docs/milestones/WR-v1.1/M30/README.md",
            ]
        },
        "rollups": {
            "ROADMAP.md": ["docs/milestones/WR-v1.1/M26/", "docs/milestones/WR-v1.1/M30/"],
            "STATUS.md": ["docs/milestones/WR-v1.1/M26/", "docs/milestones/WR-v1.1/M30/"],
        },
    },
    "WR-UI": {
        "milestones": ["WR-UI-P0", "WR-UI-P1", "WR-UI-P2", "WR-UI-P3", "WR-UI-P4"],
        "require_prompt": False,
        "local_kickoffs": {
            "labs/shared_ui/NEW_THREAD_KICKOFF_PROMPT.md": [
                "docs/milestones/WR-UI/README.md",
                "docs/milestones/WR-UI/WR-UI-P4/README.md",
            ]
        },
        "rollups": {
            "labs/shared_ui/ROADMAP.md": ["docs/milestones/WR-UI/README.md"],
            "labs/shared_ui/STATUS.md": ["docs/milestones/WR-UI/README.md"],
        },
    },
    "SO-P": {
        "milestones": [
            "SO-P0",
            "SO-P1",
            "SO-P2",
            "SO-P3",
            "SO-P4",
            "SO-P5",
            "SO-P6",
            "SO-P7",
            "SO-P7.1",
            "SO-P7.2",
            "SO-P8",
            "SO-P8.1",
            "SO-P8.2",
        ],
        "require_prompt": True,
        "local_kickoffs": {
            "labs/supply_ops_lab/NEW_THREAD_KICKOFF_PROMPT.md": [
                "docs/milestones/SO-P/README.md",
                "docs/milestones/SO-P/SO-P8.2/PROMPT.md",
            ]
        },
        "rollups": {
            "labs/supply_ops_lab/README.md": ["docs/milestones/SO-P/README.md"],
            "labs/supply_ops_lab/STATUS.md": ["docs/milestones/SO-P/README.md"],
        },
    },
    "SO-M": {
        "milestones": ["SO-M0", "SO-M1", "SO-M2", "SO-M3", "SO-M4", "SO-M5"],
        "require_prompt": True,
        "local_kickoffs": {
            "adapters/supply_ops/NEW_THREAD_KICKOFF_PROMPT.md": [
                "docs/milestones/SO-M/README.md",
                "docs/milestones/SO-M/SO-M5/PROMPT.md",
            ]
        },
        "rollups": {
            "adapters/supply_ops/README.md": ["docs/milestones/SO-M/README.md"],
            "adapters/supply_ops/STATUS.md": ["docs/milestones/SO-M/README.md"],
        },
    },
    "WG-P": {
        "milestones": [
            "WG-P0",
            "WG-P1",
            "WG-P2",
            "WG-P3",
            "WG-P4",
            "WG-P5",
            "WG-P6",
            "WG-P7",
            "WG-P8",
            "WG-P9",
            "WG-P10",
        ],
        "require_prompt": False,
        "local_kickoffs": {
            "labs/world_game_studio_next/NEW_THREAD_KICKOFF_PROMPT.md": [
                "docs/milestones/WG-P/README.md",
                "docs/milestones/WG-P/WG-P10/README.md",
            ]
        },
        "rollups": {
            "labs/world_game_studio_next/README.md": ["docs/milestones/WG-P/README.md"],
            "labs/world_game_studio_next/STATUS.md": ["docs/milestones/WG-P/README.md"],
        },
    },
}


def detect_current_root_milestone(status_text: str) -> str:
    match = CURRENT_ROOT_MILESTONE_PATTERN.search(status_text)
    if not match:
        raise ValueError("could not determine current root milestone from STATUS.md")
    return match.group(1)


def archive_train_dir(repo_root: Path, train_id: str) -> Path:
    return repo_root / "docs" / "milestones" / train_id


def check_milestone_dir(path: Path, train_id: str, milestone_id: str, require_prompt: bool) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"{train_id}:{milestone_id}: missing milestone directory {path}"]

    for filename in REQUIRED_FILES:
        if not (path / filename).exists():
            errors.append(f"{train_id}:{milestone_id}: missing required file {filename}")

    if require_prompt and not (path / "PROMPT.md").exists():
        errors.append(f"{train_id}:{milestone_id}: missing archived PROMPT.md")

    handoff_path = path / "HANDOFF.md"
    if not handoff_path.exists():
        return errors

    handoff_text = handoff_path.read_text(encoding="utf-8")
    if "## Risk Harvest And Disposition" not in handoff_text:
        errors.append(
            f"{train_id}:{milestone_id}: HANDOFF.md missing 'Risk Harvest And Disposition' section"
        )
        return errors

    has_none_pulled_forward = "none pulled forward" in handoff_text.lower()
    dispositions = DISPOSITION_PATTERN.findall(handoff_text)
    if has_none_pulled_forward and dispositions:
        errors.append(
            f"{train_id}:{milestone_id}: HANDOFF.md must use either 'none pulled forward' or structured dispositions, not both"
        )
    elif not has_none_pulled_forward and not dispositions:
        errors.append(
            f"{train_id}:{milestone_id}: HANDOFF.md risk section must either say 'none pulled forward' or include disposition entries"
        )

    for disposition in dispositions:
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(
                f"{train_id}:{milestone_id}: HANDOFF.md contains invalid disposition '{disposition}'"
            )

    return errors


def check_train(repo_root: Path, train_id: str) -> list[str]:
    errors: list[str] = []
    train_config = ARCHIVED_TRAINS[train_id]
    train_dir = archive_train_dir(repo_root, train_id)

    if not train_dir.exists():
        return [f"{train_id}: missing train directory {train_dir}"]
    if not (train_dir / "README.md").exists():
        errors.append(f"{train_id}: missing train README.md")

    for milestone_id in train_config["milestones"]:
        errors.extend(
            check_milestone_dir(
                train_dir / milestone_id,
                train_id,
                milestone_id,
                train_config["require_prompt"],
            )
        )

    for relative_path, expected_patterns in train_config["local_kickoffs"].items():
        text = (repo_root / relative_path).read_text(encoding="utf-8")
        for pattern in expected_patterns:
            if pattern not in text:
                errors.append(f"{train_id}: {relative_path} missing archive reference {pattern}")

    for relative_path, expected_patterns in train_config["rollups"].items():
        text = (repo_root / relative_path).read_text(encoding="utf-8")
        for pattern in expected_patterns:
            if pattern not in text:
                errors.append(f"{train_id}: {relative_path} missing archive reference {pattern}")

    return errors


def check_root_current_milestone(repo_root: Path) -> list[str]:
    status_text = (repo_root / "STATUS.md").read_text(encoding="utf-8")
    current_milestone = detect_current_root_milestone(status_text)
    current_path = f"docs/milestones/WR-v1.1/{current_milestone}/"
    kickoff_path = f"docs/milestones/WR-v1.1/{current_milestone}/README.md"

    errors: list[str] = []
    if current_path not in status_text:
        errors.append(f"STATUS.md missing canonical root milestone path {current_path}")
    roadmap_text = (repo_root / "ROADMAP.md").read_text(encoding="utf-8")
    if current_path not in roadmap_text:
        errors.append(f"ROADMAP.md missing canonical root milestone path {current_path}")
    kickoff_text = (repo_root / "NEW_THREAD_KICKOFF_PROMPT.md").read_text(encoding="utf-8")
    if kickoff_path not in kickoff_text:
        errors.append(f"NEW_THREAD_KICKOFF_PROMPT.md missing canonical root milestone README {kickoff_path}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the private/internal milestone archive.")
    parser.add_argument(
        "trains",
        nargs="*",
        help="Optional archive train ids to validate. Defaults to all archived trains.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to validate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    trains = args.trains or list(ARCHIVED_TRAINS.keys())

    errors: list[str] = []
    for train_id in trains:
        if train_id not in ARCHIVED_TRAINS:
            errors.append(f"unknown archived train id: {train_id}")
            continue
        errors.extend(check_train(repo_root, train_id))
    if "WR-v1.1" in trains:
        errors.extend(check_root_current_milestone(repo_root))

    if errors:
        print("Milestone docs check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    print(f"Milestone docs check passed for: {', '.join(trains)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

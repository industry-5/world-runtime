from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def copy_path(source: Path, target: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    required = [ROOT / "index.html", ROOT / "src"]
    missing = [path for path in required if not path.exists()]
    if missing:
        missing_paths = ", ".join(str(path) for path in missing)
        raise SystemExit(f"Cannot build world_game_studio_next: missing required paths: {missing_paths}")

    copy_path(ROOT / "index.html", DIST / "index.html")
    copy_path(ROOT / "src", DIST / "src")

    assets_dir = ROOT / "assets"
    if assets_dir.exists():
        copy_path(assets_dir, DIST / "assets")

    print(f"Built world_game_studio_next static bundle at: {DIST}")


if __name__ == "__main__":
    main()

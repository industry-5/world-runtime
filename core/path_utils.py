import tempfile
from pathlib import Path
from typing import Union


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _can_create_file(parent: Path) -> bool:
    try:
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=parent, prefix=".write-test-", delete=True):
            return True
    except OSError:
        return False


def resolve_writable_repo_path(repo_root: Path, target: Union[Path, str]) -> Path:
    candidate = Path(target)
    if not candidate.is_absolute():
        candidate = repo_root / candidate

    if _can_create_file(candidate.parent):
        return candidate

    if _is_relative_to(candidate, repo_root):
        relative = candidate.relative_to(repo_root)
    else:
        relative = Path(candidate.name)

    fallback_root = Path(tempfile.gettempdir()) / "world-runtime" / repo_root.name
    fallback = fallback_root / relative
    fallback.parent.mkdir(parents=True, exist_ok=True)
    return fallback


def display_repo_path(repo_root: Path, path: Path) -> str:
    if _is_relative_to(path, repo_root):
        return str(path.relative_to(repo_root))
    return str(path)


def is_repo_relative(path: Path, repo_root: Path) -> bool:
    return _is_relative_to(path, repo_root)

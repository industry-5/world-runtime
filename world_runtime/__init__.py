from importlib import metadata
from pathlib import Path


def _detect_version() -> str:
    try:
        return metadata.version("world-runtime")
    except metadata.PackageNotFoundError:
        version_file = Path(__file__).resolve().parents[1] / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
        return "0.0.0"


__version__ = _detect_version()

__all__ = ["__version__"]

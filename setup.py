from pathlib import Path

from setuptools import find_packages, setup


REPO_ROOT = Path(__file__).resolve().parent


setup(
    name="world-runtime",
    version=(REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip(),
    description="Harness-first reference runtime for executable world-model systems.",
    long_description=(REPO_ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    license="Apache-2.0",
    author="INDUSTRY 5, Inc.",
    packages=find_packages(include=["api*", "core*", "sdk*", "world_runtime*"]),
    include_package_data=True,
    package_data={
        "world_runtime.resources": [
            "bootstrap_examples/scenarios/supply-network-mini/events.json",
            "bootstrap_examples/scenarios/air-traffic-mini/events.json",
            "bootstrap_examples/scenarios/world-game-mini/events.json",
        ]
    },
    entry_points={
        "console_scripts": [
            "world-runtime=world_runtime.cli:main",
        ]
    },
)

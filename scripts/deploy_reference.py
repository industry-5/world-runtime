import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.deployment import DeploymentLoader


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reference deployment smoke bootstrap")
    parser.add_argument("--profile", choices=["local", "dev"], default="local")
    args = parser.parse_args()

    loader = DeploymentLoader(REPO_ROOT)
    profile = loader.load_profile(args.profile)

    if not profile.persistence_config.exists():
        raise SystemExit("missing persistence config: %s" % profile.persistence_config)
    if not profile.llm_config.exists():
        raise SystemExit("missing llm config: %s" % profile.llm_config)

    result = loader.smoke_check(args.profile)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

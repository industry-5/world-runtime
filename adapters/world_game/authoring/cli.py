import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from adapters.world_game.authoring import (
    create_world_game_template_bundle_draft,
    instantiate_world_game_template_bundle,
    list_world_game_template_bundles,
    load_world_game_template_bundle,
    publish_world_game_template_bundle,
    validate_world_game_template_bundle_workflow,
)


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_bundle(repo_root: Path) -> Path:
    return repo_root / "examples" / "world-game-authoring" / "template_bundle.multi-region.v1.json"


_INT_PATTERN = re.compile(r"^-?[0-9]+$")
_FLOAT_PATTERN = re.compile(r"^-?[0-9]+(?:\.[0-9]+)?$")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)
        handle.write("\n")


def _resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return repo_root / path


def _parse_param_value(raw: str) -> Any:
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INT_PATTERN.match(raw):
        try:
            return int(raw)
        except ValueError:
            pass
    if _FLOAT_PATTERN.match(raw):
        try:
            return float(raw)
        except ValueError:
            pass
    return raw


def _parse_parameter_pairs(entries: List[str]) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError("parameter must use key=value format: %s" % entry)
        key, raw_value = entry.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("parameter key is required: %s" % entry)
        parsed[key] = _parse_param_value(raw_value.strip())
    return parsed


def command_template_list(args: argparse.Namespace) -> int:
    repo_root = _default_repo_root()
    root = _resolve_path(repo_root, args.authoring_root) if args.authoring_root else None
    bundles = list_world_game_template_bundles(authoring_root=root)
    payload = {
        "authoring_root": str(root or (repo_root / "examples" / "world-game-authoring")),
        "count": len(bundles),
        "bundles": bundles,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


def command_scaffold(args: argparse.Namespace) -> int:
    repo_root = _default_repo_root()
    source = _resolve_path(repo_root, args.source_bundle) if args.source_bundle else _default_bundle(repo_root)
    draft = create_world_game_template_bundle_draft(
        source_bundle=source,
        bundle_id=args.bundle_id,
        label=args.label,
        description=args.description,
        content_version=args.content_version,
        deterministic_version_seed=args.deterministic_version_seed,
        tags=args.tags,
        created_at=args.created_at,
        updated_at=args.updated_at,
    )

    if args.output_path:
        output_path = _resolve_path(repo_root, args.output_path)
        _write_json(output_path, draft)

    print(
        json.dumps(
            {
                "source_bundle_path": str(source),
                "output_path": str(_resolve_path(repo_root, args.output_path)) if args.output_path else None,
                "bundle_metadata": draft.get("bundle_metadata", {}),
                "bundle": draft,
            },
            indent=2,
            ensure_ascii=True,
        )
    )
    return 0


def command_validate(args: argparse.Namespace) -> int:
    repo_root = _default_repo_root()
    bundle_path = _resolve_path(repo_root, args.bundle_path)
    report = validate_world_game_template_bundle_workflow(bundle_path)
    report["bundle_path"] = str(bundle_path)
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report["valid"] else 1


def command_publish(args: argparse.Namespace) -> int:
    repo_root = _default_repo_root()
    bundle_path = _resolve_path(repo_root, args.bundle_path)
    published = publish_world_game_template_bundle(
        bundle_path,
        published_at=args.published_at,
        updated_at=args.updated_at,
    )
    if args.output_path:
        output_path = _resolve_path(repo_root, args.output_path)
        _write_json(output_path, published["bundle"])

    print(
        json.dumps(
            {
                "bundle_path": str(bundle_path),
                "output_path": str(_resolve_path(repo_root, args.output_path)) if args.output_path else None,
                "publication": published["publication"],
                "bundle_metadata": published["bundle"]["bundle_metadata"],
                "validation": published["validation"],
            },
            indent=2,
            ensure_ascii=True,
        )
    )
    return 0


def command_instantiate(args: argparse.Namespace) -> int:
    repo_root = _default_repo_root()
    bundle_path = _resolve_path(repo_root, args.bundle_path)
    bundle = load_world_game_template_bundle(bundle_path)
    parameters = _parse_parameter_pairs(args.param)
    instantiated = instantiate_world_game_template_bundle(
        bundle,
        template_id=args.template_id,
        parameter_values=parameters,
    )

    if args.scenario_output_path:
        scenario_output_path = _resolve_path(repo_root, args.scenario_output_path)
        _write_json(scenario_output_path, instantiated.get("scenario_payload", instantiated["scenario"]))

    print(
        json.dumps(
            {
                "bundle_path": str(bundle_path),
                "scenario_output_path": (
                    str(_resolve_path(repo_root, args.scenario_output_path)) if args.scenario_output_path else None
                ),
                "instantiation_id": instantiated["instantiation_id"],
                "template_id": instantiated["template_id"],
                "scenario_id": instantiated["scenario"]["scenario_id"],
                "parameters": instantiated["parameters"],
                "bundle_metadata": instantiated["bundle_metadata"],
            },
            indent=2,
            ensure_ascii=True,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="World Game authoring workflow CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cmd_list = subparsers.add_parser("template-list", help="List discovered template bundles")
    cmd_list.add_argument("--authoring-root", help="Directory containing authoring bundles")
    cmd_list.set_defaults(func=command_template_list)

    cmd_scaffold = subparsers.add_parser("scaffold", help="Create a draft bundle from a source bundle")
    cmd_scaffold.add_argument("--source-bundle", help="Source bundle JSON path")
    cmd_scaffold.add_argument("--output-path", help="Optional output path for generated draft bundle")
    cmd_scaffold.add_argument("--bundle-id", help="Override bundle_metadata.bundle_id")
    cmd_scaffold.add_argument("--label", help="Override bundle_metadata.label")
    cmd_scaffold.add_argument("--description", help="Override bundle_metadata.description")
    cmd_scaffold.add_argument("--content-version", help="Override bundle_metadata.content_version")
    cmd_scaffold.add_argument(
        "--deterministic-version-seed",
        help="Override bundle_metadata.deterministic_version_seed",
    )
    cmd_scaffold.add_argument("--tag", dest="tags", action="append", default=[], help="Add bundle metadata tag")
    cmd_scaffold.add_argument("--created-at", help="Override bundle_metadata.created_at")
    cmd_scaffold.add_argument("--updated-at", help="Override bundle_metadata.updated_at")
    cmd_scaffold.set_defaults(func=command_scaffold)

    cmd_validate = subparsers.add_parser("validate", help="Validate a draft bundle (schema + semantic)")
    cmd_validate.add_argument("--bundle-path", required=True, help="Draft/published bundle JSON path")
    cmd_validate.set_defaults(func=command_validate)

    cmd_publish = subparsers.add_parser("publish", help="Publish a validated draft bundle")
    cmd_publish.add_argument("--bundle-path", required=True, help="Draft bundle JSON path")
    cmd_publish.add_argument("--output-path", help="Optional output path for published bundle")
    cmd_publish.add_argument("--published-at", help="Optional published timestamp override")
    cmd_publish.add_argument("--updated-at", help="Optional updated timestamp override")
    cmd_publish.set_defaults(func=command_publish)

    cmd_instantiate = subparsers.add_parser("instantiate", help="Instantiate a scenario from a bundle template")
    cmd_instantiate.add_argument("--bundle-path", required=True, help="Bundle JSON path")
    cmd_instantiate.add_argument("--template-id", required=True, help="Template identifier")
    cmd_instantiate.add_argument(
        "--param",
        action="append",
        default=[],
        help="Template parameter in key=value format (repeatable)",
    )
    cmd_instantiate.add_argument("--scenario-output-path", help="Optional output path for rendered scenario JSON")
    cmd_instantiate.set_defaults(func=command_instantiate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except ValueError as exc:
        parser.error(str(exc))
        return 2


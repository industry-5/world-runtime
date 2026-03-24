import argparse
import re
import shutil
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_ROOT = REPO_ROOT / "templates"

ADAPTER_TEMPLATE = TEMPLATES_ROOT / "adapter_starter"
CONNECTOR_TEMPLATE = TEMPLATES_ROOT / "connector_plugin_starter"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError("name must contain at least one alphanumeric character")
    return slug


def class_name(value: str) -> str:
    tokenized = re.findall(r"[A-Za-z0-9]+", value)
    if not tokenized:
        raise ValueError("name must contain at least one alphanumeric token")
    return "".join(part[:1].upper() + part[1:] for part in tokenized)


def replacements_for_adapter(name: str, slug: str) -> Dict[str, str]:
    return {
        "__ADAPTER_NAME__": name,
        "__ADAPTER_SLUG__": slug.replace("-", "_"),
        "__ADAPTER_ID__": f"adapter-{slug}",
        "__ADAPTER_NAME_CLASS__": class_name(name),
    }


def replacements_for_connector(name: str, slug: str, provider: str) -> Dict[str, str]:
    return {
        "__CONNECTOR_NAME__": name,
        "__CONNECTOR_SLUG__": slug.replace("-", "_"),
        "__CONNECTOR_PROVIDER__": provider,
        "__CONNECTOR_NAME_CLASS__": class_name(name),
    }


def render_tree(template_dir: Path, output_dir: Path, replacements: Dict[str, str], force: bool) -> None:
    if output_dir.exists():
        if force:
            shutil.rmtree(output_dir)
        else:
            raise ValueError(f"output directory already exists: {output_dir}")

    shutil.copytree(template_dir, output_dir)

    for path in output_dir.rglob("*"):
        if path.is_dir():
            continue
        text = path.read_text(encoding="utf-8")
        for key, value in replacements.items():
            text = text.replace(key, value)
        path.write_text(text, encoding="utf-8")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold World Runtime extension starters.")
    subparsers = parser.add_subparsers(dest="extension_type", required=True)

    adapter = subparsers.add_parser("adapter", help="Generate an adapter starter package")
    adapter.add_argument("--name", required=True, help="Human-readable adapter name")
    adapter.add_argument("--slug", help="Slug for package path and ids")
    adapter.add_argument("--output-dir", type=Path, required=True, help="Output directory path")
    adapter.add_argument("--force", action="store_true", help="Overwrite output directory if it exists")

    connector = subparsers.add_parser("connector-plugin", help="Generate a connector transport plugin starter")
    connector.add_argument("--name", required=True, help="Human-readable connector plugin name")
    connector.add_argument("--slug", help="Slug for package path")
    connector.add_argument("--provider", help="Provider id (defaults to <slug>.provider)")
    connector.add_argument("--output-dir", type=Path, required=True, help="Output directory path")
    connector.add_argument("--force", action="store_true", help="Overwrite output directory if it exists")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.extension_type == "adapter":
        slug = args.slug or slugify(args.name)
        replacements = replacements_for_adapter(name=args.name.strip(), slug=slug)
        render_tree(ADAPTER_TEMPLATE, args.output_dir, replacements, force=args.force)
        print(f"Adapter starter created at {args.output_dir}")
        return 0

    if args.extension_type == "connector-plugin":
        slug = args.slug or slugify(args.name)
        provider = args.provider or f"{slug}.provider"
        replacements = replacements_for_connector(name=args.name.strip(), slug=slug, provider=provider)
        render_tree(CONNECTOR_TEMPLATE, args.output_dir, replacements, force=args.force)
        print(f"Connector plugin starter created at {args.output_dir}")
        return 0

    raise ValueError(f"Unsupported extension type: {args.extension_type}")


if __name__ == "__main__":
    raise SystemExit(main())

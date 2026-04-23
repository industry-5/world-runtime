import argparse
from pathlib import Path
from typing import Optional

from api.http_server import add_server_arguments, serve_app_server
from api.runtime_factory import build_server_from_examples
from world_runtime.bootstrap import build_server_from_packaged_examples


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="world-runtime", description="World Runtime package CLI")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Run the supported Public API /v1 server")
    add_server_arguments(serve_parser, default_examples_dir=None)

    return parser


def _resolve_api_token(profile: str, api_token: Optional[str]) -> Optional[str]:
    if profile == "dev" and not api_token:
        raise ValueError("WORLD_RUNTIME_API_TOKEN or --api-token is required for --profile dev")
    return api_token


def run_serve(args: argparse.Namespace) -> int:
    api_token = _resolve_api_token(args.profile, args.api_token)
    if args.examples_dir:
        app_server = build_server_from_examples(Path(args.examples_dir))
    else:
        app_server = build_server_from_packaged_examples()
    serve_app_server(app_server, host=args.host, port=args.port, auth_token=api_token)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "serve":
        try:
            return run_serve(args)
        except ValueError as exc:
            parser.error(str(exc))

    parser.print_help()
    return 1

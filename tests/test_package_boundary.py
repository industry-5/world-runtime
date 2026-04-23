from api.runtime_api import PublicRuntimeAPI
from world_runtime.bootstrap import bootstrap_examples_root, build_server_from_packaged_examples
from world_runtime.cli import build_parser
from world_runtime.sdk import DEFAULT_API_VERSION, WorldRuntimeSDKClient


def test_world_runtime_cli_accepts_serve_command():
    args = build_parser().parse_args(["serve", "--profile", "local"])

    assert args.command == "serve"
    assert args.profile == "local"


def test_packaged_bootstrap_examples_exist():
    root = bootstrap_examples_root()

    assert root.joinpath("scenarios", "supply-network-mini", "events.json").is_file()
    assert root.joinpath("scenarios", "air-traffic-mini", "events.json").is_file()


def test_packaged_bootstrap_server_supports_public_api_session_flow():
    runtime_api = PublicRuntimeAPI(build_server_from_packaged_examples())

    session = runtime_api.create_session()

    assert session["session_id"].startswith("session.")


def test_world_runtime_sdk_re_exports_client():
    client = WorldRuntimeSDKClient(base_url="http://local.test")

    assert client.api_version == DEFAULT_API_VERSION

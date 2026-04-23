from importlib import resources

from api.runtime_factory import build_server_from_examples


def bootstrap_examples_root():
    return resources.files("world_runtime.resources").joinpath("bootstrap_examples")


def build_server_from_packaged_examples():
    return build_server_from_examples(bootstrap_examples_root())

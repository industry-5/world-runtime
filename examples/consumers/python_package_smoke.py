import json
import os
from urllib import request

from world_runtime.sdk import WorldRuntimeSDKClient


def _get_json(url: str) -> dict:
    with request.urlopen(url, timeout=10.0) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    base_url = os.getenv("WORLD_RUNTIME_API_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
    api_token = os.getenv("WORLD_RUNTIME_API_TOKEN")

    health = _get_json(base_url + "/health")
    meta = _get_json(base_url + "/v1/meta")

    client = WorldRuntimeSDKClient(base_url=base_url, api_token=api_token)
    session = client.create_session()

    print(
        json.dumps(
            {
                "health": health,
                "meta": meta,
                "session": session,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

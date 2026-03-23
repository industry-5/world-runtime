from copy import deepcopy
from typing import Any, Dict, Protocol

class TransportPlugin(Protocol):
    provider: str

    def send(self, payload: Dict[str, Any], attempt: int, auth: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        ...


class MockWebhookTransportPlugin:
    provider = "mock.webhook"

    def send(self, payload: Dict[str, Any], attempt: int, auth: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = options.get("endpoint")
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise ValueError("mock.webhook requires options.endpoint")

        auth_mode = auth.get("type", "none")
        if auth_mode == "api_key":
            if not auth.get("api_key"):
                raise ValueError("mock.webhook api_key auth requires auth.api_key")
        elif auth_mode == "bearer":
            if not auth.get("token"):
                raise ValueError("mock.webhook bearer auth requires auth.token")
        elif auth_mode != "none":
            raise ValueError("unsupported mock.webhook auth.type: %s" % auth_mode)

        return {
            "ack": "delivered",
            "provider": self.provider,
            "endpoint": endpoint,
            "attempt": attempt,
            "auth_type": auth_mode,
            "external_action_type": payload.get("external_action_type"),
        }


class MockQueueTransportPlugin:
    provider = "mock.queue"

    def send(self, payload: Dict[str, Any], attempt: int, auth: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        queue = options.get("queue")
        if not isinstance(queue, str) or not queue.strip():
            raise ValueError("mock.queue requires options.queue")

        auth_mode = auth.get("type", "none")
        if auth_mode == "access_key":
            if not auth.get("access_key_id") or not auth.get("secret_access_key"):
                raise ValueError(
                    "mock.queue access_key auth requires auth.access_key_id and auth.secret_access_key"
                )
        elif auth_mode != "none":
            raise ValueError("unsupported mock.queue auth.type: %s" % auth_mode)

        return {
            "ack": "queued",
            "provider": self.provider,
            "queue": queue,
            "attempt": attempt,
            "auth_type": auth_mode,
            "external_action_type": payload.get("external_action_type"),
            "message": deepcopy(payload),
        }


class TransportPluginRegistry:
    def __init__(self) -> None:
        self._plugins: Dict[str, TransportPlugin] = {}

    @classmethod
    def with_defaults(cls) -> "TransportPluginRegistry":
        registry = cls()
        registry.register(MockWebhookTransportPlugin())
        registry.register(MockQueueTransportPlugin())
        return registry

    def register(self, plugin: TransportPlugin) -> None:
        self._plugins[plugin.provider] = plugin

    def resolve(self, provider: str) -> TransportPlugin:
        plugin = self._plugins.get(provider)
        if plugin is None:
            raise ValueError("transport provider not found: %s" % provider)
        return plugin

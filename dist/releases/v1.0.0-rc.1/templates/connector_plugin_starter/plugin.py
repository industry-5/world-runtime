from copy import deepcopy
from typing import Any, Dict


class __CONNECTOR_NAME_CLASS__TransportPlugin:
    provider = "__CONNECTOR_PROVIDER__"

    def send(self, payload: Dict[str, Any], attempt: int, auth: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = options.get("endpoint")
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise ValueError("__CONNECTOR_PROVIDER__ requires options.endpoint")

        token = auth.get("token")
        if not isinstance(token, str) or not token.strip():
            raise ValueError("__CONNECTOR_PROVIDER__ requires auth.token")

        return {
            "ack": "delivered",
            "provider": self.provider,
            "endpoint": endpoint,
            "attempt": attempt,
            "payload": deepcopy(payload),
        }

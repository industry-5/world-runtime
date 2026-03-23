from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from core.connector_state_store import (
    BaseConnectorStateStore,
    ConnectorPolicyDecisionRecord,
    DeadLetterRecord,
    InMemoryConnectorStateStore,
    SQLiteConnectorStateStore,
)
from core.connector_transports import TransportPluginRegistry


class TransientConnectorError(RuntimeError):
    """Retryable connector failure."""


class PermanentConnectorError(RuntimeError):
    """Non-retryable connector failure."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3

    @classmethod
    def from_config(cls, payload: Optional[Dict[str, Any]]) -> "RetryPolicy":
        if not payload:
            return cls()
        attempts = int(payload.get("max_attempts", 3))
        if attempts < 1:
            attempts = 1
        return cls(max_attempts=attempts)


@dataclass
class InboundConnectorConfig:
    connector_id: str
    event_type_map: Dict[str, str]
    retry: RetryPolicy


@dataclass
class OutboundConnectorConfig:
    connector_id: str
    action_type_map: Dict[str, str]
    retry: RetryPolicy


class ConnectorRuntime:
    def __init__(
        self,
        event_store: Any,
        state_store: Optional[BaseConnectorStateStore] = None,
        transport_registry: Optional[TransportPluginRegistry] = None,
    ) -> None:
        self.event_store = event_store
        self.state_store = state_store or self._build_default_state_store(event_store)
        self.transport_registry = transport_registry or TransportPluginRegistry.with_defaults()

    def run_inbound(
        self,
        config: InboundConnectorConfig,
        external_event: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        preprocessor: Optional[Callable[[Dict[str, Any], int], Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        key = self._resolve_idempotency_key(
            direction="inbound",
            connector_id=config.connector_id,
            payload=external_event,
            explicit_key=idempotency_key,
        )
        duplicate = self.state_store.get_idempotency(key)
        if duplicate is not None:
            return {
                "status": "duplicate",
                "direction": "inbound",
                "connector_id": config.connector_id,
                "idempotency_key": key,
                "result": deepcopy(duplicate),
            }

        external_type = external_event.get("event_type")
        mapped_event_type = config.event_type_map.get(external_type)
        if not mapped_event_type:
            return self._dead_letter(
                connector_id=config.connector_id,
                direction="inbound",
                idempotency_key=key,
                reason="unmapped_event_type",
                payload=external_event,
                attempts=1,
                last_error="event_type mapping not found: %s" % external_type,
            )

        attempts = 0
        last_error = ""
        for attempt in range(1, config.retry.max_attempts + 1):
            attempts = attempt
            try:
                transformed = deepcopy(external_event)
                if preprocessor is not None:
                    transformed = preprocessor(deepcopy(external_event), attempt)

                internal_event = {
                    "event_type": mapped_event_type,
                    "payload": deepcopy(transformed.get("payload", {})),
                    "metadata": {
                        "connector_id": config.connector_id,
                        "external_event_type": external_type,
                        "idempotency_key": key,
                    },
                }
                stream_id = "connector.%s.inbound.%s" % (config.connector_id, key)
                appended = self.event_store.append(stream_id, internal_event)
                result = {
                    "status": "completed",
                    "direction": "inbound",
                    "connector_id": config.connector_id,
                    "idempotency_key": key,
                    "attempts": attempts,
                    "offset": appended.get("offset"),
                    "stream_id": stream_id,
                    "mapped_event_type": mapped_event_type,
                }
                self.state_store.put_idempotency(key, "inbound", config.connector_id, result)
                return result
            except TransientConnectorError as exc:
                last_error = str(exc)
                if attempt >= config.retry.max_attempts:
                    break
            except PermanentConnectorError as exc:
                last_error = str(exc)
                break

        return self._dead_letter(
            connector_id=config.connector_id,
            direction="inbound",
            idempotency_key=key,
            reason="execution_failed",
            payload=external_event,
            attempts=attempts,
            last_error=last_error or "unknown inbound connector error",
        )

    def run_outbound(
        self,
        config: OutboundConnectorConfig,
        action: Dict[str, Any],
        transport: Optional[Callable[[Dict[str, Any], int], Dict[str, Any]]] = None,
        idempotency_key: Optional[str] = None,
        transport_plugin: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        key = self._resolve_idempotency_key(
            direction="outbound",
            connector_id=config.connector_id,
            payload=action,
            explicit_key=idempotency_key,
        )
        duplicate = self.state_store.get_idempotency(key)
        if duplicate is not None:
            return {
                "status": "duplicate",
                "direction": "outbound",
                "connector_id": config.connector_id,
                "idempotency_key": key,
                "result": deepcopy(duplicate),
            }

        action_type = action.get("action_type")
        mapped_action = config.action_type_map.get(action_type)
        if not mapped_action:
            return self._dead_letter(
                connector_id=config.connector_id,
                direction="outbound",
                idempotency_key=key,
                reason="unmapped_action_type",
                payload=action,
                attempts=1,
                last_error="action_type mapping not found: %s" % action_type,
            )

        resolved_transport = transport
        provider = None
        if transport_plugin is not None:
            provider = str(transport_plugin.get("provider", "")).strip()
            resolved_transport = self._transport_from_plugin(
                connector_id=config.connector_id,
                mapped_action_type=mapped_action,
                plugin_config=transport_plugin,
            )

        if resolved_transport is None:
            raise ValueError("transport callable or transport_plugin is required for outbound connector execution")

        attempts = 0
        last_error = ""
        for attempt in range(1, config.retry.max_attempts + 1):
            attempts = attempt
            payload = {
                "connector_id": config.connector_id,
                "external_action_type": mapped_action,
                "action": deepcopy(action),
                "idempotency_key": key,
                "attempt": attempt,
            }
            try:
                transport_response = resolved_transport(deepcopy(payload), attempt)
                result = {
                    "status": "completed",
                    "direction": "outbound",
                    "connector_id": config.connector_id,
                    "idempotency_key": key,
                    "attempts": attempts,
                    "mapped_action_type": mapped_action,
                    "transport_response": deepcopy(transport_response),
                }
                if provider:
                    result["transport_provider"] = provider
                self.state_store.put_idempotency(key, "outbound", config.connector_id, result)
                return result
            except TransientConnectorError as exc:
                last_error = str(exc)
                if attempt >= config.retry.max_attempts:
                    break
            except PermanentConnectorError as exc:
                last_error = str(exc)
                break

        return self._dead_letter(
            connector_id=config.connector_id,
            direction="outbound",
            idempotency_key=key,
            reason="execution_failed",
            payload=action,
            attempts=attempts,
            last_error=last_error or "unknown outbound connector error",
        )

    def list_dead_letters(
        self,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.state_store.list_dead_letters(connector_id=connector_id, direction=direction)

    def record_policy_decision(
        self,
        decision_id: str,
        connector_id: str,
        direction: str,
        idempotency_key: str,
        final_outcome: str,
        status: str,
        policy_report: Dict[str, Any],
        provider: Optional[str] = None,
        source: Optional[str] = None,
        approval_id: Optional[str] = None,
        execution_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = ConnectorPolicyDecisionRecord(
            decision_id=decision_id,
            connector_id=connector_id,
            direction=direction,
            idempotency_key=idempotency_key,
            final_outcome=final_outcome,
            status=status,
            policy_report=deepcopy(policy_report),
            provider=provider,
            source=source,
            approval_id=approval_id,
            execution_result=deepcopy(execution_result) if execution_result is not None else None,
            created_at=_utc_now(),
        )
        self.state_store.append_policy_decision(record)
        return {
            "decision_id": decision_id,
            "connector_id": connector_id,
            "direction": direction,
            "idempotency_key": idempotency_key,
            "final_outcome": final_outcome,
            "status": status,
            "provider": provider,
            "source": source,
            "approval_id": approval_id,
            "policy_report": deepcopy(policy_report),
            "execution_result": deepcopy(execution_result) if execution_result is not None else None,
            "created_at": record.created_at,
        }

    def list_policy_decisions(
        self,
        connector_id: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.state_store.list_policy_decisions(connector_id=connector_id, direction=direction)

    def get_policy_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        return self.state_store.get_policy_decision(decision_id)

    def get_dead_letter(self, dead_letter_id: str) -> Optional[Dict[str, Any]]:
        return self.state_store.get_dead_letter(dead_letter_id)

    def replay_dead_letter(
        self,
        dead_letter_id: str,
        inbound_config: Optional[InboundConnectorConfig] = None,
        outbound_config: Optional[OutboundConnectorConfig] = None,
        transport: Optional[Callable[[Dict[str, Any], int], Dict[str, Any]]] = None,
        preprocessor: Optional[Callable[[Dict[str, Any], int], Dict[str, Any]]] = None,
        payload_override: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        transport_plugin: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        dead_letter = self.state_store.get_dead_letter(dead_letter_id)
        if dead_letter is None:
            raise ValueError("dead letter not found: %s" % dead_letter_id)

        replay_key = idempotency_key or ("%s:replay:%s" % (dead_letter["idempotency_key"], _utc_now()))
        payload = deepcopy(payload_override) if payload_override is not None else deepcopy(dead_letter["payload"])

        if dead_letter["direction"] == "inbound":
            if inbound_config is None:
                raise ValueError("inbound_config is required to replay inbound dead letters")
            result = self.run_inbound(
                config=inbound_config,
                external_event=payload,
                idempotency_key=replay_key,
                preprocessor=preprocessor,
            )
        elif dead_letter["direction"] == "outbound":
            if outbound_config is None:
                raise ValueError("outbound_config is required to replay outbound dead letters")
            result = self.run_outbound(
                config=outbound_config,
                action=payload,
                transport=transport,
                idempotency_key=replay_key,
                transport_plugin=transport_plugin,
            )
        else:
            raise ValueError("unsupported dead letter direction: %s" % dead_letter["direction"])

        replay_status = "succeeded" if result.get("status") in {"completed", "duplicate"} else "failed"
        self.state_store.mark_dead_letter_replay(dead_letter_id, replay_status, result)

        return {
            "dead_letter_id": dead_letter_id,
            "replay_status": replay_status,
            "result": result,
        }

    def _resolve_idempotency_key(
        self,
        direction: str,
        connector_id: str,
        payload: Dict[str, Any],
        explicit_key: Optional[str],
    ) -> str:
        if explicit_key:
            return "%s:%s:%s" % (direction, connector_id, explicit_key)

        for field in ("idempotency_key", "external_id", "event_id", "action_id", "proposal_id", "decision_id"):
            value = payload.get(field)
            if isinstance(value, str) and value.strip():
                return "%s:%s:%s" % (direction, connector_id, value)

        fallback = "%s:%s:%s" % (
            direction,
            connector_id,
            repr(sorted(payload.items())),
        )
        return fallback

    def _next_dead_letter_id(self, connector_id: str) -> str:
        count = len(self.state_store.list_dead_letters()) + 1
        return "dlq.%s.%04d" % (connector_id, count)

    def _dead_letter(
        self,
        connector_id: str,
        direction: str,
        idempotency_key: str,
        reason: str,
        payload: Dict[str, Any],
        attempts: int,
        last_error: str,
    ) -> Dict[str, Any]:
        dead_letter_id = self._next_dead_letter_id(connector_id)
        entry = DeadLetterRecord(
            dead_letter_id=dead_letter_id,
            connector_id=connector_id,
            direction=direction,
            idempotency_key=idempotency_key,
            reason=reason,
            payload=deepcopy(payload),
            attempts=attempts,
            last_error=last_error,
            created_at=_utc_now(),
        )
        self.state_store.append_dead_letter(entry)
        return {
            "status": "dead_lettered",
            "direction": direction,
            "connector_id": connector_id,
            "idempotency_key": idempotency_key,
            "dead_letter_id": dead_letter_id,
            "attempts": attempts,
            "last_error": last_error,
            "reason": reason,
        }

    def _transport_from_plugin(
        self,
        connector_id: str,
        mapped_action_type: str,
        plugin_config: Dict[str, Any],
    ) -> Callable[[Dict[str, Any], int], Dict[str, Any]]:
        provider = str(plugin_config.get("provider", "")).strip()
        if not provider:
            raise PermanentConnectorError("transport_plugin.provider is required")

        plugin = self.transport_registry.resolve(provider)
        auth = dict(plugin_config.get("auth") or {})
        options = dict(plugin_config.get("options") or {})

        def _send(payload: Dict[str, Any], attempt: int) -> Dict[str, Any]:
            plugin_payload = {
                "connector_id": connector_id,
                "external_action_type": mapped_action_type,
                "action": deepcopy(payload.get("action", {})),
                "idempotency_key": payload.get("idempotency_key"),
                "attempt": attempt,
            }
            try:
                return plugin.send(plugin_payload, attempt, auth, options)
            except TransientConnectorError:
                raise
            except PermanentConnectorError:
                raise
            except ValueError as exc:
                raise PermanentConnectorError(str(exc)) from exc
            except Exception as exc:
                raise TransientConnectorError(str(exc)) from exc

        return _send

    def _build_default_state_store(self, event_store: Any) -> BaseConnectorStateStore:
        database_path = getattr(event_store, "database_path", None)
        if database_path is None:
            return InMemoryConnectorStateStore()

        migrations_dir = getattr(event_store, "migrations_dir", None)
        return SQLiteConnectorStateStore(Path(database_path), migrations_dir=migrations_dir)

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Tuple


class SupplyOpsIngressPreparer:
    def fixture_dir(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "supply_ops" / "fixtures" / "ingress"

    def load_fixture_envelope(self, repo_root: Path, fixture_name: str) -> Dict[str, Any]:
        fixture_path = self.fixture_dir(repo_root) / f"{fixture_name}.json"
        with fixture_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def extract_signal_bundle(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        _, _, _, metadata, signal_bundle = self._validated_sections(envelope)
        self._require_string(metadata, "envelope_id")
        return deepcopy(signal_bundle)

    def extract_metadata(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        connector, governance, trace, metadata, _ = self._validated_sections(envelope)

        return {
            "envelope_id": self._require_string(metadata, "envelope_id"),
            "envelope_type": self._require_string(metadata, "envelope_type"),
            "schema_version": self._require_string(metadata, "schema_version"),
            "received_at": self._require_string(metadata, "received_at"),
            "connector_id": self._require_string(connector, "connector_id"),
            "direction": self._require_string(connector, "direction"),
            "provider": self._require_string(connector, "provider"),
            "source": self._require_string(connector, "source"),
            "external_message_id": self._require_string(trace, "external_message_id"),
            "correlation_id": self._require_string(trace, "correlation_id"),
            "governance": {
                "translation_required": self._require_bool(
                    governance, "translation_required"
                ),
                "mutates_runtime_state": self._require_bool(
                    governance, "mutates_runtime_state"
                ),
                "translation_boundary": self._require_string(
                    governance, "translation_boundary"
                ),
            },
        }

    def _validated_sections(
        self, envelope: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        connector = self._require_mapping(envelope, "connector")
        governance = self._require_mapping(envelope, "governance")
        trace = self._require_mapping(envelope, "trace")
        signal_bundle = self._require_mapping(envelope, "signal_bundle")

        envelope_type = self._require_string(envelope, "envelope_type")
        if envelope_type != "supply_ops_connector_signal":
            raise ValueError(
                "envelope_type must be supply_ops_connector_signal"
            )

        direction = self._require_string(connector, "direction")
        if direction != "inbound":
            raise ValueError("connector.direction must be 'inbound'")

        if self._require_bool(governance, "translation_required") is not True:
            raise ValueError("governance.translation_required must be true")
        if self._require_bool(governance, "mutates_runtime_state") is not False:
            raise ValueError("governance.mutates_runtime_state must be false")

        boundary = self._require_string(governance, "translation_boundary")
        if boundary != "proposal_only":
            raise ValueError("governance.translation_boundary must be proposal_only")

        self._require_string(envelope, "envelope_id")
        self._require_string(envelope, "schema_version")
        self._require_string(envelope, "received_at")
        self._require_string(connector, "connector_id")
        self._require_string(connector, "provider")
        self._require_string(connector, "source")
        self._require_string(trace, "external_message_id")
        self._require_string(trace, "correlation_id")

        return connector, governance, trace, envelope, signal_bundle

    def _require_mapping(self, data: Dict[str, Any], field: str) -> Dict[str, Any]:
        value = data.get(field)
        if not isinstance(value, dict):
            raise ValueError("%s must be an object" % field)
        return value

    def _require_string(self, data: Dict[str, Any], field: str) -> str:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("%s must be a non-empty string" % field)
        return value

    def _require_bool(self, data: Dict[str, Any], field: str) -> bool:
        value = data.get(field)
        if not isinstance(value, bool):
            raise ValueError("%s must be a boolean" % field)
        return value

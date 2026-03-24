import json
from pathlib import Path
from typing import Any, Dict

from adapters.supply_ops.ingress import SupplyOpsIngressPreparer


class SupplyOpsTranslator:
    def fixture_dir(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "supply_ops" / "fixtures"

    def load_fixture_bundle(self, repo_root: Path, fixture_name: str) -> Dict[str, Any]:
        fixture_path = self.fixture_dir(repo_root) / "inbound" / f"{fixture_name}.json"
        with fixture_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def translate_fixture_bundle(self, repo_root: Path, fixture_name: str) -> Dict[str, Any]:
        return self.translate(self.load_fixture_bundle(repo_root, fixture_name))

    def load_ingress_envelope_fixture(
        self, repo_root: Path, fixture_name: str
    ) -> Dict[str, Any]:
        return SupplyOpsIngressPreparer().load_fixture_envelope(repo_root, fixture_name)

    def translate_ingress_fixture(self, repo_root: Path, fixture_name: str) -> Dict[str, Any]:
        return self.translate_ingress_envelope(
            self.load_ingress_envelope_fixture(repo_root, fixture_name)
        )

    def translate_ingress_envelope(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        signal_bundle = SupplyOpsIngressPreparer().extract_signal_bundle(envelope)
        return self.translate(signal_bundle)

    def translate(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        context = self._require_mapping(bundle, "translation_context")
        order_signal = self._require_mapping(bundle, "order_signal")
        inventory_signal = self._require_mapping(bundle, "inventory_signal")
        capacity_signal = self._require_mapping(bundle, "capacity_signal")
        lane_signal = self._require_mapping(bundle, "lane_signal")
        simulation_signal = self._require_mapping(bundle, "simulation_signal")

        requested_units = self._require_int(order_signal, "requested_units")
        at_risk_units = self._require_int(order_signal, "at_risk_units")
        allocatable_units = self._require_int(inventory_signal, "allocatable_units")
        on_hand_units = self._require_int(inventory_signal, "on_hand_units")
        daily_demand_units = self._require_int(inventory_signal, "daily_demand_units")
        available_capacity_units = self._require_int(capacity_signal, "available_units")
        expedite_cost_delta_percent = self._require_number(
            lane_signal, "expedite_cost_delta_percent"
        )

        reallocation_units = min(at_risk_units, allocatable_units, available_capacity_units)
        remaining_late_units = max(at_risk_units - reallocation_units, 0)
        projected_inventory_days = self._normalize_number(
            (on_hand_units - reallocation_units) / daily_demand_units
        )

        projected_fill_rate_percent = simulation_signal.get("projected_fill_rate_percent")
        if projected_fill_rate_percent is None:
            if requested_units <= 0:
                raise ValueError("order_signal.requested_units must be positive")
            projected_fill_rate_percent = round(
                ((requested_units - remaining_late_units) / requested_units) * 100
            )

        lane_id = self._require_string(lane_signal, "lane_id")
        commitment_id = self._require_string(order_signal, "commitment_id")
        inventory_position_id = self._require_string(
            inventory_signal, "inventory_position_id"
        )
        capacity_bucket_id = self._require_string(capacity_signal, "capacity_bucket_id")
        proposal_suffix = self._require_string(context, "proposal_suffix")
        service_level = self._require_string(lane_signal, "service_level")

        action_type = (
            "rebalance_inventory_and_expedite_commitment"
            if service_level == "expedited"
            else "rebalance_inventory_and_recover_commitment"
        )

        return {
            "proposal_id": f"proposal.supply-ops.{proposal_suffix}",
            "proposal_type": context.get("proposal_type", "commitment_recovery"),
            "status": "submitted",
            "proposer": {
                "actor_id": self._require_string(context, "proposer_actor_id"),
                "actor_type": context.get("proposer_actor_type", "agent"),
            },
            "target_entities": [
                {
                    "entity_id": commitment_id,
                    "entity_type": "order_commitment",
                },
                {
                    "entity_id": inventory_position_id,
                    "entity_type": "inventory_position",
                },
                {
                    "entity_id": capacity_bucket_id,
                    "entity_type": "capacity_bucket",
                },
                {
                    "entity_id": lane_id,
                    "entity_type": "fulfillment_lane",
                },
            ],
            "proposed_action": {
                "action_type": action_type,
                "parameters": {
                    "commitment_id": commitment_id,
                    "source_inventory_id": inventory_position_id,
                    "reserve_capacity_id": capacity_bucket_id,
                    "lane_id": lane_id,
                    "reallocation_units": reallocation_units,
                    "projected_fill_rate_percent": projected_fill_rate_percent,
                    "projected_post_action_inventory_days": projected_inventory_days,
                    "expedite_cost_delta_percent": expedite_cost_delta_percent,
                    "simulation_completed": self._require_bool(
                        simulation_signal, "completed"
                    ),
                    "simulation_id": self._require_string(
                        simulation_signal, "simulation_id"
                    ),
                },
            },
            "justification": bundle.get(
                "justification",
                (
                    "Recover at-risk commitment %s using translated ERP/WMS signals."
                    % commitment_id
                ),
            ),
            "created_at": self._require_string(context, "created_at"),
        }

    def _normalize_number(self, value: float):
        rounded = round(value, 1)
        if rounded.is_integer():
            return int(rounded)
        return rounded

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

    def _require_int(self, data: Dict[str, Any], field: str) -> int:
        value = data.get(field)
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("%s must be an integer" % field)
        return value

    def _require_number(self, data: Dict[str, Any], field: str):
        value = data.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("%s must be numeric" % field)
        return value

    def _require_bool(self, data: Dict[str, Any], field: str) -> bool:
        value = data.get(field)
        if not isinstance(value, bool):
            raise ValueError("%s must be a boolean" % field)
        return value

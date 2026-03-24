from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from adapters.base import DomainAdapter


STANDARD_PUBLIC_PACKAGE_FILENAMES = ("README.md",)

STANDARD_NON_OVERLAY_BUNDLE_FILENAMES = (
    "README.md",
    "entities.json",
    "relationships.json",
    "events.json",
    "proposal.json",
    "decision.json",
    "simulation.json",
    "policy.json",
    "rule.json",
    "projection.json",
)

STANDARD_OVERLAY_BUNDLE_FILENAMES = STANDARD_NON_OVERLAY_BUNDLE_FILENAMES + (
    "host_bindings.json",
)


@dataclass(frozen=True)
class PublicAdapterTrack:
    code: str
    package_slug: str
    adapter_id: str
    scenario_slug: str
    runtime_adapter_import: str | None = None
    overlay: bool = False
    proposal_collection_files: tuple[str, ...] = ()
    supplemental_bundle_files: tuple[str, ...] = ()

    def package_dir(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / self.package_slug

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / self.scenario_slug

    def expected_package_files(self) -> tuple[str, ...]:
        return STANDARD_PUBLIC_PACKAGE_FILENAMES

    def expected_bundle_files(self) -> tuple[str, ...]:
        if self.overlay:
            return STANDARD_OVERLAY_BUNDLE_FILENAMES
        return STANDARD_NON_OVERLAY_BUNDLE_FILENAMES

    def all_bundle_files(self) -> tuple[str, ...]:
        ordered = list(self.expected_bundle_files()) + list(self.supplemental_bundle_files)
        return tuple(dict.fromkeys(ordered))

    def load_runtime_adapter(self) -> DomainAdapter | None:
        if self.runtime_adapter_import is None:
            return None

        module_name, class_name = self.runtime_adapter_import.split(":")
        adapter_cls = getattr(import_module(module_name), class_name)
        return adapter_cls()


PUBLIC_ADAPTER_TRACKS = (
    PublicAdapterTrack(
        code="SN",
        package_slug="supply_network",
        adapter_id="adapter-supply-network",
        scenario_slug="supply-network-mini",
        runtime_adapter_import="adapters.supply_network.adapter:SupplyNetworkAdapter",
        proposal_collection_files=("reroute_options.json",),
        supplemental_bundle_files=("reroute_options.json",),
    ),
    PublicAdapterTrack(
        code="AT",
        package_slug="air_traffic",
        adapter_id="adapter-air-traffic",
        scenario_slug="air-traffic-mini",
        runtime_adapter_import="adapters.air_traffic.adapter:AirTrafficAdapter",
        proposal_collection_files=("conflicting_proposals.json",),
        supplemental_bundle_files=("conflicting_proposals.json",),
    ),
    PublicAdapterTrack(
        code="SS",
        package_slug="semantic_system",
        adapter_id="adapter-semantic-system",
        scenario_slug="semantic-system-mini",
        runtime_adapter_import="adapters.semantic_system.adapter:SemanticSystemAdapter",
        proposal_collection_files=("conflicting_proposals.json",),
        supplemental_bundle_files=("conflicting_proposals.json",),
    ),
    PublicAdapterTrack(
        code="PG",
        package_slug="power_grid",
        adapter_id="adapter-power-grid",
        scenario_slug="power-grid-mini",
        runtime_adapter_import="adapters.power_grid.adapter:PowerGridAdapter",
        proposal_collection_files=("contingency_options.json",),
        supplemental_bundle_files=("contingency_options.json",),
    ),
    PublicAdapterTrack(
        code="CO",
        package_slug="city_ops",
        adapter_id="adapter-city-ops",
        scenario_slug="city-ops-mini",
        runtime_adapter_import="adapters.city_ops.adapter:CityOpsAdapter",
        proposal_collection_files=("coordination_options.json",),
        supplemental_bundle_files=("coordination_options.json",),
    ),
    PublicAdapterTrack(
        code="LS",
        package_slug="lab_science",
        adapter_id="adapter-lab-science",
        scenario_slug="lab-science-mini",
        runtime_adapter_import="adapters.lab_science.adapter:LabScienceAdapter",
        proposal_collection_files=("release_options.json",),
        supplemental_bundle_files=("release_options.json",),
    ),
    PublicAdapterTrack(
        code="MM",
        package_slug="market_micro",
        adapter_id="adapter-market-micro",
        scenario_slug="market-micro-mini",
        runtime_adapter_import="adapters.market_micro.adapter:MarketMicroAdapter",
        proposal_collection_files=("risk_options.json",),
        supplemental_bundle_files=("risk_options.json",),
    ),
    PublicAdapterTrack(
        code="MPG",
        package_slug="multiplayer_game",
        adapter_id="adapter-multiplayer-game",
        scenario_slug="multiplayer-game-mini",
        runtime_adapter_import="adapters.multiplayer_game.adapter:MultiplayerGameAdapter",
        proposal_collection_files=("resolution_options.json",),
        supplemental_bundle_files=("resolution_options.json",),
    ),
    PublicAdapterTrack(
        code="AV",
        package_slug="autonomous_vehicle",
        adapter_id="adapter-autonomous-vehicle",
        scenario_slug="autonomous-vehicle-mini",
        runtime_adapter_import="adapters.autonomous_vehicle.adapter:AutonomousVehicleAdapter",
        proposal_collection_files=("maneuver_options.json",),
        supplemental_bundle_files=("maneuver_options.json",),
    ),
    PublicAdapterTrack(
        code="MA",
        package_slug="multi_agent_ai",
        adapter_id="adapter-multi-agent-ai",
        scenario_slug="multi-agent-ai-mini",
        runtime_adapter_import="adapters.multi_agent_ai.adapter:MultiAgentAIAdapter",
        proposal_collection_files=("branch_options.json",),
        supplemental_bundle_files=("branch_options.json",),
    ),
    PublicAdapterTrack(
        code="OAW",
        package_slug="open_agent_world",
        adapter_id="adapter-open-agent-world",
        scenario_slug="open-agent-world-mini",
        runtime_adapter_import="adapters.open_agent_world.adapter:OpenAgentWorldAdapter",
        proposal_collection_files=("intervention_options.json",),
        supplemental_bundle_files=("intervention_options.json",),
    ),
    PublicAdapterTrack(
        code="DT",
        package_slug="digital_twin",
        adapter_id="adapter-digital-twin",
        scenario_slug="digital-twin-mini",
        runtime_adapter_import="adapters.digital_twin.adapter:DigitalTwinAdapter",
        overlay=True,
        proposal_collection_files=("overlay_options.json",),
        supplemental_bundle_files=("overlay_options.json",),
    ),
)


def public_adapter_tracks() -> tuple[PublicAdapterTrack, ...]:
    return PUBLIC_ADAPTER_TRACKS


def implemented_public_adapter_tracks() -> tuple[PublicAdapterTrack, ...]:
    return tuple(track for track in PUBLIC_ADAPTER_TRACKS if track.runtime_adapter_import is not None)


def validate_public_package_checklist(track: PublicAdapterTrack, repo_root: Path) -> list[str]:
    package_dir = track.package_dir(repo_root)
    if not package_dir.exists():
        return [f"missing package directory: {package_dir}"]

    errors = []
    for filename in track.expected_package_files():
        file_path = package_dir / filename
        if not file_path.exists():
            errors.append(f"missing package checklist file: {file_path}")
    return errors


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_proposals(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [payload]
    return []


def _validate_entity_refs(
    payload: dict[str, Any],
    entity_ids: set[str],
    *,
    source_name: str,
    key_name: str,
) -> list[str]:
    refs = payload.get(key_name, [])
    if not isinstance(refs, list):
        return [f"{source_name} {key_name} must be a list"]

    errors = []
    for index, ref in enumerate(refs):
        if not isinstance(ref, dict):
            errors.append(f"{source_name} {key_name}[{index}] must be an object")
            continue
        entity_id = ref.get("entity_id")
        if entity_id not in entity_ids:
            errors.append(
                f"{source_name} {key_name}[{index}] references unknown entity_id: {entity_id}"
            )
    return errors


def _validate_target_entity_refs(
    payload: dict[str, Any],
    entity_ids: set[str],
    *,
    source_name: str,
) -> list[str]:
    return _validate_entity_refs(
        payload,
        entity_ids,
        source_name=source_name,
        key_name="target_entities",
    )


def _load_entity_ids_for_track(track: PublicAdapterTrack, repo_root: Path) -> tuple[set[str], list[str]]:
    entities_path = track.scenario_dir(repo_root) / "entities.json"
    try:
        entities = load_json(entities_path)
    except (OSError, json.JSONDecodeError) as exc:
        return set(), [f"could not load {entities_path}: {exc}"]

    if not isinstance(entities, list):
        return set(), [f"{entities_path} must be a list"]

    entity_ids = {
        entity.get("entity_id")
        for entity in entities
        if isinstance(entity, dict) and entity.get("entity_id") is not None
    }
    return entity_ids, []


def _validate_overlay_host_bindings(
    track: PublicAdapterTrack,
    repo_root: Path,
    bundle_payloads: dict[str, Any],
    overlay_entity_ids: set[str],
) -> list[str]:
    host_bindings = bundle_payloads.get("host_bindings.json")
    if not isinstance(host_bindings, list):
        return ["host_bindings.json must be a list"]

    host_tracks_by_adapter_id = {
        host_track.adapter_id: host_track
        for host_track in implemented_public_adapter_tracks()
        if host_track.adapter_id != track.adapter_id and not host_track.overlay
    }

    errors = []
    host_entity_cache: dict[str, set[str]] = {}

    for index, binding in enumerate(host_bindings):
        source_name = f"host_bindings.json[{index}]"
        if not isinstance(binding, dict):
            errors.append(f"{source_name} must be an object")
            continue

        host_adapter_id = binding.get("host_adapter_id")
        if host_adapter_id not in host_tracks_by_adapter_id:
            errors.append(f"{source_name} references unknown host_adapter_id: {host_adapter_id}")
            continue

        host_track = host_tracks_by_adapter_id[host_adapter_id]
        if binding.get("host_scenario_slug") != host_track.scenario_slug:
            errors.append(
                f"{source_name} host_scenario_slug does not match {host_adapter_id}: "
                f"{binding.get('host_scenario_slug')}"
            )

        overlay_entity_id = binding.get("overlay_entity_id")
        if overlay_entity_id not in overlay_entity_ids:
            errors.append(
                f"{source_name} references unknown overlay_entity_id: {overlay_entity_id}"
            )

        cached_host_ids = host_entity_cache.get(host_adapter_id)
        if cached_host_ids is None:
            cached_host_ids, load_errors = _load_entity_ids_for_track(host_track, repo_root)
            host_entity_cache[host_adapter_id] = cached_host_ids
            errors.extend(load_errors)

        errors.extend(
            _validate_entity_refs(
                binding,
                host_entity_cache.get(host_adapter_id, set()),
                source_name=source_name,
                key_name="host_entities",
            )
        )

    return errors


def validate_standard_public_scenario_bundle(
    track: PublicAdapterTrack,
    repo_root: Path,
) -> list[str]:
    scenario_dir = track.scenario_dir(repo_root)
    if not scenario_dir.exists():
        return [f"missing scenario bundle directory: {scenario_dir}"]

    errors = []
    for filename in track.all_bundle_files():
        file_path = scenario_dir / filename
        if not file_path.exists():
            errors.append(f"missing scenario bundle file: {file_path}")

    readme_path = scenario_dir / "README.md"
    if readme_path.exists() and not readme_path.read_text(encoding="utf-8").strip():
        errors.append(f"empty scenario bundle README: {readme_path}")

    if errors:
        return errors

    bundle_payloads: dict[str, Any] = {}
    for filename in track.all_bundle_files():
        if not filename.endswith(".json"):
            continue
        file_path = scenario_dir / filename
        try:
            bundle_payloads[filename] = load_json(file_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"could not load {file_path}: {exc}")

    if errors:
        return errors

    entities = bundle_payloads.get("entities.json")
    relationships = bundle_payloads.get("relationships.json")
    proposal = bundle_payloads.get("proposal.json")
    decision = bundle_payloads.get("decision.json")
    simulation = bundle_payloads.get("simulation.json")

    if not isinstance(entities, list):
        errors.append("entities.json must be a list")
        return errors
    if not isinstance(relationships, list):
        errors.append("relationships.json must be a list")
        return errors
    if not isinstance(proposal, dict):
        errors.append("proposal.json must be an object")
        return errors
    if not isinstance(decision, dict):
        errors.append("decision.json must be an object")
        return errors
    if not isinstance(simulation, dict):
        errors.append("simulation.json must be an object")
        return errors

    entity_ids = {
        entity.get("entity_id")
        for entity in entities
        if isinstance(entity, dict) and entity.get("entity_id") is not None
    }

    for index, rel in enumerate(relationships):
        if not isinstance(rel, dict):
            errors.append(f"relationships.json[{index}] must be an object")
            continue
        from_entity = rel.get("from_entity", {})
        to_entity = rel.get("to_entity", {})
        if not isinstance(from_entity, dict):
            errors.append(f"relationships.json[{index}].from_entity must be an object")
        elif from_entity.get("entity_id") not in entity_ids:
            errors.append(
                "relationships.json[%d].from_entity references unknown entity_id: %s"
                % (index, from_entity.get("entity_id"))
            )
        if not isinstance(to_entity, dict):
            errors.append(f"relationships.json[{index}].to_entity must be an object")
        elif to_entity.get("entity_id") not in entity_ids:
            errors.append(
                "relationships.json[%d].to_entity references unknown entity_id: %s"
                % (index, to_entity.get("entity_id"))
            )

    errors.extend(
        _validate_target_entity_refs(proposal, entity_ids, source_name="proposal.json")
    )

    if track.overlay:
        errors.extend(
            _validate_overlay_host_bindings(track, repo_root, bundle_payloads, entity_ids)
        )

    primary_proposal_id = proposal.get("proposal_id")
    if primary_proposal_id is None:
        errors.append("proposal.json is missing proposal_id")
    proposal_ids = {primary_proposal_id} if primary_proposal_id is not None else set()

    for filename in track.proposal_collection_files:
        payload = bundle_payloads.get(filename)
        for index, candidate in enumerate(_normalize_proposals(payload)):
            errors.extend(
                _validate_target_entity_refs(
                    candidate,
                    entity_ids,
                    source_name=f"{filename}[{index}]",
                )
            )
            proposal_id = candidate.get("proposal_id")
            if proposal_id is None:
                errors.append(f"{filename}[{index}] is missing proposal_id")
                continue
            proposal_ids.add(proposal_id)

    if decision.get("selected_proposal_id") != primary_proposal_id:
        errors.append(
            "decision.json selected_proposal_id does not match proposal.json proposal_id"
        )

    alternatives = decision.get("alternatives_considered", [])
    if alternatives is not None and not isinstance(alternatives, list):
        errors.append("decision.json alternatives_considered must be a list when present")
    elif isinstance(alternatives, list):
        for index, alternative in enumerate(alternatives):
            if not isinstance(alternative, dict):
                errors.append(f"decision.json alternatives_considered[{index}] must be an object")
                continue
            proposal_id = alternative.get("proposal_id")
            if proposal_id not in proposal_ids:
                errors.append(
                    "decision.json alternatives_considered[%d] references unknown proposal_id: %s"
                    % (index, proposal_id)
                )

    simulation_inputs = simulation.get("inputs", {})
    if simulation_inputs is not None and not isinstance(simulation_inputs, dict):
        errors.append("simulation.json inputs must be an object when present")
    elif isinstance(simulation_inputs, dict):
        conflicting_proposals = simulation_inputs.get("conflicting_proposals")
        if conflicting_proposals is not None and not isinstance(conflicting_proposals, list):
            errors.append("simulation.json inputs.conflicting_proposals must be a list")
        elif isinstance(conflicting_proposals, list):
            for index, proposal_id in enumerate(conflicting_proposals):
                if proposal_id not in proposal_ids:
                    errors.append(
                        "simulation.json inputs.conflicting_proposals[%d] references unknown proposal_id: %s"
                        % (index, proposal_id)
                    )

    outcomes = simulation.get("outcomes", {})
    if outcomes is not None and not isinstance(outcomes, dict):
        errors.append("simulation.json outcomes must be an object when present")
    elif isinstance(outcomes, dict):
        recommended_proposal_id = outcomes.get("recommended_proposal_id")
        if recommended_proposal_id is not None and recommended_proposal_id not in proposal_ids:
            errors.append(
                "simulation.json outcomes.recommended_proposal_id references unknown proposal_id: %s"
                % recommended_proposal_id
            )

    return errors

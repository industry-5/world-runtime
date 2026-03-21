from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


def upsert_provenance_record(
    provenance_state: Dict[str, Any],
    artifact_type: str,
    artifact_id: str,
    record: Dict[str, Any],
) -> Dict[str, Any]:
    artifacts = provenance_state.setdefault("artifacts", {})
    key = "%s:%s" % (artifact_type, artifact_id)
    artifacts[key] = deepcopy(record)
    return deepcopy(artifacts[key])


def build_scenario_provenance(
    scenario: Dict[str, Any],
    scenario_path: Optional[str],
    session_id: str,
) -> Dict[str, Any]:
    metadata = scenario.get("metadata", {}) if isinstance(scenario.get("metadata"), dict) else {}
    lineage = []
    bundle_id = metadata.get("template_bundle_id")
    if bundle_id:
        lineage.append(
            {
                "artifact_type": "template_bundle",
                "artifact_id": bundle_id,
                "bundle_version_hash": metadata.get("bundle_version_hash"),
                "template_id": metadata.get("template_id"),
            }
        )
    return {
        "artifact_type": "scenario",
        "artifact_id": scenario["scenario_id"],
        "session_id": session_id,
        "scenario_path": scenario_path,
        "lineage": lineage,
        "metadata": {
            "baseline_version": scenario.get("baseline_version"),
            "template_bundle_id": bundle_id,
            "template_id": metadata.get("template_id"),
            "bundle_version_hash": metadata.get("bundle_version_hash"),
        },
        "evidence_refs": [],
    }


def build_proposal_provenance(proposal: Dict[str, Any], scenario_id: Optional[str]) -> Dict[str, Any]:
    return {
        "artifact_type": "proposal",
        "artifact_id": proposal["proposal_id"],
        "lineage": ([{"artifact_type": "scenario", "artifact_id": scenario_id}] if scenario_id else []),
        "metadata": {
            "author_actor_id": proposal.get("author_actor_id"),
            "status": proposal.get("status"),
            "assumptions": deepcopy(proposal.get("assumptions", [])),
        },
        "evidence_refs": deepcopy(proposal.get("evidence_refs", [])),
    }


def build_annotation_provenance(annotation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_type": "annotation",
        "artifact_id": annotation["annotation_id"],
        "lineage": [
            {
                "artifact_type": annotation.get("target_type"),
                "artifact_id": annotation.get("target_id"),
            }
        ],
        "metadata": {
            "annotation_type": annotation.get("annotation_type"),
            "author_actor_id": annotation.get("author_actor_id"),
            "status": annotation.get("status"),
        },
        "evidence_refs": deepcopy(annotation.get("evidence_refs", [])),
    }


def build_branch_provenance(
    branch_id: str,
    source_branch_id: Optional[str],
    scenario_id: Optional[str],
    proposal_id: Optional[str] = None,
    turn_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    lineage: List[Dict[str, Any]] = []
    if scenario_id:
        lineage.append({"artifact_type": "scenario", "artifact_id": scenario_id})
    if source_branch_id:
        lineage.append({"artifact_type": "branch", "artifact_id": source_branch_id})
    if proposal_id:
        lineage.append({"artifact_type": "proposal", "artifact_id": proposal_id})
    return {
        "artifact_type": "branch",
        "artifact_id": branch_id,
        "lineage": lineage,
        "metadata": {
            "source_branch_id": source_branch_id,
            "policy_outcome": (turn_result or {}).get("policy_outcome"),
            "turn": (turn_result or {}).get("turn"),
        },
        "evidence_refs": [],
    }


def inspect_provenance(
    provenance_state: Dict[str, Any],
    artifact_type: Optional[str] = None,
    artifact_id: Optional[str] = None,
) -> Dict[str, Any]:
    artifacts = provenance_state.get("artifacts", {})
    if artifact_type and artifact_id:
        key = "%s:%s" % (artifact_type, artifact_id)
        record = artifacts.get(key)
        if record is None:
            raise ValueError("unknown provenance artifact: %s" % key)
        return {"artifact": deepcopy(record)}

    listed = []
    for key in sorted(artifacts.keys()):
        record = artifacts[key]
        if artifact_type and record.get("artifact_type") != artifact_type:
            continue
        listed.append(deepcopy(record))
    return {"artifacts": listed, "count": len(listed)}

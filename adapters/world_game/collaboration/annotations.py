from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


ANNOTATION_TYPES = [
    "risk",
    "opportunity",
    "assumption",
    "disagreement",
    "evidence_gap",
    "facilitator_note",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_annotation_record(
    annotation_id: str,
    annotation_type: str,
    actor_id: Optional[str],
    target_type: str,
    target_id: str,
    body: str,
    evidence_refs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    normalized_type = str(annotation_type)
    if normalized_type not in ANNOTATION_TYPES:
        raise ValueError("unknown annotation_type: %s" % annotation_type)
    timestamp = _utc_now()
    return {
        "annotation_id": str(annotation_id),
        "annotation_type": normalized_type,
        "author_actor_id": actor_id,
        "target_type": str(target_type),
        "target_id": str(target_id),
        "body": str(body).strip(),
        "status": "active",
        "evidence_refs": deepcopy(evidence_refs or []),
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def update_annotation_record(annotation: Dict[str, Any], body: Optional[str], evidence_refs: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    if annotation.get("status") == "archived":
        raise ValueError("annotation %s is archived" % annotation.get("annotation_id"))
    if body is not None:
        annotation["body"] = str(body).strip()
    if evidence_refs is not None:
        annotation["evidence_refs"] = deepcopy(evidence_refs)
    annotation["updated_at"] = _utc_now()
    return deepcopy(annotation)


def archive_annotation(annotation: Dict[str, Any], actor_id: Optional[str]) -> Dict[str, Any]:
    annotation["status"] = "archived"
    annotation["archived_by_actor_id"] = actor_id
    annotation["updated_at"] = _utc_now()
    return deepcopy(annotation)


def list_annotations(
    annotations_by_id: Dict[str, Dict[str, Any]],
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    include_archived: bool = False,
) -> List[Dict[str, Any]]:
    records = []
    for annotation_id in sorted(annotations_by_id.keys()):
        record = annotations_by_id[annotation_id]
        if not include_archived and record.get("status") == "archived":
            continue
        if target_type and record.get("target_type") != target_type:
            continue
        if target_id and record.get("target_id") != target_id:
            continue
        records.append(deepcopy(record))
    return records

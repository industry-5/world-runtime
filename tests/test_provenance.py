from core.provenance import (
    canonical_json,
    normalize_evidence_ref,
    redact_sensitive_payload,
    stable_fingerprint,
)


def test_redact_sensitive_payload_masks_nested_keys():
    payload = {
        "token": "abc",
        "nested": {
            "authorization": "Bearer abc",
            "safe": "value",
        },
        "list_items": [{"api_key": "k1"}, {"name": "ok"}],
    }

    redacted, report = redact_sensitive_payload(payload)

    assert report["redacted"] is True
    assert redacted["token"] == "[REDACTED]"
    assert redacted["nested"]["authorization"] == "[REDACTED]"
    assert redacted["list_items"][0]["api_key"] == "[REDACTED]"
    assert redacted["nested"]["safe"] == "value"


def test_stable_fingerprint_is_order_insensitive_for_dict_keys():
    left = {"b": 2, "a": 1}
    right = {"a": 1, "b": 2}

    assert canonical_json(left) == canonical_json(right)
    assert stable_fingerprint(left) == stable_fingerprint(right)


def test_normalize_evidence_ref_shape():
    evidence = normalize_evidence_ref(
        evidence_type="event",
        ref_id="evt.001",
        summary="Example evidence",
        stage="proposal",
        attributes={"source": "tests"},
    )

    assert evidence["evidence_type"] == "event"
    assert evidence["ref_id"] == "evt.001"
    assert evidence["stage"] == "proposal"
    assert evidence["attributes"]["source"] == "tests"

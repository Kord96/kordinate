"""Common helpers shared across fact-family extractors and fact consumers."""

from __future__ import annotations

from typing import Any


def line_number_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, max(offset, 0)) + 1


def unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = str(value or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def make_fact_ref(target_id: str, label: str) -> dict[str, str] | None:
    target = str(target_id or "").strip()
    rel_label = str(label or "").strip()
    if not target or not rel_label:
        return None
    return {"type": "fact_ref", "label": rel_label, "target_id": target}


def make_doc_ref(target_path: str, label: str) -> dict[str, str] | None:
    path = str(target_path or "").strip()
    rel_label = str(label or "").strip()
    if not path or not rel_label:
        return None
    return {"type": "doc_ref", "label": rel_label, "target_path": path}


def make_question_ref(question_id: str, label: str = "review_question") -> dict[str, str] | None:
    qid = str(question_id or "").strip()
    rel_label = str(label or "").strip()
    if not qid or not rel_label:
        return None
    return {"type": "question_ref", "label": rel_label, "question_id": qid}


def make_entity_ref(namespace: str, target_key: str, label: str = "related_to") -> dict[str, str] | None:
    ns = str(namespace or "").strip()
    key = str(target_key or "").strip()
    rel_label = str(label or "").strip()
    if not ns or not key or not rel_label:
        return None
    return {"type": "entity_ref", "label": rel_label, "namespace": ns, "target_key": key}


def fact_payload(record: dict[str, Any]) -> dict[str, Any]:
    payload = record.get("fact")
    if isinstance(payload, dict):
        return payload
    payload = record.get("raw_evidence")
    if isinstance(payload, dict):
        normalized = dict(payload)
        kind = str(record.get("kind") or "").strip()
        if kind and "kind" not in normalized:
            normalized["kind"] = kind
        return normalized
    return {}


def fact_kind(record: dict[str, Any]) -> str:
    payload = fact_payload(record)
    kind = str(payload.get("kind") or "").strip()
    if kind:
        return kind
    return str(record.get("kind") or "").strip()


def detector_id(record: dict[str, Any]) -> str:
    direct = str(record.get("detector_id") or "").strip()
    if direct:
        return direct
    detector = record.get("detector")
    if isinstance(detector, dict):
        return str(detector.get("id") or "").strip()
    return ""


def normalize_fact_record(raw: dict[str, Any]) -> dict[str, Any]:
    record = dict(raw)
    payload = fact_payload(record)
    normalized = {
        "id": str(record.get("id") or "").strip(),
        "fact": payload,
        "detector_id": detector_id(record) or "unknown-detector",
        "source_files": [str(item) for item in record.get("source_files", []) if str(item or "").strip()],
        "domain": str(record.get("domain") or "").strip(),
    }
    return normalized


def detector_metadata_from_record(raw: dict[str, Any]) -> dict[str, Any]:
    record = dict(raw)
    payload = fact_payload(record)
    detector = record.get("detector")
    if not isinstance(detector, dict):
        detector = {}
    metadata: dict[str, Any] = {
        "id": detector_id(record) or "unknown-detector",
        "kind": str(payload.get("kind") or record.get("kind") or "").strip() or None,
        "class": str(detector.get("class") or "").strip() or None,
        "strength": detector.get("strength"),
        "rule": detector.get("rule"),
        "bundle": detector.get("bundle"),
        "docs": [],
        "review_questions": [],
    }
    return metadata


def component_ids_from_relationships(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    component_ids: list[str] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        if str(item.get("type") or "") != "entity_ref":
            continue
        if str(item.get("namespace") or "") != "component":
            continue
        target_key = str(item.get("target_key") or "").strip()
        if target_key:
            component_ids.append(target_key)
    return unique_strings(component_ids)


def relationship_targets(
    raw: Any,
    *,
    rel_type: str | None = None,
    label: str | None = None,
    namespace: str | None = None,
) -> list[str]:
    if not isinstance(raw, list):
        return []
    results: list[str] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        current_type = str(item.get("type") or "")
        current_label = str(item.get("label") or "")
        current_namespace = str(item.get("namespace") or "")
        if rel_type and current_type != rel_type:
            continue
        if label and current_label != label:
            continue
        if namespace and current_namespace != namespace:
            continue
        target = ""
        if current_type == "fact_ref":
            target = str(item.get("target_id") or "")
        elif current_type == "doc_ref":
            target = str(item.get("target_path") or "")
        elif current_type == "question_ref":
            target = str(item.get("question_id") or "")
        elif current_type == "entity_ref":
            target = str(item.get("target_key") or "")
        if target:
            results.append(target)
    return unique_strings(results)

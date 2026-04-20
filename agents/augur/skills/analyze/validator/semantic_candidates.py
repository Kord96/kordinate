from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _issue_from_error(message: str) -> dict[str, Any]:
    return {
        "level": "WARNING",
        "section": "semantic-candidates",
        "kind": "semantic-candidate-format",
        "message": message,
        "related_entities": [],
        "evidence_refs": [],
    }


def _normalize_issue(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    message = str(raw.get("message") or "").strip()
    if not message:
        return None
    level = str(raw.get("level") or "WARNING").upper()
    if level not in {"WARNING", "ERROR"}:
        level = "WARNING"
    issue: dict[str, Any] = {
        "level": level,
        "section": str(raw.get("section") or "semantic"),
        "message": message,
        "related_entities": [str(item) for item in (raw.get("related_entities") or []) if str(item).strip()],
        "evidence_refs": [str(item) for item in (raw.get("evidence_refs") or []) if str(item).strip()],
    }
    for key in ("kind", "conflict_type"):
        value = str(raw.get(key) or "").strip()
        if value:
            issue[key] = value
    related_issue_ids = [str(item) for item in (raw.get("related_issue_ids") or []) if str(item).strip()]
    if related_issue_ids:
        issue["related_issue_ids"] = related_issue_ids
    return issue


def load_semantic_candidate_issues(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        path.unlink(missing_ok=True)
        return [_issue_from_error(f"semantic candidate JSON parse failed: {exc}")]

    raw_issues = payload.get("issues") if isinstance(payload, dict) else payload
    if not isinstance(raw_issues, list):
        path.unlink(missing_ok=True)
        return [_issue_from_error("semantic candidate payload must be a JSON array or an object with an issues array")]

    issues: list[dict[str, Any]] = []
    for raw in raw_issues:
        normalized = _normalize_issue(raw)
        if normalized:
            issues.append(normalized)
    path.unlink(missing_ok=True)
    return issues

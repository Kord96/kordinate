"""Low-level validator helpers for paths, grounding, token overlap, and YAML."""

import json
import re
from pathlib import Path
from typing import Iterable

from .constants import KEBAB_RE

try:
    import yaml
except ImportError:
    yaml = None


def kebab_case(s: str) -> bool:
    return bool(KEBAB_RE.match(s))


def normalize_rel_path(path: str) -> str:
    return str(path or "").split(":", 1)[0].strip()


def path_matches_prefix(path: str, prefix: str) -> bool:
    left = normalize_rel_path(path).rstrip("/")
    right = normalize_rel_path(prefix).rstrip("/")
    if not left or not right:
        return False
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def check_grounded_in(
    refs: list,
    project_root: Path | None,
    analysis_dir: Path | None,
    section: str,
    item_id: str,
) -> list[dict]:
    issues = []
    for ref in refs:
        filepath = ref.split(":")[0]
        candidate = Path(filepath)
        if candidate.is_absolute() and candidate.exists():
            continue
        roots = [root for root in (project_root, analysis_dir) if root]
        if not any((root / filepath).exists() for root in roots):
            issues.append(
                {
                    "level": "ERROR",
                    "section": section,
                    "message": f"'{item_id}' grounded_in references non-existent file: {filepath}",
                }
            )
    return issues


def check_existing_paths(
    paths: list,
    project_root: Path | None,
    analysis_dir: Path | None,
    section: str,
    item_id: str,
    *,
    label: str = "path",
) -> list[dict]:
    issues = []
    for raw_path in paths:
        if not raw_path:
            continue
        filepath = str(raw_path)
        candidate = Path(filepath)
        if candidate.is_absolute() and candidate.exists():
            continue
        roots = [root for root in (project_root, analysis_dir) if root]
        if not any((root / filepath).exists() for root in roots):
            issues.append(
                {
                    "level": "ERROR",
                    "section": section,
                    "message": f"'{item_id}' {label} references non-existent path: {filepath}",
                }
            )
    return issues


def resolve_reference_file(
    ref: str,
    project_root: Path | None,
    analysis_dir: Path | None,
) -> Path | None:
    filepath = ref.split(":")[0]
    candidate = Path(filepath)
    if candidate.is_absolute():
        return candidate if candidate.exists() else None
    for root in (project_root, analysis_dir):
        if not root:
            continue
        resolved = root / filepath
        if resolved.exists():
            return resolved
    return None


def parse_reference_line(ref: str) -> int | None:
    parts = ref.rsplit(":", 1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[1])
    except (TypeError, ValueError):
        return None


def tokenize_for_overlap(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[A-Za-z0-9_./-]{3,}", text.lower()) if not token.isdigit()
    }


def tokenize_identifiers(text: str) -> set[str]:
    identifiers: set[str] = set()
    for raw in re.findall(r"[A-Za-z_][A-Za-z0-9_./-]{2,}", text or ""):
        token = raw.strip().lower()
        if token.isdigit():
            continue
        if (
            "_" in raw
            or "/" in raw
            or "." in raw
            or "-" in raw
            or re.search(r"[A-Z]", raw)
            or re.search(r"[0-9]", raw)
        ):
            identifiers.add(token)
    return identifiers


def split_code_like_parts(text: str) -> set[str]:
    parts: set[str] = set()
    for raw in re.findall(r"[A-Za-z_][A-Za-z0-9_./-]{2,}", text or ""):
        normalized = (
            raw.replace("/", " ").replace(".", " ").replace("-", " ").replace("_", " ")
        )
        normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", normalized)
        for part in normalized.split():
            token = part.lower()
            if len(token) >= 3 and not token.isdigit():
                parts.add(token)
    return parts


def tokenize_path_segments(path_text: str) -> set[str]:
    segments: set[str] = set()
    raw_path = path_text.split(":", 1)[0]
    for part in Path(raw_path).parts:
        lowered = part.lower()
        if lowered in {"", ".", ".."}:
            continue
        stem = Path(lowered).stem
        for token in split_code_like_parts(stem):
            segments.add(token)
        if len(lowered) >= 3 and lowered not in {stem, stem + Path(lowered).suffix}:
            segments.add(lowered)
    return segments


def verify_grounding_quality(
    refs: Iterable[str],
    claim_text: str,
    project_root: Path | None,
    analysis_dir: Path | None,
    section: str,
    item_id: str,
    evidence_snippet: str | None = None,
) -> list[dict]:
    issues = []
    claim_tokens = tokenize_for_overlap(claim_text or "")
    claim_identifiers = tokenize_identifiers(claim_text or "")
    claim_parts = split_code_like_parts(claim_text or "")
    evidence_tokens = tokenize_for_overlap(evidence_snippet or "")
    evidence_identifiers = tokenize_identifiers(evidence_snippet or "")
    evidence_parts = split_code_like_parts(evidence_snippet or "")
    if not claim_tokens:
        return issues
    for ref in refs:
        resolved = resolve_reference_file(ref, project_root, analysis_dir)
        if not resolved:
            continue
        line_no = parse_reference_line(ref)
        if line_no is None:
            issues.append(
                {
                    "level": "WARNING",
                    "section": section,
                    "message": f"'{item_id}' grounding reference has no valid line number: {ref}",
                }
            )
            continue
        try:
            lines = resolved.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        if line_no < 1 or line_no > len(lines):
            issues.append(
                {
                    "level": "ERROR",
                    "section": section,
                    "message": f"'{item_id}' grounding line out of range for {resolved}: {line_no}",
                }
            )
            continue
        start = max(0, line_no - 8)
        end = min(len(lines), line_no + 7)
        nearby_text = "\n".join(lines[start:end])
        nearby_tokens = tokenize_for_overlap(nearby_text)
        nearby_identifiers = tokenize_identifiers(nearby_text)
        nearby_parts = split_code_like_parts(nearby_text)
        path_overlap = claim_parts & tokenize_path_segments(ref)
        token_overlap = claim_tokens & (nearby_tokens | evidence_tokens)
        identifier_overlap = claim_identifiers & (nearby_identifiers | evidence_identifiers)
        part_overlap = claim_parts & (nearby_parts | evidence_parts)
        if not token_overlap and not identifier_overlap and not part_overlap and not path_overlap:
            issues.append(
                {
                    "level": "WARNING",
                    "section": section,
                    "message": f"'{item_id}' grounding at {ref} has weak code-shaped overlap with the claim",
                }
            )
    return issues


def validate_evidence_file(
    filepath: str | None,
    lines: list | None,
    claim_text: str,
    project_root: Path | None,
    analysis_dir: Path | None,
    section: str,
    item_id: str,
) -> list[dict]:
    issues = []
    if not filepath:
        return issues
    resolved = resolve_reference_file(filepath, project_root, analysis_dir)
    if not resolved:
        issues.append(
            {
                "level": "ERROR",
                "section": section,
                "message": f"'{item_id}' evidence references non-existent file: {filepath}",
            }
        )
        return issues
    if not lines:
        issues.append(
            {
                "level": "WARNING",
                "section": section,
                "message": f"'{item_id}' evidence is missing line numbers",
            }
        )
        return issues
    try:
        content = resolved.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return issues
    valid_refs: list[str] = []
    for raw_line in lines:
        if not isinstance(raw_line, int):
            issues.append(
                {
                    "level": "ERROR",
                    "section": section,
                    "message": f"'{item_id}' evidence line is not an integer: {raw_line}",
                }
            )
            continue
        if raw_line < 1 or raw_line > len(content):
            issues.append(
                {
                    "level": "ERROR",
                    "section": section,
                    "message": f"'{item_id}' evidence line out of range for {filepath}: {raw_line}",
                }
            )
            continue
        valid_refs.append(f"{filepath}:{raw_line}")
    snippet_text = "\n".join(
        content[line - 1]
        for line in lines
        if isinstance(line, int) and 1 <= line <= len(content)
    )
    issues.extend(
        verify_grounding_quality(
            valid_refs,
            claim_text,
            project_root,
            analysis_dir,
            section,
            item_id,
            evidence_snippet=snippet_text,
        )
    )
    return issues


def load_yaml(path: Path) -> dict | None:
    if yaml:
        try:
            return yaml.safe_load(path.read_text())
        except Exception:
            return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None

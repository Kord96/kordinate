from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import yaml


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


def load_yaml(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists() or not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_markdown_frontmatter(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if (
            isinstance(merged.get(key), dict)
            and isinstance(value, dict)
        ):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def find_reference_file(reference_root: Path, detector_id: str) -> Path | None:
    direct = reference_root / f"{detector_id}.md"
    if direct.exists():
        return direct
    for path in reference_root.rglob(f"{detector_id}.md"):
        if path.is_file():
            return path
    return None


def concept_asset_paths(detectors_root: Path, detector_id: str) -> dict[str, Path]:
    concepts_root = detectors_root / "concepts"

    assets: dict[str, Path] = {}
    policy = concepts_root / "policy.yaml"
    if policy.exists():
        assets["policy.yaml"] = policy

    for asset_type, filename in (
        ("ast-grep", "ast-grep.yaml"),
        ("semgrep", "semgrep.yaml"),
        ("signatures", "signatures.yaml"),
    ):
        typed = concepts_root / asset_type / f"{detector_id}.yaml"
        if typed.exists():
            assets[filename] = typed

    return assets


def unified_concepts_policy(detectors_root: Path) -> dict[str, Any]:
    return load_yaml(detectors_root / "concepts" / "policy.yaml")


def concept_policy(detectors_root: Path, detector_id: str) -> dict[str, Any]:
    unified = unified_concepts_policy(detectors_root)
    return deep_merge_dicts(
        unified.get("defaults", {}) if isinstance(unified.get("defaults"), dict) else {},
        (
            (unified.get("overrides", {}) or {}).get(detector_id, {})
            if isinstance(unified.get("overrides"), dict)
            else {}
        ),
    )


def iter_concept_asset_ids(detectors_root: Path) -> set[str]:
    concepts_root = detectors_root / "concepts"
    names: set[str] = set()
    if not concepts_root.exists():
        return names

    for asset_type in ("ast-grep", "semgrep", "signatures"):
        typed_dir = concepts_root / asset_type
        if typed_dir.exists():
            names.update(path.stem for path in typed_dir.glob("*.yaml"))

    return names


def iter_concept_ast_rule_files(detectors_root: Path) -> list[tuple[str, Path]]:
    concepts_root = detectors_root / "concepts"
    rule_files: dict[str, Path] = {}

    typed_dir = concepts_root / "ast-grep"
    if typed_dir.exists():
        for path in typed_dir.glob("*.yaml"):
            rule_files[path.stem] = path

    return sorted(rule_files.items(), key=lambda item: item[0])

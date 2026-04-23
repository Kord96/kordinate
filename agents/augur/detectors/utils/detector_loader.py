from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MEMORY_CONCEPTS = ROOT / "memory" / "concepts"
DETECTORS = ROOT / "detectors"

from layout import concept_asset_paths, concept_policy, find_reference_file, load_markdown_frontmatter, load_yaml  # noqa: E402


def load_detector_support(concept_source: Path | str) -> dict[str, Any]:
    source_path = Path(concept_source)
    concept_name = source_path.stem if source_path.suffix else source_path.name
    reference_path = find_reference_file(MEMORY_CONCEPTS, concept_name)
    reference = load_markdown_frontmatter(reference_path) if reference_path else {}
    assets = concept_asset_paths(DETECTORS, concept_name)
    policy = concept_policy(DETECTORS, concept_name)
    signatures = reference.get("signatures") if isinstance(reference.get("signatures"), dict) else {}
    asset_signatures = load_yaml(assets.get("signatures.yaml"))
    if isinstance(asset_signatures, dict):
        signatures = {**signatures, **asset_signatures}
    return {
        "policy": policy,
        "signatures": signatures,
    }


def load_execution_plan(bundle_root: Path) -> dict:
    path = bundle_root / "execution-plan.json"
    if not path.exists():
        return {"steps": []}
    return json.loads(path.read_text(encoding="utf-8"))

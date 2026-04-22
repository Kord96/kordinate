from __future__ import annotations

import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONCEPT_REFERENCES_DIR = ROOT / 'references' / 'concepts'
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


def find_concept_reference(concept_name: str) -> Path:
    direct = CONCEPT_REFERENCES_DIR / f'{concept_name}.md'
    if direct.exists():
        return direct
    for path in CONCEPT_REFERENCES_DIR.rglob(f'{concept_name}.md'):
        if path.is_file():
            return path
    return direct


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open('r', encoding='utf-8') as fh:
        return yaml.safe_load(fh) or {}


def load_markdown_frontmatter(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding='utf-8')
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def load_detector_support(concept_dir: Path) -> dict:
    concept_name = concept_dir.name
    reference = load_markdown_frontmatter(find_concept_reference(concept_name))
    policy = load_yaml(concept_dir / 'policy.yaml')
    signatures = {}
    if isinstance(reference.get('signatures'), dict):
        signatures = reference.get('signatures') or {}
    return {
        'policy': policy,
        'signatures': signatures,
    }


def load_execution_plan(bundle_root: Path) -> dict:
    path = bundle_root / 'execution-plan.json'
    if not path.exists():
        return {'steps': []}
    return json.loads(path.read_text(encoding='utf-8'))

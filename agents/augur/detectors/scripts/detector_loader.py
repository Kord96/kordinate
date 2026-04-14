from __future__ import annotations

import json
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open('r', encoding='utf-8') as fh:
        return yaml.safe_load(fh) or {}


def load_detector_support(concept_dir: Path) -> dict:
    return {
        'policy': load_yaml(concept_dir / 'policy.yaml'),
        'signatures': load_yaml(concept_dir / 'signatures.yaml'),
    }


def load_execution_plan(bundle_root: Path) -> dict:
    path = bundle_root / 'execution-plan.json'
    if not path.exists():
        return {'steps': []}
    return json.loads(path.read_text(encoding='utf-8'))

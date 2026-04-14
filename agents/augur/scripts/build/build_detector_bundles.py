#!/usr/bin/env python3
"""Build deterministic detector bundles for Augur.

Generates:
- .generated/bundles/detectors/execution-plan.json
- .generated/bundles/detectors/frameworks/<name>.json
- .generated/bundles/detectors/facts/<name>.json
- .generated/bundles/detectors/concept-evidence/<name>.json
- .generated/bundles/detectors/concept-evidence/questions.json
- .generated/bundles/detectors/concept-evidence/monitoring.json

This is intentionally lightweight for now: it groups source detector assets into
runtime bundle manifests rather than trying to merge YAML AST rules into one file.
That still gives /analyze one stable execution plan and a smaller number of
runtime bundle reads.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DETECTORS = ROOT / 'detectors'
BUNDLES = ROOT / '.generated' / 'bundles' / 'detectors'


def load_concept_meta(path: Path) -> dict:
    raw = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    detector_questions = (
        raw.get('detectors', {})
        .get('questions', {})
    )
    questions = raw.get('questions', {})
    entries = []
    for entry in questions.get('entries', []) or []:
        entries.append({
            'id': entry.get('id'),
            'prompt': entry.get('prompt'),
            'weight': entry.get('weight', 1),
            'signals': entry.get('signals', []) or [],
        })
    monitoring = raw.get('monitoring', {}) or {}
    health_signals = []
    for entry in monitoring.get('health_signals', []) or []:
        health_signals.append({
            'name': entry.get('name'),
            'description': entry.get('description'),
        })
    business_metrics = []
    for entry in monitoring.get('business_metrics', []) or []:
        business_metrics.append({
            'name': entry.get('name'),
            'description': entry.get('description'),
        })
    return {
        'concept': raw.get('concept'),
        'policy': {
            'auto_confirm_allowed': bool(
                raw.get('policy', {})
                .get('auto_confirm', {})
                .get('allowed', False)
            ),
            'unresolved_state': raw.get('policy', {}).get('unresolved_state'),
            'broad_match_requires_questions': bool(
                raw.get('policy', {}).get('broad_match_requires_questions', False)
            ),
        },
        'questions': {
            'enabled': bool(detector_questions.get('enabled', False)),
            'ask_when': detector_questions.get('ask_when', []) or [],
            'threshold': questions.get('threshold'),
            'entries': entries,
        },
        'monitoring': {
            'applies_to': monitoring.get('applies_to', []) or [],
            'health_signals': health_signals,
            'business_metrics': business_metrics,
            'gaps': monitoring.get('gaps', []) or [],
        },
    }


def collect(base: Path, kind: str):
    out = []
    if not base.exists():
        return out
    for entry in sorted(p for p in base.iterdir() if p.is_dir()):
        files = {}
        concept_meta_name = 'meta.yaml' if kind == 'concept-evidence' else 'policy.yaml'
        for name in [concept_meta_name, 'signatures.yaml', 'ast-grep.yaml', 'semgrep.yaml']:
            path = entry / name
            if path.exists():
                files[name] = str(path.relative_to(ROOT))
        record = {'name': entry.name, 'files': files}
        meta_path = entry / 'meta.yaml'
        if kind == 'concept-evidence' and meta_path.exists():
            metadata = load_concept_meta(meta_path)
            if metadata.get('questions', {}).get('entries'):
                record['question_count'] = len(metadata['questions']['entries'])
            record['policy'] = metadata['policy']
            record['questions'] = metadata['questions']
            if (
                metadata.get('monitoring', {}).get('health_signals')
                or metadata.get('monitoring', {}).get('business_metrics')
                or metadata.get('monitoring', {}).get('gaps')
            ):
                record['monitoring'] = metadata['monitoring']
        out.append(record)
    return out


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    frameworks = collect(DETECTORS / 'facts' / 'frameworks', 'frameworks')
    facts = collect(
        DETECTORS / 'facts',
        'facts',
    )
    facts = [fact for fact in facts if fact['name'] not in {'frameworks', 'concept-evidence'}]
    concepts = collect(DETECTORS / 'facts' / 'concept-evidence', 'concept-evidence')
    concept_questions = {
        concept['name']: {
            'policy': concept.get('policy'),
            'questions': concept.get('questions'),
        }
        for concept in concepts
        if concept.get('questions', {}).get('entries')
    }
    concept_monitoring = {
        concept['name']: concept.get('monitoring')
        for concept in concepts
        if concept.get('monitoring')
    }

    write_json(BUNDLES / 'frameworks' / 'all.json', {'frameworks': frameworks})
    write_json(BUNDLES / 'facts' / 'all.json', {'facts': facts})
    write_json(BUNDLES / 'concept-evidence' / 'all.json', {'concepts': concepts})
    write_json(BUNDLES / 'concept-evidence' / 'questions.json', {'concepts': concept_questions})
    write_json(BUNDLES / 'concept-evidence' / 'monitoring.json', {'concepts': concept_monitoring})
    write_json(BUNDLES / 'execution-plan.json', {
        'version': 1,
        'steps': [
            {
                'name': 'framework-detection',
                'bundle': '.generated/bundles/detectors/frameworks/all.json',
                'purpose': 'Detect frameworks first to establish stack context'
            },
            {
                'name': 'fact-extraction',
                'bundle': '.generated/bundles/detectors/facts/all.json',
                'purpose': 'Extract normalized facts before semantic concept inference'
            },
            {
                'name': 'concept-evidence-inference',
                'bundle': '.generated/bundles/detectors/concept-evidence/all.json',
                'purpose': 'Infer concept-evidence facts from normalized deterministic evidence'
            }
        ]
    })
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

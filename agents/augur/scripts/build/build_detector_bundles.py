#!/usr/bin/env python3
"""Build deterministic detector bundles for Augur.

Generates:
- .generated/bundles/detectors/execution-plan.json
- .generated/bundles/detectors/frameworks/<name>.json
- .generated/bundles/detectors/facts/<name>.json
- .generated/bundles/detectors/concepts/<name>.json
- .generated/bundles/detectors/concepts/review_questions.json
- .generated/bundles/detectors/concepts/monitoring.json

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
REFERENCES = ROOT / 'references'
BUNDLES = ROOT / '.generated' / 'bundles' / 'detectors'
import sys
sys.path.insert(0, str(ROOT / 'detectors' / 'utils'))
from layout import concept_asset_paths, find_reference_file, iter_concept_asset_ids, load_markdown_frontmatter, load_yaml  # noqa: E402


def load_concept_metadata(reference_path: Path, policy_path: Path) -> dict:
    reference = load_markdown_frontmatter(reference_path)
    policy_raw = load_yaml(policy_path)
    question_policy = (
        policy_raw.get('detectors', {})
        .get('questions', {})
        if isinstance(policy_raw.get('detectors'), dict)
        else {}
    )
    review_questions = reference.get('review_questions', {})
    entries = []
    for entry in review_questions.get('entries', []) or []:
        entries.append({
            'id': entry.get('id'),
            'prompt': entry.get('prompt'),
            'weight': entry.get('weight', 1),
            'signals': entry.get('signals', []) or [],
        })
    monitoring = reference.get('monitoring', {}) or {}
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
        'concept': reference.get('name') or reference.get('concept'),
        'policy': {
            'auto_confirm_allowed': bool(
                policy_raw.get('policy', {})
                .get('auto_confirm', {})
                .get('allowed', False)
            ),
            'unresolved_state': policy_raw.get('policy', {}).get('unresolved_state'),
            'broad_match_requires_questions': bool(
                policy_raw.get('policy', {}).get('broad_match_requires_questions', False)
            ),
        },
        'review_questions': {
            'enabled': bool(question_policy.get('enabled', False)),
            'ask_when': question_policy.get('ask_when', []) or [],
            'threshold': review_questions.get('threshold'),
            'entries': entries,
        },
        'monitoring': {
            'applies_to': monitoring.get('applies_to', []) or [],
            'health_signals': health_signals,
            'business_metrics': business_metrics,
            'gaps': monitoring.get('gaps', []) or [],
        },
        'signatures': reference.get('signatures') if isinstance(reference.get('signatures'), dict) else {},
    }


def collect_fact_domains(base: Path):
    out = []
    if not base.exists():
        return out
    for entry in sorted(p for p in base.iterdir() if p.is_dir()):
        if entry.name in {'frameworks', 'concepts', 'utils'}:
            continue
        files = {}
        for name in ['policy.yaml', 'signatures.yaml', 'ast-grep.yaml', 'semgrep.yaml']:
            path = entry / name
            if path.exists():
                files[name] = str(path.relative_to(ROOT))
        record = {'name': entry.name, 'files': files}
        out.append(record)
    return out


def collect_frameworks():
    out = []
    frameworks_dir = REFERENCES / 'frameworks'
    policy_dir = DETECTORS / 'frameworks'
    if not frameworks_dir.exists():
        return out
    for entry in sorted(p for p in frameworks_dir.glob('*.md') if p.name != 'README.md'):
        frontmatter = load_markdown_frontmatter(entry)
        signatures = frontmatter.get('signatures') if isinstance(frontmatter.get('signatures'), dict) else {}
        if not signatures:
            continue
        policy_path = policy_dir / entry.stem / 'policy.yaml'
        files = {'reference': str(entry.relative_to(ROOT))}
        if policy_path.exists():
            files['policy.yaml'] = str(policy_path.relative_to(ROOT))
        record = {
            'name': entry.stem,
            'files': files,
            'policy': load_yaml(policy_path).get('policy', {}) if policy_path.exists() else {},
            'signatures': signatures,
            'docs': [str(entry.relative_to(ROOT))],
        }
        out.append(record)
    return out


def collect_concepts():
    out = []
    names = set(iter_concept_asset_ids(DETECTORS))
    for subdir in ('concepts', 'frameworks'):
        reference_root = REFERENCES / subdir
        if not reference_root.exists():
            continue
        for path in reference_root.rglob('*.md'):
            if path.name == 'README.md':
                continue
            names.add(path.stem)
    for name in sorted(names):
        files = {}
        reference_path = find_reference_file(REFERENCES, name)
        if reference_path:
            files['reference'] = str(reference_path.relative_to(ROOT))
        assets = concept_asset_paths(DETECTORS, name)
        for filename, path in assets.items():
            files[filename] = str(path.relative_to(ROOT))
        record = {'name': name, 'files': files}
        if reference_path:
            metadata = load_concept_metadata(reference_path, assets.get('policy.yaml', Path()))
            if metadata.get('review_questions', {}).get('entries'):
                record['review_question_count'] = len(metadata['review_questions']['entries'])
            record['policy'] = metadata['policy']
            record['docs'] = [str(reference_path.relative_to(ROOT))]
            record['review_questions'] = metadata['review_questions']
            if metadata.get('signatures'):
                record['signatures'] = metadata['signatures']
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
    frameworks = collect_frameworks()
    facts = collect_fact_domains(DETECTORS)
    concepts = collect_concepts()
    concept_review_questions = {
        concept['name']: {
            'policy': concept.get('policy'),
            'docs': concept.get('docs', []),
            'review_questions': concept.get('review_questions'),
        }
        for concept in concepts
        if concept.get('review_questions', {}).get('entries')
    }
    concept_monitoring = {
        concept['name']: concept.get('monitoring')
        for concept in concepts
        if concept.get('monitoring')
    }

    write_json(BUNDLES / 'frameworks' / 'all.json', {'frameworks': frameworks})
    write_json(BUNDLES / 'facts' / 'all.json', {'facts': facts})
    write_json(BUNDLES / 'concepts' / 'all.json', {'concepts': concepts})
    write_json(BUNDLES / 'concepts' / 'review_questions.json', {'concepts': concept_review_questions})
    write_json(BUNDLES / 'concepts' / 'monitoring.json', {'concepts': concept_monitoring})
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
                'name': 'concepts-inference',
                'bundle': '.generated/bundles/detectors/concepts/all.json',
                'purpose': 'Infer concepts facts from normalized deterministic evidence'
            }
        ]
    })
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

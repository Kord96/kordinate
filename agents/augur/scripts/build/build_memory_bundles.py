#!/usr/bin/env python3
"""Build deterministic memory bundles for Augur analyze mode."""

from __future__ import annotations

from pathlib import Path
from subprocess import run

ROOT = Path(__file__).resolve().parents[2]
MEMORY = ROOT / 'memory'
BUNDLES = ROOT / '.generated' / 'bundles' / 'memory'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8').rstrip()


def concept_files() -> list[Path]:
    base = MEMORY / 'catalog' / 'concepts'
    return [
        p for p in sorted(base.iterdir())
        if p.is_file() and p.suffix == '.md' and p.name not in {'README.md', 'meta-schema.md'}
    ]


def framework_dirs() -> list[Path]:
    base = MEMORY / 'catalog' / 'frameworks'
    return [p for p in sorted(base.iterdir()) if p.is_dir() and (p / 'framework.md').exists()]


def concept_summary(path: Path) -> str:
    text = read(path).splitlines()
    title = next((line[2:].strip() for line in text if line.startswith('# ')), path.stem)
    sig = None
    for i, line in enumerate(text):
        if line.strip() == '### Signatures':
            for nxt in text[i+1:]:
                if nxt.startswith('### ') or nxt.startswith('## '):
                    break
                if nxt.strip().startswith('- '):
                    sig = nxt.strip()[2:]
                    break
            break
    if sig is None:
        sig = 'See full concept semantics for recognition details.'
    return f'- **{title}** (`{path.stem}`) — {sig}'


def framework_summary(path: Path) -> str:
    text = read(path / 'framework.md').splitlines()
    title = next((line[2:].strip() for line in text if line.startswith('# ')), path.name)
    summary = None
    for line in text[1:8]:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            summary = stripped
            break
    if summary is None:
        summary = 'Framework semantics available.'
    return f'- **{title}** (`{path.name}`) — {summary}'


def common_header(title: str, mode_note: str) -> list[str]:
    return [
        f'# {title}',
        '',
        '## Shared analyze workflow',
        '',
        '1. Resolve mode and scope (full, incremental, or skip).',
        '2. Start from the prepared deterministic artifacts for this run: `$RUN/blast.json` and `$RUN/facts/`.',
        '3. Use deterministic evidence, including `facts/concept-evidence.json`, to decide what deserves attention.',
        '4. Interpret that evidence semantically.',
        '5. Widen into source files only where the prepared artifacts leave ambiguity or show a larger boundary.',
        '6. Build the architectural model, derive grounded tensions and failure modes, and write atlas/stories.',
        '',
        'Deterministic detector evidence establishes what is likely present in the codebase. Semantic memory is used to interpret and evaluate that evidence, not to replace it.',
        '',
        mode_note,
        '',
        '## Workflow',
        '',
        read(MEMORY / 'workflow.md'),
        '',
        '## Contracts',
        '',
        read(MEMORY / 'contracts' / 'app-contract.md'),
        '',
        '## Ontology and indexes',
        '',
        read(MEMORY / 'indexes' / 'abstractions.md'),
        '',
        read(MEMORY / 'indexes' / 'anti-patterns.md'),
        '',
        read(MEMORY / 'indexes' / 'concepts.md'),
        '',
    ]


def build_holistic() -> str:
    sections = common_header(
        'Augur Analyze Bundle — Holistic v1',
        'This bundle includes the full semantic catalog in memory. Still begin with the prepared run artifacts so the analysis is grounded and focused.',
    )
    sections.extend(['## Framework semantics', ''])
    for framework in framework_dirs():
        sections.extend([read(framework / 'framework.md'), ''])
    sections.extend(['## Concept semantics', ''])
    for concept in concept_files():
        sections.extend([read(concept), ''])
    return '\n'.join(sections).rstrip() + '\n'


def build_selective() -> str:
    sections = common_header(
        'Augur Analyze Bundle — Selective v1',
        'This bundle includes the ontology and semantic summaries, not the full semantic catalog. Begin with the prepared run artifacts, then read full semantic definitions only for the most relevant concepts before final interpretation.',
    )
    sections.extend(['## Framework summaries', ''])
    sections.extend(framework_summary(p) for p in framework_dirs())
    sections.extend(['', '## Concept summaries', ''])
    sections.extend(concept_summary(p) for p in concept_files())
    sections.extend(['', '## Selective-read rule', '', 'When detector evidence is ambiguous, high-signal, or central to the architecture, read the full semantic definition from `memory/catalog/frameworks/<name>/framework.md` or `memory/catalog/concepts/<name>.md` before final interpretation.'])
    return '\n'.join(sections).rstrip() + '\n'


def main() -> int:
    BUNDLES.mkdir(parents=True, exist_ok=True)
    (BUNDLES / 'analyze-holistic-v1.md').write_text(build_holistic(), encoding='utf-8')
    (BUNDLES / 'analyze-selective-v1.md').write_text(build_selective(), encoding='utf-8')
    run(['python3', str(Path(__file__).with_name('build_ontology_graph.py'))], check=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

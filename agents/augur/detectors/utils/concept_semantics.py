from __future__ import annotations

from pathlib import Path


def read_concept_markdown(concept_root: Path, concept: str) -> str:
    path = concept_root / concept / 'concept.md'
    if not path.exists():
        return ''
    return path.read_text(encoding='utf-8')


def extract_section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    out: list[str] = []
    capture = False
    for line in lines:
        if line.strip() == heading:
            capture = True
            continue
        if capture and line.startswith('## ') and line.strip() != heading:
            break
        if capture:
            out.append(line)
    return out


def extract_bullets(section_lines: list[str]) -> list[str]:
    bullets = []
    for line in section_lines:
        stripped = line.strip()
        if stripped.startswith('- '):
            bullets.append(stripped[2:])
    return bullets


def concept_review_checklist(concept_root: Path, concept: str) -> list[str]:
    text = read_concept_markdown(concept_root, concept)
    return extract_bullets(extract_section(text, '### Review Checklist'))


def concept_anti_patterns(concept_root: Path, concept: str) -> list[str]:
    text = read_concept_markdown(concept_root, concept)
    return extract_bullets(extract_section(text, '### Anti-patterns'))


def concept_signatures(concept_root: Path, concept: str) -> list[str]:
    text = read_concept_markdown(concept_root, concept)
    return extract_bullets(extract_section(text, '### Signatures'))

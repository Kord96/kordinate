#!/usr/bin/env python3
"""Generate a deterministic static agent bundle from INDEX.yaml.

Usage:
  python generate-agent-bundle.py <agent-dir> <output-file>
"""

from __future__ import annotations

import sys
from pathlib import Path
import yaml


def load_yaml(path: Path):
    with path.open('r', encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def iter_included(entries):
    for entry in entries or []:
        if entry.get('preload') == 'preload' and entry.get('include') is True:
            yield entry
        for child in iter_included(entry.get('children') or []):
            yield child


def iter_repo_files(root: Path, rel: str):
    path = root / rel
    if path.is_file():
        yield rel, path
        return
    if path.is_dir():
        for child in sorted(path.rglob('*')):
            if child.is_file() and child.suffix == '.md':
                yield str(child.relative_to(root)), child


def main() -> int:
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <agent-dir> <output-file>', file=sys.stderr)
        return 1

    agent_dir = Path(sys.argv[1])
    out_file = Path(sys.argv[2])
    index_path = agent_dir / 'INDEX.yaml'
    if not index_path.exists():
        print(f'INDEX.yaml not found: {index_path}', file=sys.stderr)
        return 1

    index = load_yaml(index_path)
    agent = index.get('agent', agent_dir.name)
    description = index.get('description', '')

    sections = [f'# {agent.upper()} static bundle', '']
    if description:
        sections.extend([description, ''])

    seen = set()
    for entry in iter_included(index.get('entries') or []):
        rel = entry['path']
        title = entry.get('purpose') or rel
        for actual_rel, file_path in iter_repo_files(agent_dir, rel):
            if actual_rel in seen:
                continue
            seen.add(actual_rel)
            sections.extend([f'## {actual_rel}', '', f'Purpose: {title}', ''])
            sections.append(file_path.read_text(encoding='utf-8').rstrip())
            sections.append('')

    # Always include INDEX.yaml itself for traceability
    sections.extend(['## INDEX.yaml', '', 'Purpose: Static content manifest for this agent bundle', ''])
    sections.append(index_path.read_text(encoding='utf-8').rstrip())
    sections.append('')

    out_file.write_text('\n'.join(sections).rstrip() + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

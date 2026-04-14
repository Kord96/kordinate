#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from detector_loader import load_execution_plan

ROOT = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = ROOT / '.generated' / 'bundles' / 'detectors'
SCRIPT_DIR = Path(__file__).resolve().parent


def run_step(name: str, project_root: str) -> list[dict]:
    if name == 'concept-detection':
        cmd = [sys.executable, str(SCRIPT_DIR / 'run_ast_grep.py'), project_root]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise SystemExit(result.stderr.strip() or f'{name} failed')
        return json.loads(result.stdout or '[]')
    return []


def main() -> int:
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <project-root>', file=sys.stderr)
        return 2

    project_root = sys.argv[1]
    plan = load_execution_plan(BUNDLE_ROOT)
    outputs: dict[str, list[dict]] = {}
    for step in plan.get('steps', []):
        outputs[step['name']] = run_step(step['name'], project_root)
    print(json.dumps(outputs))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

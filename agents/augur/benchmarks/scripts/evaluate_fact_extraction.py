#!/usr/bin/env python3
"""Run Augur fact extraction across repos and summarize results."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXTRACT = ROOT / "detectors" / "scripts" / "extract_facts.py"


def run_extract(repo: Path) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    subprocess.run([sys.executable, str(EXTRACT), str(repo), "--analysis-mode", "full", "--output", str(tmp_path), "--pretty"], check=True)
    return json.loads(tmp_path.read_text(encoding="utf-8"))


def summarize(repo: Path, payload: dict) -> dict:
    facts = payload.get("facts", [])
    frameworks = [f.get("raw_evidence", {}).get("framework") for f in facts if f.get("kind") == "framework"]
    routes = [f for f in facts if f.get("kind") == "route"]
    models = [f for f in facts if f.get("kind") in {"model", "state-store"}]
    clients = [f for f in facts if f.get("kind") == "external-client"]
    suspicious_frameworks = [fw for fw in frameworks if fw and not any(src.endswith(("package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "Gemfile", "composer.json")) for f in facts if f.get("kind") == "framework" and f.get("raw_evidence", {}).get("framework") == fw for src in f.get("source_files", []))]
    return {
        "repo": str(repo),
        "fact_count": len(facts),
        "domains": dict(Counter(f.get("domain") for f in facts)),
        "frameworks": frameworks,
        "routes": len(routes),
        "models": len(models),
        "external_clients": len(clients),
        "suspicious_frameworks": suspicious_frameworks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Augur fact extraction across repos")
    parser.add_argument("repos", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = [summarize(repo, run_extract(repo)) for repo in args.repos]
    rendered = json.dumps({"results": results}, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

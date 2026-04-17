#!/usr/bin/env python3
"""Build Augur semantic runtime context from prepared run artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Augur semantic runtime context")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--working-dir", required=True, help="Target repo working directory")
    parser.add_argument("--run-dir", required=True, help="Prepared semantic run directory")
    parser.add_argument("--analysis-mode", required=True, choices=["full", "incremental"], help="Prepared analysis mode")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    analysis_dir = run_dir.parent
    project_mem = analysis_dir.parent
    facts_dir = run_dir / "facts"
    startup_path = facts_dir / "startup.json"
    blast_path = run_dir / "blast.json"
    concept_evidence_path = facts_dir / "concept-evidence.json"
    atlas_path = run_dir / "atlas.json"

    starter_files: list[str] = [str(blast_path), str(startup_path)]
    try:
        startup = json.loads(startup_path.read_text(encoding="utf-8"))
        startup_files = startup.get("startup_files") or []
        if isinstance(startup_files, list):
            for relative_path in startup_files:
                if not isinstance(relative_path, str) or not relative_path.strip():
                    continue
                normalized = relative_path.removeprefix("./")
                absolute_path = run_dir / normalized if normalized.startswith("facts/") else facts_dir / normalized
                absolute = str(absolute_path)
                if absolute not in starter_files:
                    starter_files.append(absolute)
    except Exception:
        for fallback in (
            facts_dir / "frameworks.json",
            facts_dir / "boundaries.json",
            facts_dir / "dispatch-bindings.json",
            facts_dir / "hot-files.json",
        ):
            absolute = str(fallback)
            if fallback.exists() and absolute not in starter_files:
                starter_files.append(absolute)

    if args.analysis_mode == "incremental":
        startup_directive = " ".join(
            [
                "Begin with the prepared analysis artifacts, not generic repo orientation.",
                "Read starter_files first and treat facts/startup.json plus facts/index.json as the authority for which deterministic domains are available in this run.",
                "Use those facts to choose where to investigate in the repo, then widen into code as needed.",
                "Preserve unchanged accepted outputs unless blast evidence forces wider revision.",
                "When you need schemas, use the exact canonical files under /app/agents/augur/schemas/.",
            ]
        )
    else:
        startup_directive = " ".join(
            [
                "Begin with the prepared analysis artifacts, not generic repo orientation.",
                "Read starter_files first and treat facts/startup.json plus facts/index.json as the authority for which deterministic domains are available in this run.",
                "Use those facts to choose where to investigate in the repo, then widen into code as needed.",
                "Use the run manifest for available fact files instead of guessing optional paths.",
                "When you need schemas, use the exact canonical files under /app/agents/augur/schemas/.",
            ]
        )

    payload = {
        "project": args.project,
        "mode": args.analysis_mode,
        "working_dir": str(Path(args.working_dir).resolve()),
        "run_dir": str(run_dir),
        "analysis_dir": str(analysis_dir),
        "project_mem": str(project_mem),
        "facts_dir": str(facts_dir),
        "startup_path": str(startup_path),
        "blast_path": str(blast_path),
        "concept_evidence_path": str(concept_evidence_path),
        "atlas_path": str(atlas_path),
        "latest_path": str(analysis_dir / "latest.json"),
        "starter_files": starter_files,
        "startup_directive": startup_directive,
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

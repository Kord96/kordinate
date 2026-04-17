#!/usr/bin/env python3
"""Prepare deterministic Augur analysis artifacts in a run directory.

This is the shared entrypoint for the pre-semantic stage. It materializes:
- facts/*.json via extract_facts.py
- facts/concept-evidence.json via infer_concepts_from_facts.py
- blast.json via compute_blast_radius.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare deterministic Augur artifacts in a run dir")
    parser.add_argument("repo_root", help="Repository root to analyze")
    parser.add_argument("--run-dir", required=True, help="Prepared analysis run directory")
    parser.add_argument("--project", required=True, help="Project slug")
    parser.add_argument("--agent-home", required=True, help="Agent home directory for blast computation")
    parser.add_argument("--current-sha", help="Optional current commit SHA to forward to blast computation")
    parser.add_argument("--previous-sha", help="Optional previous commit SHA to forward to blast computation")
    parser.add_argument(
        "--analysis-mode",
        choices=["full", "incremental", "design"],
        default="full",
        help="Deterministic analysis mode label",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print generated JSON files")
    return parser.parse_args()


def run_cmd(args: list[str]) -> None:
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    if result.returncode == 0:
        return
    if result.stdout:
        sys.stderr.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    raise subprocess.CalledProcessError(result.returncode, args)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def refresh_fact_manifests(facts_dir: Path, concept_evidence_path: Path) -> None:
    if not concept_evidence_path.exists():
        return

    concept_payload = load_json(concept_evidence_path)
    concept_count = int(concept_payload.get("count") or len(concept_payload.get("facts") or []))

    index_path = facts_dir / "index.json"
    if index_path.exists():
        index_payload = load_json(index_path)
        index = index_payload.setdefault("index", {})
        domains = index.setdefault("domains", [])
        domains = [
            domain for domain in domains
            if str(domain.get("name") or "") != "concept-evidence"
        ]
        domains.append({
            "name": "concept-evidence",
            "file": "facts/concept-evidence.json",
            "count": concept_count,
        })
        domains.sort(key=lambda item: str(item.get("name") or ""))
        index["domains"] = domains
        write_json(index_path, index_payload)

    startup_path = facts_dir / "startup.json"
    if startup_path.exists():
        startup_payload = load_json(startup_path)
        large_domains = startup_payload.get("large_domains") or []
        large_domains = [
            domain for domain in large_domains
            if str(domain.get("name") or "") != "concept-evidence"
        ]
        large_domains.append({
            "name": "concept-evidence",
            "file": "facts/concept-evidence.json",
            "count": concept_count,
        })
        large_domains.sort(key=lambda item: str(item.get("name") or ""))
        startup_payload["large_domains"] = large_domains

        domain_counts = startup_payload.get("domain_counts") or []
        domain_counts = [
            domain for domain in domain_counts
            if str(domain.get("name") or "") != "concept-evidence"
        ]
        domain_counts.append({
            "name": "concept-evidence",
            "file": "facts/concept-evidence.json",
            "count": concept_count,
        })
        domain_counts.sort(key=lambda item: str(item.get("name") or ""))
        startup_payload["domain_counts"] = domain_counts
        write_json(startup_path, startup_payload)


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    run_dir = Path(args.run_dir).resolve()
    facts_dir = run_dir / "facts"
    concept_evidence_path = facts_dir / "concept-evidence.json"
    blast_path = run_dir / "blast.json"

    run_dir.mkdir(parents=True, exist_ok=True)
    facts_dir.mkdir(parents=True, exist_ok=True)

    extract_cmd = [
        "python3",
        str(ROOT / "scripts" / "extract_facts.py"),
        str(repo_root),
        "--output-dir",
        str(facts_dir),
        "--analysis-mode",
        args.analysis_mode,
    ]
    if args.pretty:
        extract_cmd.append("--pretty")
    run_cmd(extract_cmd)

    run_cmd([
        "python3",
        str(ROOT / "scripts" / "infer_concepts_from_facts.py"),
        str(facts_dir),
        "--output",
        str(concept_evidence_path),
    ])
    refresh_fact_manifests(facts_dir, concept_evidence_path)

    blast_cmd = [
        "python3",
        str(ROOT / "scripts" / "compute_blast_radius.py"),
        str(repo_root),
        "--project",
        args.project,
        "--agent-home",
        str(Path(args.agent_home).resolve()),
        "--output",
        str(blast_path),
    ]
    if args.current_sha:
        blast_cmd.extend(["--current-sha", args.current_sha])
    if args.previous_sha:
        blast_cmd.extend(["--previous-sha", args.previous_sha])
    run_cmd(blast_cmd)

    payload = {
        "repo_root": str(repo_root),
        "run_dir": str(run_dir),
        "facts_dir": str(facts_dir),
        "concept_evidence": str(concept_evidence_path),
        "blast": str(blast_path),
        "analysis_mode": args.analysis_mode,
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

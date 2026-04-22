#!/usr/bin/env python3
"""Deterministic Augur fact extraction CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "detectors"))

from fact_extractor_support import build_facts_payload
from utils import detector_metadata_from_record, normalize_fact_record


def concept_detector_metadata() -> dict[str, dict[str, object]]:
    bundle = ROOT / ".generated" / "bundles" / "detectors" / "concepts" / "review_questions.json"
    if not bundle.exists():
        return {}
    try:
        payload = json.loads(bundle.read_text(encoding="utf-8"))
    except Exception:
        return {}
    concepts = payload.get("concepts")
    if not isinstance(concepts, dict):
        return {}
    metadata: dict[str, dict[str, object]] = {}
    for concept_name, details in concepts.items():
        if not isinstance(details, dict):
            continue
        detector_id = f"concepts-{concept_name}"
        question_block = details.get("review_questions")
        entries = question_block.get("entries") if isinstance(question_block, dict) else []
        metadata[detector_id] = {
            "docs": list(details.get("docs") or []),
            "review_questions": [
                str(entry.get("prompt") or "").strip()
                for entry in entries or []
                if isinstance(entry, dict) and str(entry.get("prompt") or "").strip()
            ],
        }
    return metadata


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract normalized Augur facts from a project.")
    parser.add_argument("root", nargs="?", default=".", help="Project root to scan.")
    parser.add_argument("--repo-dir", help="Alias for the project root to scan.")
    parser.add_argument("--output", "-o", help="Write JSON to this file instead of stdout.")
    parser.add_argument("--output-dir", help="Write a facts directory rooted at this path.")
    parser.add_argument("--output-root", help="Write run manifests such as startup.json and index.json at this run root.")
    parser.add_argument(
        "--analysis-mode",
        choices=["full", "incremental", "design"],
        default="full",
        help="Label the extraction run for downstream consumers.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root_arg = args.repo_dir or args.root
    root = Path(root_arg).resolve()
    if not root.exists():
        print(f"error: root not found: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 2

    payload = build_facts_payload(root, analysis_mode=args.analysis_mode)
    serialized = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=bool(args.pretty))
    if args.pretty:
        serialized += "\n"

    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_root = Path(args.output_root).resolve() if args.output_root else output_dir
        concept_metadata = concept_detector_metadata()

        facts = payload.get("facts", [])
        domains: dict[str, list[dict[str, object]]] = {}
        for fact in facts:
            domain = str(fact.get("domain") or "").strip()
            if not domain:
                continue
            domains.setdefault(domain, []).append(fact)

        for domain, items in sorted(domains.items()):
            domain_path = output_dir / f"{domain}.json"
            detectors: dict[str, dict[str, object]] = {}
            normalized_items: list[dict[str, object]] = []
            for item in items:
                normalized = normalize_fact_record(item)
                normalized.pop("domain", None)
                normalized_items.append(normalized)
                metadata = detector_metadata_from_record(item)
                detector_id = str(metadata.get("id") or "").strip()
                if not detector_id:
                    continue
                merged = dict(metadata)
                if detector_id in concept_metadata:
                    merged["docs"] = list(concept_metadata[detector_id].get("docs") or [])
                    merged["review_questions"] = list(concept_metadata[detector_id].get("review_questions") or [])
                detectors[detector_id] = merged
            domain_payload = {
                "version": payload.get("version", "1"),
                "generated": payload.get("generated"),
                "project": payload.get("project"),
                "analysis_mode": payload.get("analysis_mode"),
                "domain": domain,
                "detectors": detectors,
                "count": len(normalized_items),
                "facts": normalized_items,
            }
            domain_path.write_text(
                json.dumps(domain_payload, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)) + ("\n" if args.pretty else ""),
                encoding="utf-8",
            )

        index_payload = {
            key: value
            for key, value in payload.items()
            if key != "facts"
        }
        (output_root / "index.json").write_text(
            json.dumps(index_payload, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)) + ("\n" if args.pretty else ""),
            encoding="utf-8",
        )

        startup_domains = [
            domain
            for domain in ("frameworks", "dispatch-bindings", "hot-files")
            if domain in domains
        ]
        startup_payload = {
            "version": payload.get("version", "1"),
            "generated": payload.get("generated"),
            "project": payload.get("project"),
            "analysis_mode": payload.get("analysis_mode"),
            "root": payload.get("root"),
            "startup_files": [f"facts/{domain}.json" for domain in startup_domains],
            "targeted_domains": {
                "concept_questions": [
                    "facts/concepts.json",
                    "facts/frameworks.json",
                ],
                "decomposition_and_narratives": [
                    "derived/component-seeds.json",
                    "derived/story-seeds.json",
                    "derived/narrative-seeds.json",
                ],
                "state_and_data_flow": [
                    "facts/symbols-seed.json",
                    "facts/state-seeds.json",
                    "facts/state-access-summary.json",
                    "facts/execution-slices.json",
                    "facts/data-touches.json",
                ],
                "boundaries_and_dependencies": [
                    "facts/boundaries.json",
                    "facts/handlers.json",
                    "facts/external-clients.json",
                    "facts/auth-surface.json",
                    "facts/config.json",
                ],
                "health_and_failure": [
                    "facts/health-candidates.json",
                    "facts/failure-scenario-candidates.json",
                    "facts/control-hotspots.json",
                ],
            },
            "detector_status": [
                {
                    "id": run.get("id"),
                    "domain": run.get("domain"),
                    "class": run.get("class"),
                    "status": run.get("status"),
                }
                for run in (index_payload.get("index", {}) or {}).get("detectors_run", [])
            ],
        }
        (output_root / "startup.json").write_text(
            json.dumps(startup_payload, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)) + ("\n" if args.pretty else ""),
            encoding="utf-8",
        )
    elif args.output:
        out = Path(args.output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized)
        if not serialized.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deterministic Augur fact extraction CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fact_extractor_support import build_facts_payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract normalized Augur facts from a project.")
    parser.add_argument("root", nargs="?", default=".", help="Project root to scan.")
    parser.add_argument("--repo-dir", help="Alias for the project root to scan.")
    parser.add_argument("--output", "-o", help="Write JSON to this file instead of stdout.")
    parser.add_argument("--output-dir", help="Write a facts directory rooted at this path.")
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

        facts = payload.get("facts", [])
        domains: dict[str, list[dict[str, object]]] = {}
        for fact in facts:
            domain = str(fact.get("domain") or "").strip()
            if not domain:
                continue
            domains.setdefault(domain, []).append(fact)

        for domain, items in sorted(domains.items()):
            domain_path = output_dir / f"{domain}.json"
            domain_payload = {
                "version": payload.get("version", "1"),
                "generated": payload.get("generated"),
                "project": payload.get("project"),
                "analysis_mode": payload.get("analysis_mode"),
                "domain": domain,
                "count": len(items),
                "facts": items,
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
        (output_dir / "index.json").write_text(
            json.dumps(index_payload, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)) + ("\n" if args.pretty else ""),
            encoding="utf-8",
        )

        startup_domains = [
            domain
            for domain in ("frameworks", "boundaries", "routes", "dispatch-bindings", "hot-files", "control-hotspots", "state-access-summary")
            if domain in domains
        ]
        startup_payload = {
            "version": payload.get("version", "1"),
            "generated": payload.get("generated"),
            "project": payload.get("project"),
            "analysis_mode": payload.get("analysis_mode"),
            "root": payload.get("root"),
            "startup_files": [f"facts/{domain}.json" for domain in startup_domains],
            "large_domains": [
                {
                    "name": domain.get("name"),
                    "file": domain.get("file"),
                    "count": domain.get("count"),
                }
                for domain in (index_payload.get("index", {}) or {}).get("domains", [])
                if str(domain.get("name") or "") in {"concept-evidence", "external-clients", "config", "import-graph", "call-edges", "data-touches", "execution-slices"}
            ],
            "domain_counts": [
                {
                    "name": domain.get("name"),
                    "file": domain.get("file"),
                    "count": domain.get("count"),
                }
                for domain in (index_payload.get("index", {}) or {}).get("domains", [])
            ],
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
        (output_dir / "startup.json").write_text(
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

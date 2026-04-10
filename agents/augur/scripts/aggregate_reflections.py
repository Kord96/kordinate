#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECTS_ROOT = Path("/kord/augur/memory/projects")
INDEX_ROOT = Path("/kord/augur/memory/global/reflections/records")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    lowered = re.sub(r"\s+", " ", lowered)
    lowered = re.sub(r"[`\"'()\\[\\]{}]+", "", lowered)
    return lowered


def sentence_units(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    parts = re.split(r"(?<=[.!?])\s+|\n+", stripped)
    return [part.strip(" -") for part in parts if part.strip(" -")]


def fingerprint(text: str) -> str:
    return hashlib.sha1(normalize_text(text).encode("utf-8")).hexdigest()[:12]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_reflection_files(root: Path, use_index: bool) -> list[Path]:
    if root.is_file():
        return [root]
    if use_index:
        return sorted(root.rglob("*.json"))
    return sorted(root.rglob("reflections/runs/*.json"))


def repo_slug(repo: str) -> str:
    return repo.replace("/", "--")


def build_summary(records: list[dict[str, Any]], group_label: str) -> dict[str, Any]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    signal_to_models: dict[str, set[str]] = defaultdict(set)
    signal_examples: dict[str, str] = {}
    per_model_signals: dict[str, set[str]] = defaultdict(set)
    per_model_counts: Counter[str] = Counter()
    source_reflection_ids: list[str] = []

    for record in records:
        model = record.get("model") or record.get("backend_model") or "unknown"
        provider = record.get("provider") or record.get("backend_provider") or "unknown"
        runtime = record.get("runtime_kind") or record.get("backend_runtime") or "unknown"
        by_model[model].append(record)
        per_model_counts[model] += 1
        source_reflection_ids.append(record["reflection_id"])

        for field in ("project", "general"):
            for unit in sentence_units(record.get("reflection", {}).get(field, "")):
                unit_id = fingerprint(unit)
                signal_to_models[unit_id].add(model)
                signal_examples.setdefault(unit_id, unit)
                per_model_signals[model].add(unit_id)

        record.setdefault("provider", provider)
        record.setdefault("runtime_kind", runtime)

    consensus_signals = []
    for unit_id, models in signal_to_models.items():
        if len(models) > 1:
            consensus_signals.append({
                "signal_id": unit_id,
                "text": signal_examples[unit_id],
                "models": sorted(models),
                "model_count": len(models),
            })
    consensus_signals.sort(key=lambda item: (-item["model_count"], item["text"]))

    unique_yield = []
    for model, signals in sorted(per_model_signals.items()):
        uniques = sorted(signal for signal in signals if signal_to_models[signal] == {model})
        unique_yield.append({
            "model": model,
            "unique_signal_count": len(uniques),
            "unique_signals": [
                {"signal_id": unit_id, "text": signal_examples[unit_id]}
                for unit_id in uniques[:20]
            ],
        })

    complementarity = []
    models = sorted(per_model_signals)
    for left in models:
        for right in models:
            if left >= right:
                continue
            left_signals = per_model_signals[left]
            right_signals = per_model_signals[right]
            overlap = len(left_signals & right_signals)
            union = len(left_signals | right_signals)
            complementarity.append({
                "left_model": left,
                "right_model": right,
                "shared_signal_count": overlap,
                "union_signal_count": union,
                "jaccard_similarity": round((overlap / union), 4) if union else 0.0,
                "left_only_count": len(left_signals - right_signals),
                "right_only_count": len(right_signals - left_signals),
            })
    complementarity.sort(key=lambda item: (item["jaccard_similarity"], item["left_model"], item["right_model"]))

    model_profiles = []
    for model in sorted(by_model):
        sample_record = by_model[model][0]
        model_profiles.append({
            "model": model,
            "provider": sample_record.get("provider", "unknown"),
            "runtime_kind": sample_record.get("runtime_kind", "unknown"),
            "reflection_count": per_model_counts[model],
            "signal_count": len(per_model_signals[model]),
        })

    return {
        "summary_id": f"{utc_now().replace(':', '-')}__{group_label}",
        "generated_at": utc_now(),
        "group_label": group_label,
        "source_reflection_ids": sorted(source_reflection_ids),
        "record_count": len(records),
        "model_profiles": model_profiles,
        "consensus_signals": consensus_signals[:50],
        "unique_yield": unique_yield,
        "complementarity": complementarity,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate Augur reflections into a cross-model summary.")
    parser.add_argument("--root", type=Path, default=INDEX_ROOT, help="Reflection index root, raw projects root, or single reflection file.")
    parser.add_argument("--repo", help="Optional repo filter.")
    parser.add_argument("--output", type=Path, help="Explicit output path for the summary JSON.")
    parser.add_argument("--source", choices=["index", "raw"], default="index", help="Whether to read normalized global records or raw project records.")
    args = parser.parse_args()

    files = find_reflection_files(args.root, use_index=args.source == "index")
    records = [load_json(path) for path in files]
    if args.repo:
        records = [record for record in records if record.get("repo") == args.repo]
    if not records:
        raise SystemExit("No reflection records found for the requested scope.")

    group_label = normalize_text(args.repo or "all-projects").replace(" ", "-")
    summary = build_summary(records, group_label)

    if args.output:
        output_path = args.output
    elif args.repo:
        output_path = PROJECTS_ROOT / repo_slug(args.repo) / "reflections" / "summaries" / f"{summary['summary_id']}.json"
    else:
        output_path = Path("/kord/augur/memory/global/reflections/summaries") / f"{summary['summary_id']}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_path": str(output_path), "record_count": summary["record_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

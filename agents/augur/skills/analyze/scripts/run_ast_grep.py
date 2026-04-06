#!/usr/bin/env python3
"""Run ast-grep concept detection and emit structured evidence records.

Usage:
    python run_ast_grep.py <project-root> [--kordinate-home <path>]

Finds concept detector ast-grep rule files in the detector source tree and runs them
against the target project. Outputs JSON array of structured evidence records.
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from concept_decision import evidence_verdict  # noqa: E402
from detector_loader import load_detector_support  # noqa: E402


def infer_specificity(match_count: int) -> str:
    if match_count <= 1:
        return "narrow"
    if match_count <= 3:
        return "narrow"
    if match_count <= 10:
        return "broad"
    return "broad"


def infer_noise(match_count: int) -> str:
    if match_count <= 2:
        return "low"
    if match_count <= 8:
        return "medium"
    return "high"


def infer_match_confidence(detector_strength: int, match_count: int, noise: str) -> int:
    if match_count == 0:
        return 1
    confidence = detector_strength
    if noise == "medium":
        confidence = max(2, confidence - 1)
    elif noise == "high":
        confidence = max(1, confidence - 2)
    return max(1, min(5, confidence))


def build_evidence_record(concept: str, detector_strength: int, matches: list[dict], rule_file: str) -> dict:
    match_count = len(matches)
    specificity = infer_specificity(match_count)
    noise = infer_noise(match_count)
    match_confidence = infer_match_confidence(detector_strength, match_count, noise)
    matched = match_count > 0
    verdict = evidence_verdict(detector_strength, match_confidence, specificity, matched)

    locations = []
    for match in matches[:10]:
        path = match.get("file") or match.get("path") or match.get("filename")
        line = None
        if isinstance(match.get("range"), dict):
            start = match["range"].get("start") or {}
            line = start.get("line")
            if isinstance(line, int):
                line += 1
        elif isinstance(match.get("start"), dict):
            line = match["start"].get("line")
        excerpt = match.get("lines") or match.get("text") or match.get("message")
        locations.append({
            "path": path,
            "line": line,
            "excerpt": excerpt.strip() if isinstance(excerpt, str) else excerpt,
        })

    notes = []
    if matched:
        notes.append(f"{match_count} ast-grep match(es) for {concept}")
    else:
        notes.append(f"No ast-grep matches for {concept}")

    return {
        "schema": "augur-evidence-record/v1",
        "concept": concept,
        "detector": {
            "type": "ast_grep",
            "rule_id": Path(rule_file).stem,
            "rule_file": Path(rule_file).name,
            "language": None,
            "framework": None,
        },
        "polarity": "positive" if matched else "neutral",
        "scores": {
            "detector_strength": detector_strength,
            "match_confidence": match_confidence,
        },
        "verdict": verdict,
        "summary": {
            "matched": matched,
            "match_count": match_count,
            "specificity": specificity,
            "scope": "repo",
            "noise": noise,
            "contradiction_flags": [],
            "notes": notes,
        },
        "locations": locations,
        "signals": [],
        "follow_up": {
            "recommended_next_step": "ask_questions" if verdict == "candidate" else ("none" if verdict == "confirmed" else "verify_signatures"),
            "question_ids": [],
        },
    }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <project-root> [--kordinate-home <path>]", file=sys.stderr)
        sys.exit(2)

    project_root = sys.argv[1]
    kordinate_home = os.environ.get("KORDINATE_HOME", os.path.expanduser("~/.kord"))

    if "--kordinate-home" in sys.argv:
        idx = sys.argv.index("--kordinate-home")
        if idx + 1 < len(sys.argv):
            kordinate_home = sys.argv[idx + 1]

    concepts_dir = Path(kordinate_home) / "agents" / "augur" / "detectors" / "concepts"

    if not concepts_dir.exists():
        print(f"Detector directory not found: {concepts_dir}", file=sys.stderr)
        sys.exit(1)

    rule_files = sorted(glob.glob(str(concepts_dir / "*/ast-grep.yaml")))

    if not rule_files:
        print("[]")
        return

    evidence_records = []
    errors = []

    for rule_file in rule_files:
        concept = Path(rule_file).parent.name
        support = load_detector_support(Path(rule_file).parent)
        detector_strength = int(
            support.get("policy", {})
            .get("detectors", {})
            .get("ast_grep", {})
            .get("detector_strength", 2)
        )
        matches = []
        try:
            result = subprocess.run(
                ["ast-grep", "scan", "-r", rule_file, project_root, "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                loaded = json.loads(result.stdout)
                if isinstance(loaded, list):
                    matches = loaded
        except subprocess.TimeoutExpired:
            errors.append(f"Timeout scanning with {concept}")
        except (json.JSONDecodeError, Exception) as e:
            errors.append(f"Error with {concept}: {e}")

        evidence_records.append(build_evidence_record(concept, detector_strength, matches, rule_file))

    if errors:
        print(f"Warnings: {len(errors)} rules had issues", file=sys.stderr)
        for err in errors[:10]:
            print(f"  - {err}", file=sys.stderr)

    print(json.dumps(evidence_records))


if __name__ == "__main__":
    main()

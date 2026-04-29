#!/usr/bin/env python3
"""Validate Augur concept/unit catalogs that use Markdown frontmatter."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ALLOWED_CONCEPT_TYPES = {
    "pattern",
    "anti-pattern",
    "domain-model",
    "flow-shape",
    "structure-shape",
    "framework",
}

GENERIC_WORDS = {
    "architecture",
    "code",
    "component",
    "design",
    "good",
    "implementation",
    "logic",
    "pattern",
    "process",
    "quality",
    "service",
    "system",
    "thing",
}

REQUIRED_MARKDOWN_KEYS = {"description"}
KNOWN_MARKDOWN_KEYS = {
    "abstraction",
    "aliases",
    "analysis",
    "categories",
    "concept",
    "description",
    "detectors",
    "diagnostic_questions",
    "distributed",
    "fact_generator",
    "graphable",
    "kind",
    "monitoring",
    "name",
    "observable",
    "policy",
    "schema",
    "semantic_validation",
    "signatures",
    "support_rules",
    "taxonomy",
    "testable",
    "testing",
    "traits",
    "type",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    path: str
    message: str


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def add(findings: list[Finding], severity: str, path: Path, root: Path, message: str) -> None:
    findings.append(Finding(severity, rel(path, root), message))


def read_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", text, re.DOTALL)
    if not match:
        return None, text
    data = yaml.safe_load(match.group(1))
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return data, text[match.end() :]


def concept_name_from_frontmatter(data: dict[str, Any]) -> str | None:
    for key in ("concept", "name"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def concept_type_from_frontmatter(data: dict[str, Any]) -> str | None:
    for key in ("type", "kind"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    taxonomy = data.get("taxonomy")
    if isinstance(taxonomy, dict):
        value = taxonomy.get("type")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def is_kebab(value: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value))


def as_bool(value: Any) -> bool:
    return isinstance(value, bool)


def categories(data: dict[str, Any]) -> list[str]:
    raw = data.get("categories")
    if raw is None:
        taxonomy = data.get("taxonomy")
        if isinstance(taxonomy, dict):
            raw = taxonomy.get("categories")
    if raw is None:
        raw = data.get("abstraction")
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, str) and item.strip()]
    return []


def detector_entries(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    detectors = data.get("detectors")
    if not isinstance(detectors, dict):
        return []
    return [(name, cfg) for name, cfg in detectors.items() if isinstance(cfg, dict)]


def detector_file_refs(data: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for _name, cfg in detector_entries(data):
        file_ref = cfg.get("file")
        if isinstance(file_ref, str) and file_ref.strip():
            refs.append(file_ref.strip())
    support_rules = data.get("support_rules")
    if isinstance(support_rules, dict):
        for value in support_rules.values():
            if isinstance(value, str) and value.strip():
                refs.append(value.strip())
    fact_generator = data.get("fact_generator")
    if isinstance(fact_generator, str) and fact_generator.strip():
        refs.append(fact_generator.strip())
    if isinstance(fact_generator, dict):
        file_ref = fact_generator.get("file") or fact_generator.get("script")
        if isinstance(file_ref, str) and file_ref.strip():
            refs.append(file_ref.strip())
    return refs


def validate_markdown(path: Path, root: Path, findings: list[Finding]) -> dict[str, Any] | None:
    try:
        frontmatter, body = read_frontmatter(path)
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
        add(findings, "ERROR", path, root, f"invalid frontmatter: {exc}")
        return None

    if frontmatter is None:
        add(findings, "ERROR", path, root, "missing YAML frontmatter")
        return None

    missing = sorted(REQUIRED_MARKDOWN_KEYS - set(frontmatter))
    if missing:
        add(findings, "ERROR", path, root, f"missing required frontmatter key(s): {', '.join(missing)}")

    unknown = sorted(set(frontmatter) - KNOWN_MARKDOWN_KEYS)
    if unknown:
        add(findings, "WARNING", path, root, f"unknown frontmatter key(s): {', '.join(unknown)}")

    name = concept_name_from_frontmatter(frontmatter)
    if not name:
        add(findings, "ERROR", path, root, "frontmatter must include concept or name")
    elif not is_kebab(name):
        add(findings, "ERROR", path, root, f"concept/name must be kebab-case: {name}")

    concept_type = concept_type_from_frontmatter(frontmatter)
    if not concept_type:
        add(findings, "ERROR", path, root, "frontmatter must include type, kind, or taxonomy.type")
    elif concept_type not in ALLOWED_CONCEPT_TYPES:
        add(findings, "ERROR", path, root, f"unsupported concept type: {concept_type}")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        add(findings, "ERROR", path, root, "description must be a non-empty string")
    elif len(description.strip()) < 20:
        add(findings, "WARNING", path, root, "description is very short")

    if name and path.name == "concept.md" and path.parent.name != name:
        add(findings, "ERROR", path, root, f"concept/name {name} does not match directory {path.parent.name}")

    for key in ("testable", "observable", "distributed", "graphable"):
        if key in frontmatter and not as_bool(frontmatter[key]):
            add(findings, "ERROR", path, root, f"{key} must be boolean when present")

    traits = frontmatter.get("traits")
    if isinstance(traits, dict):
        for key, value in traits.items():
            if key in {"testable", "observable", "distributed", "graphable"} and not as_bool(value):
                add(findings, "ERROR", path, root, f"traits.{key} must be boolean")

    detectors = frontmatter.get("detectors")
    if detectors is not None and not isinstance(detectors, dict):
        add(findings, "ERROR", path, root, "detectors must be a mapping")
    for name, cfg in detector_entries(frontmatter):
        if "enabled" in cfg and not isinstance(cfg["enabled"], bool):
            add(findings, "ERROR", path, root, f"detectors.{name}.enabled must be boolean")
        strength = cfg.get("detector_strength")
        if strength is not None and not (isinstance(strength, int) and 1 <= strength <= 5):
            add(findings, "ERROR", path, root, f"detectors.{name}.detector_strength must be an integer from 1 to 5")

    policy = frontmatter.get("policy")
    if policy is not None and not isinstance(policy, dict):
        add(findings, "ERROR", path, root, "policy must be a mapping")
    elif isinstance(policy, dict):
        auto_confirm = policy.get("auto_confirm")
        if auto_confirm is not None and not isinstance(auto_confirm, dict):
            add(findings, "ERROR", path, root, "policy.auto_confirm must be a mapping")
        if "unresolved_state" in policy and policy["unresolved_state"] not in {"candidate", "absent", "unknown"}:
            add(findings, "ERROR", path, root, "policy.unresolved_state must be candidate, absent, or unknown")

    questions = frontmatter.get("diagnostic_questions")
    if questions is not None:
        validate_questions(path, root, questions, findings)

    if not body.strip():
        add(findings, "ERROR", path, root, "Markdown body is empty")

    for file_ref in detector_file_refs(frontmatter):
        ref_path = (path.parent / file_ref).resolve()
        if not ref_path.exists():
            add(findings, "ERROR", path, root, f"referenced support file does not exist: {file_ref}")

    return frontmatter


def validate_questions(path: Path, root: Path, questions: Any, findings: list[Finding]) -> None:
    question_list: Any
    if isinstance(questions, dict):
        threshold = questions.get("threshold")
        if threshold is not None and not isinstance(threshold, int):
            add(findings, "ERROR", path, root, "diagnostic_questions.threshold must be an integer")
        question_list = questions.get("questions")
    else:
        question_list = questions

    if not isinstance(question_list, list) or not question_list:
        add(findings, "ERROR", path, root, "diagnostic_questions must contain a non-empty questions list")
        return

    seen: set[str] = set()
    for index, question in enumerate(question_list):
        if not isinstance(question, dict):
            add(findings, "ERROR", path, root, f"diagnostic_questions[{index}] must be a mapping")
            continue
        qid = question.get("id")
        if not isinstance(qid, str) or not is_kebab(qid):
            add(findings, "ERROR", path, root, f"diagnostic_questions[{index}].id must be kebab-case")
        elif qid in seen:
            add(findings, "ERROR", path, root, f"duplicate diagnostic question id: {qid}")
        else:
            seen.add(qid)
        prompt = question.get("prompt")
        if not isinstance(prompt, str) or len(prompt.strip()) < 20:
            add(findings, "ERROR", path, root, f"diagnostic_questions[{index}].prompt must be descriptive")
        weight = question.get("weight")
        if weight is not None and not (isinstance(weight, int) and 1 <= weight <= 5):
            add(findings, "ERROR", path, root, f"diagnostic_questions[{index}].weight must be an integer from 1 to 5")
        signals = question.get("signals")
        if signals is not None and not (
            isinstance(signals, list) and all(isinstance(signal, str) and signal.strip() for signal in signals)
        ):
            add(findings, "ERROR", path, root, f"diagnostic_questions[{index}].signals must be a list of strings")


def validate_yaml_support(path: Path, root: Path, findings: list[Finding]) -> None:
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        add(findings, "ERROR", path, root, f"invalid YAML: {exc}")


def validate_fact_generator(command: str | None, target: Path, findings: list[Finding]) -> None:
    if not command:
        return
    argv = [*shlex.split(command), str(target)]
    result = subprocess.run(argv, cwd=target, text=True, capture_output=True)
    if result.returncode != 0:
        output = (result.stderr or result.stdout or "").strip().splitlines()
        detail = output[0] if output else f"exit code {result.returncode}"
        findings.append(Finding("ERROR", rel(target, target), f"fact-generator failed: {detail}"))


def semantic_score(path: Path, root: Path, data: dict[str, Any], body: str) -> list[Finding]:
    findings: list[Finding] = []
    scores: dict[str, int] = {}
    description = str(data.get("description") or "")
    words = {word.lower() for word in re.findall(r"[A-Za-z][A-Za-z-]+", description)}

    detectors = detector_entries(data)
    signatures = data.get("signatures")
    questions = data.get("diagnostic_questions")
    cats = categories(data)
    refs = detector_file_refs(data)

    scores["specificity"] = 3
    if len(words) < 4 or len(words - GENERIC_WORDS) < 3:
        scores["specificity"] -= 2
    if not cats:
        scores["specificity"] -= 1

    scores["detectability"] = 0
    if detectors:
        scores["detectability"] += 2
    if refs:
        scores["detectability"] += 1
    if signatures or re.search(r"(?im)^#+\s*signatures\b", body):
        scores["detectability"] += 1
    if questions:
        scores["detectability"] += 1
    scores["detectability"] = min(scores["detectability"], 5)

    scores["evidence_value"] = 1
    if refs:
        scores["evidence_value"] += 1
    if questions:
        scores["evidence_value"] += 1
    if re.search(r"(?im)^#+\s*(confidence|recognition|review checklist)\b", body):
        scores["evidence_value"] += 1
    if data.get("fact_generator"):
        scores["evidence_value"] += 1
    scores["evidence_value"] = min(scores["evidence_value"], 5)

    scores["noise_control"] = 2
    policy = data.get("policy")
    if isinstance(policy, dict):
        if policy.get("broad_match_requires_questions") is True:
            scores["noise_control"] += 1
        if isinstance(policy.get("auto_confirm"), dict):
            scores["noise_control"] += 1
        if policy.get("requires_no_contradiction") is True:
            scores["noise_control"] += 1
    if questions:
        scores["noise_control"] += 1
    scores["noise_control"] = min(scores["noise_control"], 5)

    scores["actionability"] = 0
    action_markers = ["testing", "monitoring", "deployment", "analysis"]
    scores["actionability"] += sum(1 for marker in action_markers if marker in data)
    if re.search(r"(?im)^#+\s*(architecture|review checklist|anti-patterns)\b", body):
        scores["actionability"] += 1
    scores["actionability"] = min(scores["actionability"], 5)

    total = sum(scores.values())
    max_total = len(scores) * 5
    pct = round(total * 100 / max_total)
    findings.append(Finding("INFO", rel(path, root), f"semantic score {pct}/100: {json.dumps(scores, sort_keys=True)}"))

    if scores["specificity"] <= 1:
        findings.append(Finding("ERROR", rel(path, root), "severe semantic issue: concept is too generic"))
    if scores["detectability"] <= 1:
        findings.append(Finding("ERROR", rel(path, root), "severe semantic issue: concept lacks concrete detection signals"))
    if scores["evidence_value"] <= 1:
        findings.append(Finding("WARNING", rel(path, root), "semantic issue: emitted evidence may be too weak for downstream analysis"))
    if pct < 50:
        findings.append(Finding("ERROR", rel(path, root), f"severe semantic issue: rubric score below blocking threshold ({pct}/100)"))
    elif pct < 70:
        findings.append(Finding("WARNING", rel(path, root), f"semantic quality below target ({pct}/100)"))

    return findings


def validate_catalog(target: Path, fact_generator: str | None) -> tuple[list[Finding], dict[str, Any]]:
    root = target.resolve()
    findings: list[Finding] = []
    stats: dict[str, Any] = {"markdown_files": 0, "concept_units": 0, "yaml_support_files": 0}

    if not root.exists():
        return [Finding("ERROR", str(root), "target directory does not exist")], stats
    if not root.is_dir():
        return [Finding("ERROR", str(root), "target must be a directory")], stats

    for meta_path in sorted(root.rglob("meta.yaml")):
        add(findings, "ERROR", meta_path, root, "meta.yaml is not supported; move schema data into Markdown frontmatter")

    concept_dirs = sorted({path.parent for path in root.rglob("concept.md")})
    stats["concept_units"] = len(concept_dirs)
    if not concept_dirs:
        add(findings, "ERROR", root, root, "no concept.md files found")

    for concept_dir in concept_dirs:
        md_files = sorted(concept_dir.glob("*.md"))
        if not md_files:
            add(findings, "ERROR", concept_dir, root, "concept unit has no Markdown files")
        for md_path in md_files:
            stats["markdown_files"] += 1
            data = validate_markdown(md_path, root, findings)
            if data is not None:
                try:
                    _frontmatter, body = read_frontmatter(md_path)
                except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError):
                    body = ""
                findings.extend(semantic_score(md_path, root, data, body))

    for yaml_path in sorted(root.rglob("*.yaml")):
        if yaml_path.name == "meta.yaml":
            continue
        stats["yaml_support_files"] += 1
        validate_yaml_support(yaml_path, root, findings)

    validate_fact_generator(fact_generator, root, findings)
    return findings, stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Augur concepts/units that use Markdown frontmatter")
    parser.add_argument("target", help="Path to concepts/, concepts/units/, or another concept catalog root")
    parser.add_argument(
        "--fact-generator",
        help="Optional command to run as a deterministic fact-generator check. The target path is appended.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = Path(args.target)
    findings, stats = validate_catalog(target, args.fact_generator)
    errors = [finding for finding in findings if finding.severity == "ERROR"]
    warnings = [finding for finding in findings if finding.severity == "WARNING"]
    infos = [finding for finding in findings if finding.severity == "INFO"]

    if args.json:
        print(json.dumps({
            "valid": not errors,
            "stats": stats,
            "findings": [finding.__dict__ for finding in findings],
        }, indent=2, sort_keys=True))
    else:
        print(f"Augur concept validation: {'PASS' if not errors else 'FAIL'}")
        print(f"Stats: {json.dumps(stats, sort_keys=True)}")
        for finding in findings:
            print(f"{finding.severity} [{finding.path}]: {finding.message}")
        print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s), {len(infos)} info item(s)")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

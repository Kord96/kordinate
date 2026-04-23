#!/usr/bin/env python3
"""Shared support for deterministic fact extraction.

The extractor is intentionally pragmatic:
- prefer manifests and AST for Python
- use regex heuristics for JS/TS and other common source files
- normalize raw matches into schema-shaped fact objects
"""

from __future__ import annotations

import ast
import functools
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "detectors"))

from utils import (
    component_ids_from_relationships,
    extract_auth_surfaces,
    extract_boundaries,
    extract_csharp_boundaries,
    extract_csharp_dispatch_bindings,
    extract_csharp_handlers,
    extract_csharp_registrations,
    extract_csharp_routes_structured,
    extract_config_sources,
    extract_dispatch_bindings,
    extract_entity_framework_models,
    extract_events,
    extract_go_boundaries,
    extract_go_dispatch_bindings,
    extract_go_gorm_models,
    extract_go_handlers,
    extract_go_registrations,
    extract_go_routes_structured,
    extract_handlers,
    extract_java_kotlin_boundaries,
    extract_java_kotlin_dispatch_bindings,
    extract_java_kotlin_handlers,
    extract_java_kotlin_models_structured,
    extract_java_kotlin_registrations,
    extract_java_kotlin_routes_structured,
    extract_jobs,
    extract_plugin_boundaries,
    extract_plugin_dispatch_bindings,
    extract_plugin_registrations,
    extract_registrations,
    fact_payload,
    line_number_for_offset,
    normalize_fact_record,
)


MAX_FILE_BYTES = 100 * 1024
ROOT = Path(__file__).resolve().parents[1]
FACT_DETECTORS = ROOT / "detectors"
FRAMEWORK_DETECTORS = FACT_DETECTORS / "frameworks"
FRAMEWORK_REFERENCES = ROOT / "memory" / "concepts" / "frameworks"
AST_GREP_BIN = shutil.which("ast-grep")
REPO_PROFILE_SCRIPT = ROOT.parent.parent / "shared" / "tools" / "repo_profile" / "detect_repo_profile.py"
JOERN_BATCH_EXPORTER = ROOT.parent.parent / "shared" / "tools" / "joern" / "export_augur_facts.py"
JOERN_CALL_EDGE_EXPORTER = ROOT.parent.parent / "shared" / "tools" / "joern" / "export_call_edges.py"
JOERN_DATA_TOUCH_EXPORTER = ROOT.parent.parent / "shared" / "tools" / "joern" / "export_data_touches.py"
JOERN_EXECUTION_SLICE_EXPORTER = ROOT.parent.parent / "shared" / "tools" / "joern" / "export_execution_slices.py"
JOERN_SUPPORTED_LANGUAGES = {"java", "c", "cpp", "javascript", "python", "go", "kotlin", "csharp", "php", "ruby", "swift"}
_JOERN_BATCH_CACHE: dict[tuple[str, str], dict[str, Any]] = {}

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".scala",
    ".rb",
    ".php",
    ".cs",
    ".swift",
    ".dart",
    ".lua",
    ".hs",
    ".ml",
    ".ex",
    ".exs",
    ".prisma",
    ".graphql",
    ".gql",
    ".proto",
    ".sql",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
}

EXCLUDE_DIRS = {
    ".git",
    ".agents",
    ".worktrees",
    "node_modules",
    "vendor",
    "venv",
    ".venv",
    "__pycache__",
    ".next",
    "dist",
    "build",
    ".cache",
    ".tmp",
    "site",
    "coverage",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "target",
    "bin",
    "obj",
    ".terraform",
    ".gradle",
    ".cargo",
    ".nx",
    "__snapshots__",
    ".idea",
    ".vscode",
}

def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


@dataclass(frozen=True)
class FrameworkRule:
    name: str
    manifest_packages: dict[str, tuple[str, ...]]
    source_extensions: tuple[str, ...]
    path_patterns: dict[str, tuple[str, ...]]
    source_patterns: dict[str, tuple[str, ...]]
    negative_path_patterns: tuple[str, ...]
    negative_source_patterns: tuple[str, ...]
    semantic_metadata: dict[str, Any]


MANIFEST_FILES: dict[str, str] = {
    "package_json": "package.json",
    "pyproject": "pyproject.toml",
    "requirements": "requirements.txt",
    "csproj": "*.csproj",
    "gemfile": "Gemfile",
    "composer": "composer.json",
    "cargo": "Cargo.toml",
    "pom": "pom.xml",
    "go_mod": "go.mod",
    "package_swift": "Package.swift",
    "mix_exs": "mix.exs",
}


def _tuple_strings(values: Any) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()
    items = [str(value).strip() for value in values if str(value).strip()]
    return tuple(items)


def _pattern_groups(values: Any) -> dict[str, tuple[str, ...]]:
    if not isinstance(values, dict):
        return {"strong": (), "medium": (), "weak": ()}
    return {
        "strong": _tuple_strings(values.get("strong")),
        "medium": _tuple_strings(values.get("medium")),
        "weak": _tuple_strings(values.get("weak")),
    }


def _semantic_framework_metadata(name: str) -> dict[str, Any]:
    reference_path = FRAMEWORK_REFERENCES / f"{name}.md"
    if not reference_path.exists():
        return {
            "language": "",
            "scope": "",
            "framework_kind": "",
            "status": "",
            "traits": {},
            "relationships": {
                "implements": [],
                "supports": [],
                "related_to": [],
                "uses": [],
            },
            "common_concepts": [],
            "common_failure_modes": [],
            "concepts": [],
        }
    text = reference_path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    frontmatter = yaml.safe_load(match.group(1)) if match else {}
    relationships = frontmatter.get("relationships") if isinstance(frontmatter.get("relationships"), dict) else {}
    common_concepts = _tuple_strings(frontmatter.get("common_concepts"))
    implemented = _tuple_strings(relationships.get("implements"))
    supported = _tuple_strings(relationships.get("supports"))
    related = _tuple_strings(relationships.get("related_to"))
    used = _tuple_strings(relationships.get("uses"))
    concepts = tuple(dict.fromkeys([*implemented, *supported, *common_concepts]))
    return {
        "language": str(frontmatter.get("language") or "").strip(),
        "scope": str(frontmatter.get("scope") or "").strip(),
        "framework_kind": str(frontmatter.get("framework_kind") or "").strip(),
        "status": str(frontmatter.get("status") or "").strip(),
        "traits": frontmatter.get("traits") if isinstance(frontmatter.get("traits"), dict) else {},
        "relationships": {
            "implements": list(implemented),
            "supports": list(supported),
            "related_to": list(related),
            "uses": list(used),
        },
        "common_concepts": list(common_concepts),
        "common_failure_modes": list(_tuple_strings(frontmatter.get("common_failure_modes"))),
        "concepts": list(concepts),
    }


@functools.lru_cache(maxsize=1)
def load_framework_rules() -> tuple[FrameworkRule, ...]:
    rules: list[FrameworkRule] = []
    if not FRAMEWORK_REFERENCES.exists():
        return ()
    for entry in sorted(p for p in FRAMEWORK_REFERENCES.glob("*.md") if p.name != "README.md"):
        text = entry.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
        frontmatter = yaml.safe_load(match.group(1)) if match else {}
        signatures = frontmatter.get("signatures") if isinstance(frontmatter.get("signatures"), dict) else {}
        name = str(signatures.get("framework") or entry.name).strip()
        if not name:
            continue
        manifests = signatures.get("manifest_packages") if isinstance(signatures.get("manifest_packages"), dict) else {}
        manifest_packages = {
            manifest: _tuple_strings(values)
            for manifest, values in manifests.items()
            if manifest in MANIFEST_FILES and _tuple_strings(values)
        }
        rules.append(
            FrameworkRule(
                name=name,
                manifest_packages=manifest_packages,
                source_extensions=_tuple_strings(signatures.get("source_extensions")),
                path_patterns=_pattern_groups(signatures.get("path_patterns")),
                source_patterns=_pattern_groups(signatures.get("source_patterns")),
                negative_path_patterns=_tuple_strings(signatures.get("negative_path_patterns")),
                negative_source_patterns=_tuple_strings(signatures.get("negative_source_patterns")),
                semantic_metadata=_semantic_framework_metadata(name),
            )
        )
    return tuple(rules)

CLIENT_PATTERNS = [
    (
        "http-client",
        "http-api",
        [
            r"\brequests\b",
            r"\bhttpx\b",
            r"\baiohttp\b",
            r"\bfetch\s*\(",
            r"\baxios\b",
            r"\burllib3\b",
            r"\bXMLHttpRequest\b",
        ],
    ),
    (
        "database-client",
        "database",
        [
            r"\bpsycopg2\b",
            r"\bpsycopg\b",
            r"\bsqlalchemy\b",
            r"\bprisma\b",
            r"\bmongoose\b",
            r"\bsequelize\b",
            r"\bknex\b",
            r"\bmysql\b",
            r"\bsqlite3\b",
            r"\bpg\b",
        ],
    ),
    (
        "cache-client",
        "cache",
        [
            r"\bredis\b",
            r"\bmemcached\b",
            r"\blru_cache\b",
            r"\bcachetools\b",
        ],
    ),
    (
        "message-client",
        "message-broker",
        [
            r"\bkafka\b",
            r"\bconfluent_kafka\b",
            r"\bpika\b",
            r"\bamqp\b",
            r"\brabbitmq\b",
            r"\bnats\b",
            r"\bpubsub\b",
        ],
    ),
    (
        "grpc-client",
        "grpc",
        [
            r"\bgrpc\b",
            r"\bgrpcio\b",
            r"\btonic\b",
            r"\b@grpc/grpc-js\b",
        ],
    ),
    (
        "object-store-client",
        "object-store",
        [
            r"\bboto3\b",
            r"\bbotocore\b",
            r"\bgoogle\.cloud\.storage\b",
            r"\bazure\.storage\b",
            r"\bminio\b",
            r"\bs3\b",
        ],
    ),
    (
        "auth-provider-client",
        "auth-provider",
        [
            r"\boauth\b",
            r"\boidc\b",
            r"\bAuth0\b",
            r"\bokta\b",
            r"\bkeycloak\b",
            r"\bcognito\b",
        ],
    ),
]

MODEL_PATTERNS = [
    ("pydantic", [r"BaseModel\b", r"pydantic\b", r"Field\s*\("]),
    ("sqlalchemy", [r"declarative_base\s*\(", r"Column\s*\(", r"relationship\s*\("]),
    ("django", [r"models\.Model\b", r"models\.ForeignKey\b", r"models\.ManyToManyField\b"]),
    ("prisma", [r"^\s*model\s+\w+\s*\{", r"^\s*enum\s+\w+\s*\{"]),
    ("sql", [r"CREATE\s+TABLE\b", r"ALTER\s+TABLE\b"]),
]

ROUTE_HTTP_METHODS = ("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD")
JS_ROUTE_METHODS = ("get", "post", "put", "delete", "patch", "options", "head", "use")


def stable_id(prefix: str, *parts: str) -> str:
    payload = "\x1f".join(parts).encode("utf-8")
    digest = hashlib.sha1(payload).hexdigest()[:10]
    return f"{prefix}-{digest}"


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "unknown"


def infer_component_ids(rel_path: str) -> list[str]:
    path = Path(rel_path)
    parts = [part for part in path.parts if part not in {"src", "lib", "app"}]
    if not parts:
        return []
    if len(parts) == 1:
        stem = Path(parts[0]).stem
        return [slugify(stem)]
    return [slugify(parts[0])]


def base_relationships(rel_path: str) -> dict[str, list[str]]:
    return {
        "component_ids": infer_component_ids(rel_path),
        "depends_on_fact_ids": [],
        "related_fact_ids": [],
    }


def read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


@functools.lru_cache(maxsize=4096)
def _ast_fact_matches(domain: str, file_path: str) -> list[dict[str, Any]]:
    if not AST_GREP_BIN:
        return []
    rule_file = FACT_DETECTORS / domain / "ast-grep.yaml"
    if not rule_file.exists():
        return []
    try:
        result = subprocess.run(
            [AST_GREP_BIN, "scan", "-r", str(rule_file), file_path, "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        loaded = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    return loaded if isinstance(loaded, list) else []


def extract_ast_fact_matches(domain: str, path: Path) -> list[dict[str, Any]]:
    return _ast_fact_matches(domain, str(path.resolve()))


def _meta_single(match: dict[str, Any], key: str) -> str:
    meta = match.get("metaVariables", {}).get("single", {})
    value = meta.get(key, {})
    text = value.get("text")
    return text if isinstance(text, str) else ""


def _match_line(match: dict[str, Any]) -> int:
    start = (match.get("range") or {}).get("start") or {}
    line = start.get("line")
    return int(line) + 1 if isinstance(line, int) else 1


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"', "`"}:
        return value[1:-1]
    return value


def is_source_file(path: Path) -> bool:
    name = path.name
    if name.startswith(".") and name not in {".env", ".env.example", ".env.sample"}:
        return False
    if path.suffix.lower() in SOURCE_EXTENSIONS:
        return True
    return name in {
        "README.md",
        "README.rst",
        "Dockerfile",
        "Makefile",
        "Justfile",
        "Earthfile",
        "Taskfile.yml",
        "Taskfile.yaml",
        "Procfile",
        "Tiltfile",
        "Caddyfile",
        "nginx.conf",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "Gemfile",
        "composer.json",
        "Package.swift",
        "mix.exs",
        ".env.example",
        ".env.sample",
    }


def iter_project_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, filenames in os.walk(root):
        current_path = Path(current)
        dirs[:] = [d for d in sorted(dirs) if d not in EXCLUDE_DIRS]
        for filename in sorted(filenames):
            path = current_path / filename
            if not is_source_file(path):
                continue
            content = read_text(path)
            if content is None:
                continue
            header = "\n".join(content.splitlines()[:5]).lower()
            if "auto-generated" in header or "do not edit" in header:
                continue
            files.append(path)
    return sorted(files)


def get_git_sha(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    sha = result.stdout.strip()
    return sha or None


def _normalize_joern_path(path: str) -> str:
    if not path:
        return ""
    if path.startswith("/repo/"):
        return path.removeprefix("/repo/")
    return path.lstrip("/")


def _run_joern_export(
    *,
    root: Path,
    repo_profile: dict[str, Any],
    exporter: Path,
    detector_id: str,
    domain: str,
    output_file: str,
) -> tuple[str | None, dict[str, Any], dict[str, Any] | None]:
    language = str(repo_profile.get("dominant_language") or "").strip().lower()
    if language not in JOERN_SUPPORTED_LANGUAGES:
        return language, {
            "id": detector_id,
            "domain": domain,
            "class": "cpg",
            "framework_context": [],
            "status": "skipped",
        }, None
    cache_key = (str(root.resolve()), language)
    if JOERN_BATCH_EXPORTER.exists():
        cached = _JOERN_BATCH_CACHE.get(cache_key)
        if cached is None:
            try:
                with tempfile.TemporaryDirectory(prefix="augur-joern-") as temp_dir:
                    output_path = Path(temp_dir) / "joern-augur-facts.json"
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(JOERN_BATCH_EXPORTER),
                            str(root),
                            "--language",
                            language,
                            "--output",
                            str(output_path),
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=1200,
                    )
                    if result.returncode != 0 or not output_path.exists():
                        return language, {
                            "id": detector_id,
                            "domain": domain,
                            "class": "cpg",
                            "framework_context": [],
                            "status": "failed",
                        }, None
                    cached = json.loads(output_path.read_text(encoding="utf-8"))
                    _JOERN_BATCH_CACHE[cache_key] = cached
            except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
                return language, {
                    "id": detector_id,
                    "domain": domain,
                    "class": "cpg",
                    "framework_context": [],
                    "status": "failed",
                }, None
        domain_payload = (cached.get("domains", {}) or {}).get(domain)
        if isinstance(domain_payload, dict):
            return language, {
                "id": detector_id,
                "domain": domain,
                "class": "cpg",
                "framework_context": [],
                "status": "success" if domain_payload.get("records") else "partial",
            }, domain_payload
    if not exporter.exists():
        return language, {
            "id": detector_id,
            "domain": domain,
            "class": "cpg",
            "framework_context": [],
            "status": "skipped",
        }, None

    try:
        with tempfile.TemporaryDirectory(prefix="augur-joern-") as temp_dir:
            output_path = Path(temp_dir) / output_file
            result = subprocess.run(
                [
                    sys.executable,
                    str(exporter),
                    str(root),
                    "--language",
                    language,
                    "--output",
                    str(output_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=900,
            )
            if result.returncode != 0 or not output_path.exists():
                return language, {
                    "id": detector_id,
                    "domain": domain,
                    "class": "cpg",
                    "framework_context": [],
                    "status": "failed",
                }, None
            payload = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return language, {
            "id": detector_id,
            "domain": domain,
            "class": "cpg",
            "framework_context": [],
            "status": "failed",
        }, None
    return language, {
        "id": detector_id,
        "domain": domain,
        "class": "cpg",
        "framework_context": [],
        "status": "success" if payload.get("records") else "partial",
    }, payload


def extract_joern_call_edge_facts(root: Path, repo_profile: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    language, detector_run, payload = _run_joern_export(
        root=root,
        repo_profile=repo_profile,
        exporter=JOERN_CALL_EDGE_EXPORTER,
        detector_id="joern-call-edge-detector",
        domain="call-edges",
        output_file="call-edges.json",
    )
    if payload is None:
        return [], detector_run

    facts: list[dict[str, Any]] = []
    for idx, record in enumerate(payload.get("records", [])):
        source_file = _normalize_joern_path(str(record.get("source_file", "")))
        caller_file = _normalize_joern_path(str(record.get("caller_file", "")))
        line_number = int(record.get("line_number", -1) or -1)
        caller_full_name = str(record.get("caller_full_name", "") or "")
        callee_full_name = str(record.get("callee_full_name", "") or "")
        if not source_file or not caller_full_name or not callee_full_name:
            continue

        component_ids = list(dict.fromkeys(infer_component_ids(source_file) + (infer_component_ids(caller_file) if caller_file else [])))
        source_ref = f"{source_file}:{line_number}" if line_number > 0 else source_file
        confidence = "high" if callee_full_name and callee_full_name != "<unknownFullName>" else "medium"
        caller_name = str(record.get("caller_name", "") or "")
        callee_name = str(record.get("callee_name", "") or "")
        summary = f"Detected call edge {caller_name or caller_full_name} -> {callee_name or callee_full_name}"
        facts.append(
            {
                "id": stable_id(
                    "call-edge",
                    source_file,
                    str(line_number),
                    caller_full_name,
                    callee_full_name,
                    str(idx),
                ),
                "kind": "call-edge",
                "domain": "call-edges",
                "summary": summary,
                "confidence": confidence,
                "framework_context": [],
                "source_files": [source_ref],
                "detector": {
                    "id": "joern-call-edge-detector",
                    "class": "cpg",
                    "strength": 5,
                    "rule": language or "",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "caller_name": caller_name,
                    "caller_full_name": caller_full_name,
                    "caller_signature": str(record.get("caller_signature", "") or ""),
                    "caller_file": caller_file,
                    "caller_line": int(record.get("caller_line", -1) or -1),
                    "callee_name": callee_name,
                    "callee_full_name": callee_full_name,
                    "callee_signature": str(record.get("callee_signature", "") or ""),
                    "call_code": str(record.get("call_code", "") or ""),
                    "dispatch_type": str(record.get("dispatch_type", "") or ""),
                    "source_file": source_file,
                    "line_number": line_number,
                    "column_number": int(record.get("column_number", -1) or -1),
                    "tool": "joern",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": {
                    "component_ids": component_ids,
                    "depends_on_fact_ids": [],
                    "related_fact_ids": [],
                },
            }
        )

    return facts, detector_run


def extract_joern_data_touch_facts(root: Path, repo_profile: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    language, detector_run, payload = _run_joern_export(
        root=root,
        repo_profile=repo_profile,
        exporter=JOERN_DATA_TOUCH_EXPORTER,
        detector_id="joern-data-touch-detector",
        domain="data-touches",
        output_file="data-touches.json",
    )
    if payload is None:
        return [], detector_run

    facts: list[dict[str, Any]] = []
    for idx, record in enumerate(payload.get("records", [])):
        owner_file = _normalize_joern_path(str(record.get("owner_file", "")))
        owner_full_name = str(record.get("owner_full_name", "") or "")
        touch_kind = str(record.get("touch_kind", "") or "")
        line_number = int(record.get("line_number", -1) or -1)
        if not owner_file or not owner_full_name or not touch_kind:
            continue

        target_name = str(record.get("target_name", "") or "")
        target_full_name = str(record.get("target_full_name", "") or "")
        source_ref = f"{owner_file}:{line_number}" if line_number > 0 else owner_file
        facts.append(
            {
                "id": stable_id("data-touch", owner_file, str(line_number), owner_full_name, touch_kind, target_full_name or target_name, str(idx)),
                "kind": "data-touch",
                "domain": "data-touches",
                "summary": f"Detected {touch_kind} data touch from {owner_full_name} to {target_name or target_full_name or 'unknown target'}",
                "confidence": "high" if target_full_name else "medium",
                "framework_context": [],
                "source_files": [source_ref],
                "detector": {
                    "id": "joern-data-touch-detector",
                    "class": "cpg",
                    "strength": 5,
                    "rule": language or "",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "owner_name": str(record.get("owner_name", "") or ""),
                    "owner_full_name": owner_full_name,
                    "owner_file": owner_file,
                    "owner_line": int(record.get("owner_line", -1) or -1),
                    "touch_kind": touch_kind,
                    "target_name": target_name,
                    "target_full_name": target_full_name,
                    "target_code": str(record.get("target_code", "") or ""),
                    "line_number": line_number,
                    "column_number": int(record.get("column_number", -1) or -1),
                    "tool": "joern",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": {
                    "component_ids": infer_component_ids(owner_file),
                    "depends_on_fact_ids": [],
                    "related_fact_ids": [],
                },
            }
        )

    return facts, detector_run


def extract_joern_execution_slice_facts(root: Path, repo_profile: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    language, detector_run, payload = _run_joern_export(
        root=root,
        repo_profile=repo_profile,
        exporter=JOERN_EXECUTION_SLICE_EXPORTER,
        detector_id="joern-execution-slice-detector",
        domain="execution-slices",
        output_file="execution-slices.json",
    )
    if payload is None:
        return [], detector_run

    facts: list[dict[str, Any]] = []
    for idx, record in enumerate(payload.get("records", [])):
        slice_file = _normalize_joern_path(str(record.get("slice_file", "")))
        slice_full_name = str(record.get("slice_full_name", "") or "")
        steps = record.get("steps", [])
        if not slice_file or not slice_full_name:
            continue
        if not isinstance(steps, list) or not steps:
            continue

        slice_line = int(record.get("slice_line", -1) or -1)
        source_ref = f"{slice_file}:{slice_line}" if slice_line > 0 else slice_file
        facts.append(
            {
                "id": stable_id("execution-slice", slice_file, str(slice_line), slice_full_name, str(idx)),
                "kind": "execution-slice",
                "domain": "execution-slices",
                "summary": f"Detected execution slice {slice_full_name} with {len(steps)} steps",
                "confidence": "high" if len(steps) >= 3 else "medium",
                "framework_context": [],
                "source_files": [source_ref],
                "detector": {
                    "id": "joern-execution-slice-detector",
                    "class": "cpg",
                    "strength": 5,
                    "rule": language or "",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "slice_name": str(record.get("slice_name", "") or ""),
                    "slice_full_name": slice_full_name,
                    "slice_file": slice_file,
                    "slice_line": slice_line,
                    "steps": steps,
                    "tool": "joern",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": {
                    "component_ids": infer_component_ids(slice_file),
                    "depends_on_fact_ids": [],
                    "related_fact_ids": [],
                },
            }
        )

    return facts, detector_run


def derive_joern_state_access_summary_facts(data_touch_facts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for fact in data_touch_facts:
        raw = fact.get("raw_evidence") or {}
        target_name = str(raw.get("target_name") or raw.get("target_full_name") or "").strip()
        if not target_name:
            continue
        owner_components = component_ids_from_relationships(fact.get("relationships"))
        if not owner_components:
            continue
        touch_kind = str(raw.get("touch_kind") or "read").strip().lower()
        key = (target_name, touch_kind)
        bucket = grouped.setdefault(
            key,
            {
                "target_name": target_name,
                "target_full_name": str(raw.get("target_full_name") or ""),
                "touch_kind": touch_kind,
                "components": set(),
                "source_files": set(),
                "count": 0,
            },
        )
        bucket["count"] += 1
        bucket["components"].update(owner_components)
        bucket["source_files"].update(str(item) for item in fact.get("source_files", []) if item)

    facts: list[dict[str, Any]] = []
    for idx, ((_target_name, touch_kind), bucket) in enumerate(sorted(grouped.items())):
        components = sorted(bucket["components"])
        source_files = sorted(bucket["source_files"])
        facts.append(
            {
                "id": stable_id("state-access-summary", bucket["target_name"], touch_kind, str(idx)),
                "kind": "state-access-summary",
                "domain": "state-access-summary",
                "summary": f"Components {' ,'.join(components)} {touch_kind} {bucket['target_name']}",
                "confidence": "high" if bucket["count"] >= 2 else "medium",
                "framework_context": [],
                "source_files": source_files,
                "detector": {
                    "id": "joern-state-access-summarizer",
                    "class": "inference",
                    "strength": 4,
                    "rule": "group-joern-data-touches",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "target_name": bucket["target_name"],
                    "target_full_name": bucket["target_full_name"],
                    "touch_kind": touch_kind,
                    "components": components,
                    "touch_count": bucket["count"],
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": {
                    "component_ids": components,
                    "depends_on_fact_ids": [],
                    "related_fact_ids": [],
                },
            }
        )
    detector_run = {
        "id": "joern-state-access-summarizer",
        "domain": "state-access-summary",
        "class": "inference",
        "framework_context": [],
        "status": "success" if facts else "partial",
    }
    return facts, detector_run


def derive_joern_control_hotspot_facts(execution_slice_facts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for fact in execution_slice_facts:
        raw = fact.get("raw_evidence") or {}
        slice_file = str(raw.get("slice_file") or "").strip()
        if not slice_file:
            continue
        component_ids = component_ids_from_relationships(fact.get("relationships")) or infer_component_ids(slice_file)
        component = component_ids[0] if component_ids else "unknown"
        key = (component, slice_file)
        bucket = grouped.setdefault(
            key,
            {
                "component": component,
                "slice_file": slice_file,
                "slice_names": set(),
                "source_files": set(),
                "slice_count": 0,
                "step_count": 0,
            },
        )
        bucket["slice_count"] += 1
        bucket["slice_names"].add(str(raw.get("slice_name") or raw.get("slice_full_name") or "runtime-path"))
        bucket["source_files"].update(str(item) for item in fact.get("source_files", []) if item)
        bucket["step_count"] += len(raw.get("steps") or [])

    facts: list[dict[str, Any]] = []
    for idx, ((_component, _slice_file), bucket) in enumerate(sorted(grouped.items())):
        avg_steps = round(bucket["step_count"] / max(bucket["slice_count"], 1), 2)
        facts.append(
            {
                "id": stable_id("control-hotspot", bucket["component"], bucket["slice_file"], str(idx)),
                "kind": "control-hotspot",
                "domain": "control-hotspots",
                "summary": f"{bucket['slice_file']} is a control hotspot for {bucket['component']} with {bucket['slice_count']} slices",
                "confidence": "high" if bucket["slice_count"] >= 2 else "medium",
                "framework_context": [],
                "source_files": sorted(bucket["source_files"]),
                "detector": {
                    "id": "joern-control-hotspot-summarizer",
                    "class": "inference",
                    "strength": 4,
                    "rule": "group-joern-execution-slices",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "component": bucket["component"],
                    "slice_file": bucket["slice_file"],
                    "slice_count": bucket["slice_count"],
                    "average_steps": avg_steps,
                    "slice_names": sorted(bucket["slice_names"]),
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": {
                    "component_ids": [bucket["component"]] if bucket["component"] != "unknown" else [],
                    "depends_on_fact_ids": [],
                    "related_fact_ids": [],
                },
            }
        )
    detector_run = {
        "id": "joern-control-hotspot-summarizer",
        "domain": "control-hotspots",
        "class": "inference",
        "framework_context": [],
        "status": "success" if facts else "partial",
    }
    return facts, detector_run


def infer_languages(files: Iterable[Path]) -> list[str]:
    langs: set[str] = set()
    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".py":
            langs.add("Python")
        elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
            langs.add("TypeScript" if suffix in {".ts", ".tsx"} else "JavaScript")
        elif suffix == ".go":
            langs.add("Go")
        elif suffix == ".rs":
            langs.add("Rust")
        elif suffix in {".java", ".kt", ".scala"}:
            langs.add("JVM")
        elif suffix in {".rb"}:
            langs.add("Ruby")
        elif suffix in {".php"}:
            langs.add("PHP")
        elif suffix in {".cs"}:
            langs.add("C#")
        elif suffix in {".swift"}:
            langs.add("Swift")
        elif suffix in {".ex", ".exs"}:
            langs.add("Elixir")
    if not langs:
        langs.add("Unknown")
    return sorted(langs)


def load_repo_profile(root: Path) -> dict[str, Any]:
    if not REPO_PROFILE_SCRIPT.exists():
        return {}
    try:
        result = subprocess.run(
            [sys.executable, str(REPO_PROFILE_SCRIPT), str(root), "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _load_json_file(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _find_package_json_dependencies(path: Path, packages: tuple[str, ...]) -> list[str]:
    data = _load_json_file(path)
    matches: list[str] = []
    if not isinstance(data, dict):
        return matches
    target = {item.lower() for item in packages}
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        deps = data.get(section, {})
        if not isinstance(deps, dict):
            continue
        for dep in deps:
            if dep.lower() in target:
                matches.append(f"{path.name}:{section}:{dep}")
    scripts = data.get("scripts", {})
    if isinstance(scripts, dict):
        script_blob = " ".join(str(value) for value in scripts.values()).lower()
        for dep in packages:
            if dep.lower() in script_blob:
                matches.append(f"{path.name}:scripts:{dep}")
    return matches


def _find_composer_dependencies(path: Path, packages: tuple[str, ...]) -> list[str]:
    data = _load_json_file(path)
    matches: list[str] = []
    if not isinstance(data, dict):
        return matches
    target = {item.lower() for item in packages}
    for section in ("require", "require-dev"):
        deps = data.get(section, {})
        if not isinstance(deps, dict):
            continue
        for dep in deps:
            if dep.lower() in target:
                matches.append(f"{path.name}:{section}:{dep}")
    return matches


def _find_text_manifest_matches(path: Path, packages: tuple[str, ...]) -> list[str]:
    text = read_text(path) or ""
    haystack = text.lower()
    matches: list[str] = []
    for package in packages:
        if package.lower() in haystack:
            matches.append(path.name)
    return matches


def parse_manifest_frameworks(root: Path) -> dict[str, list[tuple[str, str]]]:
    frameworks: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for rule in load_framework_rules():
        for manifest_name, packages in rule.manifest_packages.items():
            manifest_rel = MANIFEST_FILES.get(manifest_name)
            if not manifest_rel or not packages:
                continue
            candidate_paths = list(root.glob(manifest_rel)) if "*" in manifest_rel else [root / manifest_rel]
            for path in candidate_paths:
                if not path.exists():
                    continue
                if manifest_name == "package_json":
                    matches = _find_package_json_dependencies(path, packages)
                elif manifest_name == "composer":
                    matches = _find_composer_dependencies(path, packages)
                else:
                    matches = _find_text_manifest_matches(path, packages)
                for source in matches:
                    frameworks[rule.name].append((source, "strong"))
    return frameworks


def _match_signal_group(patterns: tuple[str, ...], haystack: str) -> bool:
    return any(re.search(pattern, haystack, re.M) for pattern in patterns)


def detect_frameworks(files: Iterable[Path], root: Path) -> dict[str, dict[str, Any]]:
    evidence: dict[str, list[tuple[str, str]]] = defaultdict(list)
    negative_evidence: dict[str, list[str]] = defaultdict(list)
    rules = load_framework_rules()

    for file in files:
        if not is_framework_signal_file(file, root):
            continue
        rel = str(file.relative_to(root))
        rel_lower = rel.lower()
        text = read_text(file) or ""
        suffix = file.suffix.lower()
        for rule in rules:
            if rule.source_extensions and suffix not in rule.source_extensions and suffix:
                continue
            positive_strength: str | None = None
            for strength in ("strong", "medium", "weak"):
                if _match_signal_group(rule.path_patterns.get(strength, ()), rel_lower):
                    positive_strength = strength
                    break
                if text and _match_signal_group(rule.source_patterns.get(strength, ()), text):
                    positive_strength = strength
                    break

            negative_match = False
            if text and _match_signal_group(rule.negative_source_patterns, text):
                negative_evidence[rule.name].append(rel)
                negative_match = True
            elif _match_signal_group(rule.negative_path_patterns, rel_lower):
                negative_evidence[rule.name].append(rel)
                negative_match = True

            if positive_strength:
                evidence[rule.name].append((rel, positive_strength))
            elif negative_match:
                continue

    manifest_evidence = parse_manifest_frameworks(root)
    for name, sources in manifest_evidence.items():
        evidence[name].extend(sources)

    result: dict[str, dict[str, Any]] = {}
    rules_by_name = {rule.name: rule for rule in rules}
    for name in sorted(evidence):
        weighted_sources = evidence[name]
        sources = sorted({source for source, _ in weighted_sources})
        strengths = {strength for _, strength in weighted_sources}
        manifest_like = any(":" in source or source.endswith(tuple(MANIFEST_FILES.values())) for source in sources)
        non_manifest_sources = [
            source for source in sources
            if not (":" in source or source.endswith(tuple(MANIFEST_FILES.values())))
        ]
        negatives = sorted(set(negative_evidence.get(name, [])))
        if negatives and not manifest_like:
            continue
        if negatives and manifest_like and not non_manifest_sources:
            continue
        if "strong" in strengths or manifest_like or len(sources) >= 2:
            confidence = "high"
            detector_strength = 5
        elif "medium" in strengths:
            confidence = "medium"
            detector_strength = 4
        else:
            confidence = "low"
            detector_strength = 3
        rule = rules_by_name.get(name)
        metadata = rule.semantic_metadata if rule else {}
        detector_class = "manifest" if manifest_like else "signature"
        result[name] = {
            "id": stable_id("framework", name, *sources),
            "kind": "framework",
            "domain": "frameworks",
            "summary": f"Detected {name} framework context",
            "confidence": confidence,
            "framework_context": [name],
            "source_files": sources,
            "detector": {
                "id": f"{name}-framework-detector",
                "class": detector_class,
                "strength": detector_strength,
                "rule": None,
                "bundle": "detectors:frameworks",
            },
            "raw_evidence": {
                "framework": name,
                "language": metadata.get("language", ""),
                "scope": metadata.get("scope", ""),
                "framework_kind": metadata.get("framework_kind", ""),
                "status": metadata.get("status", ""),
                "traits": metadata.get("traits", {}),
                "relationships": metadata.get("relationships", {}),
                "common_concepts": metadata.get("common_concepts", []),
                "common_failure_modes": metadata.get("common_failure_modes", []),
                "concepts": metadata.get("concepts", []),
                "signals": sources,
                "negative_signals": negatives,
            },
            "negative_evidence": negatives,
            "contradictions": [],
            "relationships": {
                "component_ids": [],
                "depends_on_fact_ids": [],
                "related_fact_ids": [],
            },
        }
    return result


def is_framework_signal_file(path: Path, root: Path) -> bool:
    name = path.name.lower()
    if name in {
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "go.mod",
        "cargo.toml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "gemfile",
        "composer.json",
        "package.swift",
        "mix.exs",
        ".env.example",
        ".env.sample",
    }:
        return True
    if path.suffix.lower() in {".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".go", ".rs", ".java", ".kt", ".scala", ".rb", ".php", ".cs", ".swift", ".dart", ".ex", ".exs"}:
        return True
    return False


def extract_python_imports(text: str) -> list[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module:
                imports.append(module)
    return [module for module in imports if not _is_stdlib_module(module)]


def _is_stdlib_module(module: str) -> bool:
    top = module.split(".", 1)[0]
    stdlib = getattr(sys, "stdlib_module_names", set())
    return top in stdlib


def extract_python_routes(text: str) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    routes: list[dict[str, Any]] = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            self._inspect(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
            self._inspect(node)
            self.generic_visit(node)

        def _inspect(self, node: ast.AST) -> None:
            decorators = getattr(node, "decorator_list", [])
            for deco in decorators:
                if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute):
                    attr = deco.func.attr.lower()
                    if attr in {"get", "post", "put", "delete", "patch", "options", "head", "route"}:
                        path = None
                        if deco.args and isinstance(deco.args[0], ast.Constant) and isinstance(deco.args[0].value, str):
                            path = deco.args[0].value
                        methods = [attr.upper()] if attr != "route" else []
                        for kw in deco.keywords:
                            if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                                methods = [
                                    elt.value.upper()
                                    for elt in kw.value.elts
                                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                                ]
                        routes.append(
                            {
                                "method": methods[0] if methods else "ANY",
                                "path": path or "",
                                "handler": getattr(node, "name", "handler"),
                                "decorator": attr,
                            }
                        )

    Visitor().visit(tree)
    return routes


def extract_js_routes(text: str) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    route_re = re.compile(
        r"\b(?P<target>app|router|fastify|server|handler)\.(?P<method>get|post|put|delete|patch|options|head|route)\s*\(\s*(?P<path>['\"`][^'\"`]+['\"`])",
        re.I,
    )
    next_route_re = re.compile(r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH)\b")
    export_route_re = re.compile(r"export\s+\{\s*(GET|POST|PUT|DELETE|PATCH)\s*\}")

    for match in route_re.finditer(text):
        path = match.group("path").strip("'\"`")
        method = match.group("method").upper()
        if method == "ROUTE":
            method = "ANY"
        routes.append(
            {
                "method": method,
                "path": path,
                "handler": match.group("target"),
                "decorator": "method-call",
            }
        )

    for pattern in (next_route_re, export_route_re):
        for match in pattern.finditer(text):
            routes.append(
                {
                    "method": match.group(1).upper(),
                    "path": "",
                    "handler": "default-export",
                    "decorator": "file-route",
                }
            )
    return routes


def extract_ast_routes(path: Path) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for match in extract_ast_fact_matches("routes", path):
        rule_id = match.get("ruleId", "")
        method = "ANY"
        if "get" in rule_id:
            method = "GET"
        elif "post" in rule_id:
            method = "POST"
        elif "put" in rule_id:
            method = "PUT"
        elif "delete" in rule_id:
            method = "DELETE"
        elif "patch" in rule_id:
            method = "PATCH"
        path_value = _strip_quotes(_meta_single(match, "PATH"))
        handler = _meta_single(match, "HANDLER") or _meta_single(match, "VIEW") or "handler"
        routes.append(
            {
                "method": method,
                "path": path_value,
                "handler": handler,
                "decorator": rule_id,
                "line": _match_line(match),
                "source": "ast",
            }
        )
    return routes


def extract_models(text: str, path: Path) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []

    if path.suffix.lower() == ".prisma":
        model_re = re.compile(r"^\s*model\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{", re.M)
        for match in model_re.finditer(text):
            models.append({"name": match.group(1), "source": "prisma", "fields": []})
        return models

    if path.suffix.lower() == ".sql":
        table_re = re.compile(r"CREATE\s+TABLE\s+([A-Za-z_][A-Za-z0-9_.\"]+)", re.I)
        for match in table_re.finditer(text):
            models.append({"name": match.group(1).strip('"'), "source": "sql", "fields": []})
        return models

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return models

    class ModelVisitor(ast.NodeVisitor):
        def visit_ClassDef(self, node: ast.ClassDef) -> Any:
            bases = {getattr(base, "id", None) or getattr(base, "attr", None) for base in node.bases}
            base_names = {b for b in bases if b}
            if base_names & {"BaseModel", "Model", "SQLModel", "DeclarativeBase"}:
                fields = [
                    stmt.target.id
                    for stmt in node.body
                    if isinstance(stmt, ast.AnnAssign)
                    and isinstance(stmt.target, ast.Name)
                ]
                models.append(
                    {
                        "name": node.name,
                        "source": "python",
                        "fields": fields,
                    }
                )
            self.generic_visit(node)

    ModelVisitor().visit(tree)
    return models


def extract_ast_models(path: Path) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    for match in extract_ast_fact_matches("models", path):
        rule_id = match.get("ruleId", "")
        name = _meta_single(match, "MODEL")
        if not name:
            continue
        if "prisma" in rule_id:
            source = "prisma"
        elif "django" in rule_id:
            source = "django"
        elif "sequelize" in rule_id:
            source = "sequelize"
        elif "mongoose" in rule_id:
            source = "mongoose"
        elif "sqlmodel" in rule_id:
            source = "sqlmodel"
        elif "pydantic" in rule_id:
            source = "pydantic"
        else:
            source = "python"
        models.append(
            {
                "name": name,
                "source": source,
                "fields": [],
                "line": _match_line(match),
                "rule_id": rule_id,
            }
        )
    return models


def extract_python_clients(text: str) -> list[dict[str, Any]]:
    clients: list[dict[str, Any]] = []
    imports = extract_python_imports(text)

    def add(kind: str, technology: str, source: str, target: str | None = None) -> None:
        clients.append(
            {
                "kind": kind,
                "technology": technology,
                "source": source,
                "target": target or "",
            }
        )

    if any(name in imports for name in ("requests", "httpx", "aiohttp")):
        tech = next(name for name in ("requests", "httpx", "aiohttp") if name in imports)
        add("http-api", tech, "import")
    if "boto3" in imports or "botocore" in imports:
        add("object-store", "boto3", "import")
    if any(name in imports for name in ("redis", "aioredis")):
        add("cache", "redis", "import")
    if any(name in imports for name in ("grpc", "grpcio")):
        add("grpc", "grpc", "import")
    if any(name in imports for name in ("pika", "kafka", "confluent_kafka")):
        add("message-broker", "messaging", "import")
    if any(name in imports for name in ("sqlalchemy", "psycopg2", "psycopg")):
        add("database", "database", "import")

    url_match = re.search(r"https?://[^\s\"'`>]+", text)
    if url_match:
        add("http-api", "url", "literal", url_match.group(0))

    return clients


def extract_js_clients(text: str) -> list[dict[str, Any]]:
    clients: list[dict[str, Any]] = []
    lowered = text.lower()

    patterns = [
        ("http-api", "fetch", [r"\bfetch\s*\(", r"\baxios\b", r"\brequest\b"]),
        ("cache", "redis", [r"\bredis\b"]),
        ("database", "orm", [r"\bprisma\b", r"\bsequelize\b", r"\bknex\b", r"\bmongoose\b"]),
        ("message-broker", "messaging", [r"\bkafka\b", r"\brabbitmq\b", r"\bnats\b", r"\bamqp\b"]),
        ("grpc", "grpc", [r"\bgrpc\b", r"\b@grpc/grpc-js\b"]),
        ("object-store", "cloud-storage", [r"\bboto3\b", r"\baws-sdk\b", r"\bminio\b"]),
        ("auth-provider", "auth", [r"\boauth\b", r"\boidc\b", r"\bkeycloak\b", r"\bokta\b", r"\bauth0\b"]),
    ]

    for kind, tech, pats in patterns:
        if any(re.search(p, lowered) for p in pats):
            clients.append({"kind": kind, "technology": tech, "source": "text", "target": ""})

    url_match = re.search(r"https?://[^\s\"'`>]+", text)
    if url_match:
        clients.append({"kind": "http-api", "technology": "url", "source": "literal", "target": url_match.group(0)})
    return clients


def extract_ast_clients(path: Path) -> list[dict[str, Any]]:
    clients: list[dict[str, Any]] = []
    for match in extract_ast_fact_matches("external-clients", path):
        rule_id = match.get("ruleId", "")
        target = _strip_quotes(_meta_single(match, "URL") or _meta_single(match, "SERVICE"))
        if "requests" in rule_id:
            kind, technology = "http-api", "requests"
        elif "httpx" in rule_id:
            kind, technology = "http-api", "httpx"
        elif "aiohttp" in rule_id:
            kind, technology = "http-api", "aiohttp"
        elif "boto3" in rule_id:
            kind, technology = "object-store", "boto3"
        elif "axios" in rule_id:
            kind, technology = "http-api", "axios"
        elif "fetch" in rule_id:
            kind, technology = "http-api", "fetch"
        elif "redis" in rule_id:
            kind, technology = "cache", "redis"
        else:
            kind, technology = "external", rule_id
        clients.append(
            {
                "kind": kind,
                "technology": technology,
                "source": "ast",
                "target": target,
                "line": _match_line(match),
                "rule_id": rule_id,
            }
        )
    return clients


def extract_ast_middleware(path: Path) -> list[dict[str, Any]]:
    middleware: list[dict[str, Any]] = []
    for match in extract_ast_fact_matches("middleware", path):
        rule_id = match.get("ruleId", "")
        name = _meta_single(match, "MIDDLEWARE") or _meta_single(match, "HANDLER") or _meta_single(match, "ARGS")
        middleware.append(
            {
                "name": name or rule_id,
                "callsite": path.name,
                "auth": "guard" if "guard" in rule_id else "",
                "validation": "validation" if "validation" in rule_id else "",
                "ordering": "",
                "line": _match_line(match),
                "rule_id": rule_id,
            }
        )
    return middleware


def extract_ast_auth_surfaces(path: Path) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    for match in extract_ast_fact_matches("auth-surface", path):
        rule_id = match.get("ruleId", "")
        if "jwt" in rule_id:
            technology = "jwt"
        elif "bearer" in rule_id:
            technology = "token-auth"
        elif "next" in rule_id:
            technology = "route-guard"
        elif "guard" in rule_id:
            technology = "route-guard"
        else:
            technology = "oauth-oidc"
        surfaces.append(
            {
                "technology": technology,
                "auth": technology,
                "line": _match_line(match),
                "rule_id": rule_id,
            }
        )
    return surfaces


def extract_python_imports_from_file(path: Path, text: str) -> list[str]:
    imports = extract_python_imports(text)
    if path.name in {"__init__.py", "manage.py", "main.py", "app.py"}:
        return imports
    return imports


def extract_js_imports(text: str) -> list[str]:
    imports: list[str] = []
    import_re = re.compile(r"""^\s*import\s+(?:[^'"]+\s+from\s+)?['"]([^'"]+)['"]""", re.M)
    require_re = re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)""")
    export_from_re = re.compile(r"""from\s+['"]([^'"]+)['"]""")
    for pattern in (import_re, require_re, export_from_re):
        imports.extend(pattern.findall(text))
    return imports


def parse_python_file(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    rel = str(path.relative_to(root))
    relationships = base_relationships(rel)
    imports = extract_python_imports_from_file(path, text)
    client_matches = extract_python_clients(text)

    for import_name in imports:
        top = import_name.split(".", 1)[0]
        facts.append(
            {
                "kind": "import-edge",
                "domain": "import-graph",
                "summary": f"{rel} imports {import_name}",
                "confidence": "high",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "python-import-graph",
                    "class": "ast",
                    "strength": 5,
                    "rule": "python-import",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "from": rel,
                    "to": top,
                    "import_type": "python",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    routes = extract_ast_routes(path) or extract_python_routes(text)
    for idx, route in enumerate(routes, start=1):
        path_value = route["path"] or ""
        method = route["method"]
        handler = route["handler"]
        line_no = int(route.get("line", idx))
        fact_id = stable_id("route", rel, str(idx), method, path_value, handler)
        facts.append(
            {
                "id": fact_id,
                "kind": "route",
                "domain": "routes",
                "summary": f"{method} {path_value or '(unresolved path)'} handled by {handler}",
                "confidence": "high" if path_value else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{line_no}"],
                "detector": {
                    "id": "python-route-detector",
                    "class": "ast",
                    "strength": 5,
                    "rule": route.get("decorator", f"route-{method.lower()}"),
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "style": "rest",
                    "method": method,
                    "path": path_value,
                    "handler": handler,
                    "router": "python-decorator",
                    "auth": "",
                    "validation": "",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    models = extract_ast_models(path) or extract_models(text, path)
    for idx, model in enumerate(models, start=1):
        fact_id = stable_id("model", rel, model["name"], str(idx))
        line_no = int(model.get("line", idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "model",
                "domain": "models",
                "summary": f"Detected {model['source']} model {model['name']}",
                "confidence": "high" if model["fields"] else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{line_no}"],
                "detector": {
                    "id": f"python-{model['source']}-model-detector",
                    "class": "ast",
                    "strength": 5,
                    "rule": model.get("rule_id", model["source"]),
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "technology": model["source"],
                    "entity": model["name"],
                    "fields": model["fields"],
                    "relations": [],
                    "migration_path": "",
                    "store_purpose": "source-of-truth",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, client in enumerate(extract_ast_clients(path) or client_matches, start=1):
        fact_id = stable_id("client", rel, client["kind"], client["technology"], str(idx))
        line_no = int(client.get("line", 1))
        facts.append(
            {
                "id": fact_id,
                "kind": "external-client",
                "domain": "external-clients",
                "summary": f"Detected {client['kind']} client via {client['technology']}",
                "confidence": "high" if client["source"] in {"import", "ast"} else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{line_no}"],
                "detector": {
                    "id": "python-client-detector",
                    "class": "ast" if client["source"] == "ast" else ("signature" if client["source"] == "import" else "regex"),
                    "strength": 5 if client["source"] == "ast" else 4,
                    "rule": client.get("rule_id", client["technology"]),
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "technology": client["technology"],
                    "target": client["target"],
                    "callsite": rel,
                    "timeout": "",
                    "retry": "",
                    "circuit_breaker": "",
                    "fallback": "",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, mw in enumerate(extract_ast_middleware(path), start=1):
        facts.append(
            {
                "id": stable_id("middleware", rel, mw["name"], str(idx)),
                "kind": "middleware",
                "domain": "middleware",
                "summary": f"Detected middleware {mw['name']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{int(mw.get('line', 1))}"],
                "detector": {
                    "id": "python-middleware-detector",
                    "class": "ast",
                    "strength": 4,
                    "rule": mw.get("rule_id", mw["name"]),
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "name": mw["name"],
                    "callsite": rel,
                    "auth": mw.get("auth", ""),
                    "validation": mw.get("validation", ""),
                    "ordering": mw.get("ordering", ""),
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, surface in enumerate(extract_ast_auth_surfaces(path) or extract_auth_surfaces(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("auth", rel, surface["technology"], str(idx)),
                "kind": "auth-surface",
                "domain": "auth-surface",
                "summary": f"Detected auth surface {surface['technology']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{int(surface.get('line', 1))}"],
                "detector": {
                    "id": "python-auth-detector",
                    "class": "ast" if "rule_id" in surface else "regex",
                    "strength": 5 if "rule_id" in surface else 3,
                    "rule": surface.get("rule_id", surface["technology"]),
                    "bundle": "detectors:facts",
                },
                "raw_evidence": surface,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, config in enumerate(extract_config_sources(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("config", rel, config["source_type"], str(idx)),
                "kind": "config-source",
                "domain": "config",
                "summary": f"Detected config source {config['source_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "python-config-detector",
                    "class": "regex",
                    "strength": 3,
                    "rule": config["source_type"],
                    "bundle": "detectors:facts",
                },
                "raw_evidence": config,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, job in enumerate(extract_jobs(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("job", rel, job["job_type"], str(idx)),
                "kind": "job",
                "domain": "jobs",
                "summary": f"Detected job type {job['job_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "python-job-detector",
                    "class": "regex",
                    "strength": 3,
                    "rule": job["job_type"],
                    "bundle": "detectors:facts",
                },
                "raw_evidence": job,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, event in enumerate(extract_events(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("event", rel, event["event_type"], str(idx)),
                "kind": "event",
                "domain": "events",
                "summary": f"Detected event flow {event['event_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "python-event-detector",
                    "class": "regex",
                    "strength": 3,
                    "rule": event["event_type"],
                    "bundle": "detectors:facts",
                },
                "raw_evidence": event,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_registrations(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("registration", rel, item["registration_type"], str(idx)),
                "kind": "registration",
                "domain": "registrations",
                "summary": f"Detected {item['registration_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "python-registration-detector", "class": "signature", "strength": 3, "rule": item["registration_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_handlers(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("handler", rel, item["handler_type"], item["name"], str(idx)),
                "kind": "handler",
                "domain": "handlers",
                "summary": f"Detected {item['handler_type']} {item['name']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "python-handler-detector", "class": "signature", "strength": 3, "rule": item["handler_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_dispatch_bindings(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("dispatch", rel, item["binding_type"], item["channel"], str(idx)),
                "kind": "dispatch-binding",
                "domain": "dispatch-bindings",
                "summary": f"Detected {item['binding_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "python-dispatch-detector", "class": "signature", "strength": 3, "rule": item["binding_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_boundaries(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("boundary", rel, item["boundary_type"], item["interface"], item["implementation"], str(idx)),
                "kind": "boundary",
                "domain": "boundaries",
                "summary": f"Detected {item['boundary_type']} boundary",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "python-boundary-detector", "class": "signature", "strength": 3, "rule": item["boundary_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    append_plugin_facts(facts, rel, relationships, text, path.suffix.lower())
    return facts


def parse_js_ts_file(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    rel = str(path.relative_to(root))
    relationships = base_relationships(rel)
    imports = extract_js_imports(text)

    for idx, import_name in enumerate(imports, start=1):
        facts.append(
            {
                "id": stable_id("import", rel, import_name, str(idx)),
                "kind": "import-edge",
                "domain": "import-graph",
                "summary": f"{rel} imports {import_name}",
                "confidence": "high",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "js-import-graph",
                    "class": "regex",
                    "strength": 4,
                    "rule": "js-import",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "from": rel,
                    "to": import_name,
                    "import_type": "javascript",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    routes = extract_ast_routes(path) or extract_js_routes(text)
    for idx, route in enumerate(routes, start=1):
        fact_id = stable_id("route", rel, str(idx), route["method"], route["path"], route["handler"])
        line_no = int(route.get("line", idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "route",
                "domain": "routes",
                "summary": f"{route['method']} {route['path'] or '(file route)'} handled by {route['handler']}",
                "confidence": "high" if route["path"] else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{line_no}"],
                "detector": {
                    "id": "js-route-detector",
                    "class": "ast" if route.get("source") == "ast" else "regex",
                    "strength": 5 if route.get("source") == "ast" else 4,
                    "rule": route["decorator"],
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "style": "rest",
                    "method": route["method"],
                    "path": route["path"],
                    "handler": route["handler"],
                    "router": "js-method-call",
                    "auth": "",
                    "validation": "",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    models = extract_ast_models(path) or extract_models(text, path)
    for idx, model in enumerate(models, start=1):
        fact_id = stable_id("model", rel, model["name"], str(idx))
        line_no = int(model.get("line", idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "model",
                "domain": "models",
                "summary": f"Detected {model['source']} model {model['name']}",
                "confidence": "high" if model["fields"] else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{line_no}"],
                "detector": {
                    "id": f"js-{model['source']}-model-detector",
                    "class": "ast" if "rule_id" in model else "regex",
                    "strength": 5 if "rule_id" in model else 4,
                    "rule": model.get("rule_id", model["source"]),
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "technology": model["source"],
                    "entity": model["name"],
                    "fields": model["fields"],
                    "relations": [],
                    "migration_path": "",
                    "store_purpose": "source-of-truth",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, client in enumerate(extract_ast_clients(path) or extract_js_clients(text), start=1):
        fact_id = stable_id("client", rel, client["kind"], client["technology"], str(idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "external-client",
                "domain": "external-clients",
                "summary": f"Detected {client['kind']} client via {client['technology']}",
                "confidence": "high" if client.get("source") == "ast" else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{int(client.get('line', 1))}"],
                "detector": {
                    "id": "js-client-detector",
                    "class": "ast" if client.get("source") == "ast" else "regex",
                    "strength": 5 if client.get("source") == "ast" else 4,
                    "rule": client.get("rule_id", client["technology"]),
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "technology": client["technology"],
                    "target": client["target"],
                    "callsite": rel,
                    "timeout": "",
                    "retry": "",
                    "circuit_breaker": "",
                    "fallback": "",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, mw in enumerate(extract_ast_middleware(path), start=1):
        facts.append(
            {
                "id": stable_id("middleware", rel, mw["name"], str(idx)),
                "kind": "middleware",
                "domain": "middleware",
                "summary": f"Detected middleware {mw['name']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{int(mw.get('line', 1))}"],
                "detector": {
                    "id": "js-middleware-detector",
                    "class": "ast",
                    "strength": 4,
                    "rule": mw.get("rule_id", mw["name"]),
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "name": mw["name"],
                    "callsite": rel,
                    "auth": mw.get("auth", ""),
                    "validation": mw.get("validation", ""),
                    "ordering": mw.get("ordering", ""),
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, surface in enumerate(extract_ast_auth_surfaces(path) or extract_auth_surfaces(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("auth", rel, surface["technology"], str(idx)),
                "kind": "auth-surface",
                "domain": "auth-surface",
                "summary": f"Detected auth surface {surface['technology']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{int(surface.get('line', 1))}"],
                "detector": {
                    "id": "js-auth-detector",
                    "class": "ast" if "rule_id" in surface else "regex",
                    "strength": 5 if "rule_id" in surface else 3,
                    "rule": surface.get("rule_id", surface["technology"]),
                    "bundle": "detectors:facts",
                },
                "raw_evidence": surface,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, config in enumerate(extract_config_sources(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("config", rel, config["source_type"], str(idx)),
                "kind": "config-source",
                "domain": "config",
                "summary": f"Detected config source {config['source_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "js-config-detector",
                    "class": "regex",
                    "strength": 3,
                    "rule": config["source_type"],
                    "bundle": "detectors:facts",
                },
                "raw_evidence": config,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, job in enumerate(extract_jobs(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("job", rel, job["job_type"], str(idx)),
                "kind": "job",
                "domain": "jobs",
                "summary": f"Detected job type {job['job_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "js-job-detector",
                    "class": "regex",
                    "strength": 3,
                    "rule": job["job_type"],
                    "bundle": "detectors:facts",
                },
                "raw_evidence": job,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, event in enumerate(extract_events(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("event", rel, event["event_type"], str(idx)),
                "kind": "event",
                "domain": "events",
                "summary": f"Detected event flow {event['event_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "js-event-detector",
                    "class": "regex",
                    "strength": 3,
                    "rule": event["event_type"],
                    "bundle": "detectors:facts",
                },
                "raw_evidence": event,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_registrations(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("registration", rel, item["registration_type"], str(idx)),
                "kind": "registration",
                "domain": "registrations",
                "summary": f"Detected {item['registration_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "js-registration-detector", "class": "signature", "strength": 3, "rule": item["registration_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_handlers(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("handler", rel, item["handler_type"], item["name"], str(idx)),
                "kind": "handler",
                "domain": "handlers",
                "summary": f"Detected {item['handler_type']} {item['name']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "js-handler-detector", "class": "signature", "strength": 3, "rule": item["handler_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_dispatch_bindings(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("dispatch", rel, item["binding_type"], item["channel"], str(idx)),
                "kind": "dispatch-binding",
                "domain": "dispatch-bindings",
                "summary": f"Detected {item['binding_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "js-dispatch-detector", "class": "signature", "strength": 3, "rule": item["binding_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_boundaries(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("boundary", rel, item["boundary_type"], item["interface"], item["implementation"], str(idx)),
                "kind": "boundary",
                "domain": "boundaries",
                "summary": f"Detected {item['boundary_type']} boundary",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "js-boundary-detector", "class": "signature", "strength": 3, "rule": item["boundary_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    append_plugin_facts(facts, rel, relationships, text, path.suffix.lower())
    return facts


def parse_go_file(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    rel = str(path.relative_to(root))
    relationships = base_relationships(rel)

    for idx, route in enumerate(extract_go_routes_structured(text), start=1):
        facts.append(
            {
                "id": stable_id("route", rel, route["method"], route["path"], route["handler"], str(idx)),
                "kind": "route",
                "domain": "routes",
                "summary": f"{route['method']} {route['path']} handled by {route['handler']}",
                "confidence": "high",
                "framework_context": [],
                "source_files": [f"{rel}:{route['line']}"],
                "detector": {
                    "id": "go-route-detector",
                    "class": "structured",
                    "strength": 5,
                    "rule": route["decorator"],
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "style": "rest",
                    "method": route["method"],
                    "path": route["path"],
                    "handler": route["handler"],
                    "router": "go-structured",
                    "auth": "",
                    "validation": "",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, model in enumerate(extract_go_gorm_models(text), start=1):
        facts.append(
            {
                "id": stable_id("model", rel, model["name"], str(idx)),
                "kind": "model",
                "domain": "models",
                "summary": f"Detected GORM model {model['name']}",
                "confidence": "high" if model["fields"] else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{model['line']}"],
                "detector": {
                    "id": "go-gorm-model-detector",
                    "class": "structured",
                    "strength": 5,
                    "rule": "gorm-struct",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "technology": "gorm",
                    "entity": model["name"],
                    "fields": model["fields"],
                    "relations": [],
                    "migration_path": "",
                    "store_purpose": "source-of-truth",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_go_registrations(text), start=1):
        facts.append(
            {
                "id": stable_id("registration", rel, item["registration_type"], item["symbol"], str(idx)),
                "kind": "registration",
                "domain": "registrations",
                "summary": f"Detected {item['registration_type']}",
                "confidence": "high",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "go-registration-detector", "class": "structured", "strength": 4, "rule": item["registration_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_go_handlers(text), start=1):
        facts.append(
            {
                "id": stable_id("handler", rel, item["handler_type"], item["name"], str(idx)),
                "kind": "handler",
                "domain": "handlers",
                "summary": f"Detected {item['handler_type']} {item['name']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "go-handler-detector", "class": "structured", "strength": 4, "rule": item["handler_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_go_dispatch_bindings(text), start=1):
        facts.append(
            {
                "id": stable_id("dispatch", rel, item["binding_type"], item["channel"], str(idx)),
                "kind": "dispatch-binding",
                "domain": "dispatch-bindings",
                "summary": f"Detected {item['binding_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "go-dispatch-detector", "class": "structured", "strength": 4, "rule": item["binding_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_go_boundaries(text), start=1):
        facts.append(
            {
                "id": stable_id("boundary", rel, item["boundary_type"], item["interface"], item["implementation"], str(idx)),
                "kind": "boundary",
                "domain": "boundaries",
                "summary": f"Detected {item['boundary_type']} boundary",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "go-boundary-detector", "class": "structured", "strength": 4, "rule": item["boundary_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, config in enumerate(extract_config_sources(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("config", rel, config["source_type"], str(idx)), "kind": "config-source", "domain": "config", "summary": f"Detected config source {config['source_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "go-config-detector", "class": "regex", "strength": 3, "rule": config["source_type"], "bundle": "detectors:facts"}, "raw_evidence": config, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    for idx, job in enumerate(extract_jobs(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("job", rel, job["job_type"], str(idx)), "kind": "job", "domain": "jobs", "summary": f"Detected job type {job['job_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "go-job-detector", "class": "regex", "strength": 3, "rule": job["job_type"], "bundle": "detectors:facts"}, "raw_evidence": job, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    for idx, event in enumerate(extract_events(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("event", rel, event["event_type"], str(idx)), "kind": "event", "domain": "events", "summary": f"Detected event flow {event['event_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "go-event-detector", "class": "regex", "strength": 3, "rule": event["event_type"], "bundle": "detectors:facts"}, "raw_evidence": event, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    append_plugin_facts(facts, rel, relationships, text, path.suffix.lower())
    return facts


def parse_csharp_file(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    rel = str(path.relative_to(root))
    relationships = base_relationships(rel)

    for idx, route in enumerate(extract_csharp_routes_structured(text), start=1):
        facts.append(
            {
                "id": stable_id("route", rel, route["method"], route["path"], route["decorator"], str(idx)),
                "kind": "route",
                "domain": "routes",
                "summary": f"{route['method']} {route['path']} via {route['decorator']}",
                "confidence": "high",
                "framework_context": [],
                "source_files": [f"{rel}:{route['line']}"],
                "detector": {
                    "id": "csharp-route-detector",
                    "class": "structured",
                    "strength": 5,
                    "rule": route["decorator"],
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "style": "rest",
                    "method": route["method"],
                    "path": route["path"],
                    "handler": route["handler"],
                    "router": "aspnet-structured",
                    "auth": "",
                    "validation": "",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, model in enumerate(extract_entity_framework_models(text), start=1):
        facts.append(
            {
                "id": stable_id("model", rel, model["name"], str(idx)),
                "kind": "model",
                "domain": "models",
                "summary": f"Detected Entity Framework model {model['name']}",
                "confidence": "high" if model["fields"] else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{model['line']}"],
                "detector": {
                    "id": "csharp-ef-model-detector",
                    "class": "structured",
                    "strength": 5,
                    "rule": "entity-framework",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "technology": "entity-framework",
                    "entity": model["name"],
                    "fields": model["fields"],
                    "relations": [],
                    "migration_path": "",
                    "store_purpose": "source-of-truth",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_csharp_registrations(text), start=1):
        facts.append(
            {
                "id": stable_id("registration", rel, item["registration_type"], item["symbol"], str(idx)),
                "kind": "registration",
                "domain": "registrations",
                "summary": f"Detected {item['registration_type']}",
                "confidence": "high",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "csharp-registration-detector", "class": "structured", "strength": 4, "rule": item["registration_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_csharp_handlers(text), start=1):
        facts.append(
            {
                "id": stable_id("handler", rel, item["handler_type"], item["name"], str(idx)),
                "kind": "handler",
                "domain": "handlers",
                "summary": f"Detected {item['handler_type']} {item['name']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "csharp-handler-detector", "class": "structured", "strength": 4, "rule": item["handler_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_csharp_dispatch_bindings(text), start=1):
        facts.append(
            {
                "id": stable_id("dispatch", rel, item["binding_type"], item["channel"], str(idx)),
                "kind": "dispatch-binding",
                "domain": "dispatch-bindings",
                "summary": f"Detected {item['binding_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "csharp-dispatch-detector", "class": "structured", "strength": 4, "rule": item["binding_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, item in enumerate(extract_csharp_boundaries(text), start=1):
        facts.append(
            {
                "id": stable_id("boundary", rel, item["boundary_type"], item["interface"], item["implementation"], str(idx)),
                "kind": "boundary",
                "domain": "boundaries",
                "summary": f"Detected {item['boundary_type']} boundary",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "csharp-boundary-detector", "class": "structured", "strength": 4, "rule": item["boundary_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, config in enumerate(extract_config_sources(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("config", rel, config["source_type"], str(idx)), "kind": "config-source", "domain": "config", "summary": f"Detected config source {config['source_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "csharp-config-detector", "class": "regex", "strength": 3, "rule": config["source_type"], "bundle": "detectors:facts"}, "raw_evidence": config, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    for idx, job in enumerate(extract_jobs(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("job", rel, job["job_type"], str(idx)), "kind": "job", "domain": "jobs", "summary": f"Detected job type {job['job_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "csharp-job-detector", "class": "regex", "strength": 3, "rule": job["job_type"], "bundle": "detectors:facts"}, "raw_evidence": job, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    for idx, event in enumerate(extract_events(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("event", rel, event["event_type"], str(idx)), "kind": "event", "domain": "events", "summary": f"Detected event flow {event['event_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "csharp-event-detector", "class": "regex", "strength": 3, "rule": event["event_type"], "bundle": "detectors:facts"}, "raw_evidence": event, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    return facts


def parse_java_kotlin_file(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    rel = str(path.relative_to(root))
    relationships = base_relationships(rel)

    for idx, route in enumerate(extract_java_kotlin_routes_structured(text), start=1):
        facts.append(
            {
                "id": stable_id("route", rel, route["method"], route["path"], route["decorator"], str(idx)),
                "kind": "route",
                "domain": "routes",
                "summary": f"{route['method']} {route['path']} via {route['decorator']}",
                "confidence": "high",
                "framework_context": [],
                "source_files": [f"{rel}:{route['line']}"],
                "detector": {"id": "java-kotlin-route-detector", "class": "structured", "strength": 5, "rule": route["decorator"], "bundle": "detectors:facts"},
                "raw_evidence": {"style": "rest", "method": route["method"], "path": route["path"], "handler": route["handler"], "router": "java-kotlin-structured", "auth": "", "validation": ""},
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    for idx, model in enumerate(extract_java_kotlin_models_structured(text), start=1):
        facts.append(
            {
                "id": stable_id("model", rel, model["name"], str(idx)),
                "kind": "model",
                "domain": "models",
                "summary": f"Detected {model['source']} model {model['name']}",
                "confidence": "high" if model["fields"] else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{model['line']}"],
                "detector": {"id": "java-kotlin-model-detector", "class": "structured", "strength": 5, "rule": model["source"], "bundle": "detectors:facts"},
                "raw_evidence": {"technology": model["source"], "entity": model["name"], "fields": model["fields"], "relations": [], "migration_path": "", "store_purpose": "source-of-truth"},
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

    structured_groups = [
        ("registration", "registrations", "java-kotlin-registration-detector", extract_java_kotlin_registrations(text), "registration_type", lambda item: f"Detected {item['registration_type']}"),
        ("handler", "handlers", "java-kotlin-handler-detector", extract_java_kotlin_handlers(text), "handler_type", lambda item: f"Detected {item['handler_type']} {item['name']}"),
        ("dispatch", "dispatch-bindings", "java-kotlin-dispatch-detector", extract_java_kotlin_dispatch_bindings(text), "binding_type", lambda item: f"Detected {item['binding_type']}"),
        ("boundary", "boundaries", "java-kotlin-boundary-detector", extract_java_kotlin_boundaries(text), "boundary_type", lambda item: f"Detected {item['boundary_type']} boundary"),
    ]
    for prefix, domain, detector_id, items, rule_key, summary in structured_groups:
        for idx, item in enumerate(items, start=1):
            facts.append(
                {
                    "id": stable_id(prefix, rel, str(item.get(rule_key, "")), str(item.get("line", idx)), str(idx)),
                    "kind": "dispatch-binding" if domain == "dispatch-bindings" else prefix,
                    "domain": domain,
                    "summary": summary(item),
                    "confidence": "medium" if domain in {"handlers", "boundaries"} else "high",
                    "framework_context": [],
                    "source_files": [f"{rel}:{int(item.get('line', 1))}"],
                    "detector": {"id": detector_id, "class": "structured", "strength": 4, "rule": item.get(rule_key, ""), "bundle": "detectors:facts"},
                    "raw_evidence": item,
                    "negative_evidence": [],
                    "contradictions": [],
                    "relationships": relationships,
                }
            )

    for idx, config in enumerate(extract_config_sources(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("config", rel, config["source_type"], str(idx)), "kind": "config-source", "domain": "config", "summary": f"Detected config source {config['source_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "java-kotlin-config-detector", "class": "regex", "strength": 3, "rule": config["source_type"], "bundle": "detectors:facts"}, "raw_evidence": config, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    for idx, job in enumerate(extract_jobs(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("job", rel, job["job_type"], str(idx)), "kind": "job", "domain": "jobs", "summary": f"Detected job type {job['job_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "java-kotlin-job-detector", "class": "regex", "strength": 3, "rule": job["job_type"], "bundle": "detectors:facts"}, "raw_evidence": job, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    for idx, event in enumerate(extract_events(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("event", rel, event["event_type"], str(idx)), "kind": "event", "domain": "events", "summary": f"Detected event flow {event['event_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "java-kotlin-event-detector", "class": "regex", "strength": 3, "rule": event["event_type"], "bundle": "detectors:facts"}, "raw_evidence": event, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    append_plugin_facts(facts, rel, relationships, text, path.suffix.lower())
    return facts


def append_plugin_facts(
    facts: list[dict[str, Any]],
    rel: str,
    relationships: dict[str, Any],
    text: str,
    suffix: str,
) -> None:
    for idx, item in enumerate(extract_plugin_registrations(text, suffix), start=1):
        facts.append(
            {
                "id": stable_id("registration", rel, item["registration_type"], item["symbol"], "plugin", str(idx)),
                "kind": "registration",
                "domain": "registrations",
                "summary": f"Detected {item['registration_type']}",
                "confidence": "high",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "plugin-registration-detector", "class": "signature", "strength": 4, "rule": item["registration_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )
    for idx, item in enumerate(extract_plugin_dispatch_bindings(text, suffix), start=1):
        facts.append(
            {
                "id": stable_id("dispatch", rel, item["binding_type"], item["channel"], "plugin", str(idx)),
                "kind": "dispatch-binding",
                "domain": "dispatch-bindings",
                "summary": f"Detected {item['binding_type']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "plugin-dispatch-detector", "class": "signature", "strength": 4, "rule": item["binding_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )
    for idx, item in enumerate(extract_plugin_boundaries(text, suffix), start=1):
        facts.append(
            {
                "id": stable_id("boundary", rel, item["boundary_type"], item["interface"], "plugin", str(idx)),
                "kind": "boundary",
                "domain": "boundaries",
                "summary": f"Detected {item['boundary_type']} boundary",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{item['line']}"],
                "detector": {"id": "plugin-boundary-detector", "class": "signature", "strength": 4, "rule": item["boundary_type"], "bundle": "detectors:facts"},
                "raw_evidence": item,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )


def parse_generic_source_file(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    rel = str(path.relative_to(root))
    relationships = base_relationships(rel)

    generic_specs = [
        ("registration", "registrations", "generic-registration-detector", extract_registrations(text, path.suffix.lower()), "registration_type", lambda item: f"Detected {item['registration_type']}"),
        ("handler", "handlers", "generic-handler-detector", extract_handlers(text, path.suffix.lower()), "handler_type", lambda item: f"Detected {item['handler_type']} {item['name']}"),
        ("dispatch", "dispatch-bindings", "generic-dispatch-detector", extract_dispatch_bindings(text, path.suffix.lower()), "binding_type", lambda item: f"Detected {item['binding_type']}"),
        ("boundary", "boundaries", "generic-boundary-detector", extract_boundaries(text, path.suffix.lower()), "boundary_type", lambda item: f"Detected {item['boundary_type']} boundary"),
    ]
    for prefix, domain, detector_id, items, rule_key, summary in generic_specs:
        for idx, item in enumerate(items, start=1):
            facts.append(
                {
                    "id": stable_id(prefix, rel, str(item.get(rule_key, "")), str(item.get("line", idx)), str(idx)),
                    "kind": "dispatch-binding" if domain == "dispatch-bindings" else prefix,
                    "domain": domain,
                    "summary": summary(item),
                    "confidence": "medium",
                    "framework_context": [],
                    "source_files": [f"{rel}:{int(item.get('line', 1))}"],
                    "detector": {"id": detector_id, "class": "signature", "strength": 3, "rule": item.get(rule_key, ""), "bundle": "detectors:facts"},
                    "raw_evidence": item,
                    "negative_evidence": [],
                    "contradictions": [],
                    "relationships": relationships,
                }
            )

    for idx, config in enumerate(extract_config_sources(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("config", rel, config["source_type"], str(idx)), "kind": "config-source", "domain": "config", "summary": f"Detected config source {config['source_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "generic-config-detector", "class": "regex", "strength": 3, "rule": config["source_type"], "bundle": "detectors:facts"}, "raw_evidence": config, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    for idx, job in enumerate(extract_jobs(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("job", rel, job["job_type"], str(idx)), "kind": "job", "domain": "jobs", "summary": f"Detected job type {job['job_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "generic-job-detector", "class": "regex", "strength": 3, "rule": job["job_type"], "bundle": "detectors:facts"}, "raw_evidence": job, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    for idx, event in enumerate(extract_events(text, path.suffix.lower()), start=1):
        facts.append({"id": stable_id("event", rel, event["event_type"], str(idx)), "kind": "event", "domain": "events", "summary": f"Detected event flow {event['event_type']}", "confidence": "medium", "framework_context": [], "source_files": [f"{rel}:1"], "detector": {"id": "generic-event-detector", "class": "regex", "strength": 3, "rule": event["event_type"], "bundle": "detectors:facts"}, "raw_evidence": event, "negative_evidence": [], "contradictions": [], "relationships": relationships})
    append_plugin_facts(facts, rel, relationships, text, path.suffix.lower())
    return facts


def parse_prisma_file(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    rel = str(path.relative_to(root))
    models = extract_models(text, path)
    for idx, model in enumerate(models, start=1):
        fact_id = stable_id("model", rel, model["name"], str(idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "model",
                "domain": "models",
                "summary": f"Detected Prisma model {model['name']}",
                "confidence": "high",
                "framework_context": [],
                "source_files": [f"{rel}:{idx}"],
                "detector": {
                    "id": "prisma-model-detector",
                    "class": "regex",
                    "strength": 5,
                    "rule": "prisma-model",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "technology": "prisma",
                    "entity": model["name"],
                    "fields": model["fields"],
                    "relations": [],
                    "migration_path": "",
                    "store_purpose": "source-of-truth",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": {
                    "component_ids": [],
                    "depends_on_fact_ids": [],
                    "related_fact_ids": [],
                },
            }
        )
    return facts


def parse_sql_file(path: Path, root: Path, text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    rel = str(path.relative_to(root))
    models = extract_models(text, path)
    for idx, model in enumerate(models, start=1):
        fact_id = stable_id("model", rel, model["name"], str(idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "model",
                "domain": "models",
                "summary": f"Detected SQL table {model['name']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{idx}"],
                "detector": {
                    "id": "sql-model-detector",
                    "class": "regex",
                    "strength": 4,
                    "rule": "create-table",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "technology": "sql",
                    "entity": model["name"],
                    "fields": model["fields"],
                    "relations": [],
                    "migration_path": "",
                    "store_purpose": "source-of-truth",
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": {
                    "component_ids": [],
                    "depends_on_fact_ids": [],
                    "related_fact_ids": [],
                },
            }
        )
    return facts


HOT_FILE_DOMAIN_WEIGHTS: dict[str, int] = {
    "frameworks": 5,
    "boundaries": 5,
    "dispatch-bindings": 5,
    "handlers": 4,
    "routes": 4,
    "registrations": 3,
    "external-clients": 3,
    "middleware": 3,
    "auth-surface": 3,
    "call-edges": 3,
    "execution-slices": 3,
    "data-touches": 2,
    "models": 2,
    "events": 1,
    "jobs": 1,
    "config": 1,
    "import-graph": 1,
    "concepts": 1,
}

LOW_SIGNAL_PATH_SEGMENTS = {
    "docs",
    "doc",
    "tests",
    "test",
    "__tests__",
    "__mocks__",
    "fixtures",
    "fixture",
    "examples",
    "example",
    ".github",
    "vendor",
    "third_party",
    "node_modules",
    ".generated",
}

SUPPORT_PATH_SEGMENTS = {
    "audit",
    "benchmark",
    "benchmarks",
    "notes",
    "schema",
    "schemas",
}

SUPPORT_PATH_SUFFIXES = (
    ("detectors", "scripts"),
    ("skills", "analyze", "scripts"),
    ("scripts", "benchmark"),
)


def _path_parts_lower(path: Path) -> tuple[str, ...]:
    return tuple(part.lower() for part in path.parts)


def _is_excluded_hotfile_candidate(candidate: Path) -> bool:
    parts = _path_parts_lower(candidate)
    return any(part in EXCLUDE_DIRS for part in parts)


def _is_support_hotfile_candidate(candidate: Path) -> bool:
    parts = _path_parts_lower(candidate)
    if set(parts) & SUPPORT_PATH_SEGMENTS:
        return True
    return any(parts[-len(suffix):] == suffix for suffix in SUPPORT_PATH_SUFFIXES if len(parts) >= len(suffix))


def file_hotness_scores(facts: list[dict[str, Any]], root: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    domain_coverage: dict[str, set[str]] = defaultdict(set)

    for fact in facts:
        domain = str(fact.get("domain") or "").strip()
        weight = HOT_FILE_DOMAIN_WEIGHTS.get(domain, 0)
        if weight <= 0:
            continue
        for source in fact.get("source_files", []):
            candidate = source.split(":", 1)[0]
            if not candidate:
                continue
            candidate_path = Path(candidate)
            if _is_excluded_hotfile_candidate(candidate_path):
                continue
            if candidate_path.is_absolute():
                if root not in candidate_path.parents:
                    continue
                candidate_path = candidate_path.relative_to(root)
            if _is_excluded_hotfile_candidate(candidate_path):
                continue
            resolved = (root / candidate_path).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                continue
            if not resolved.is_file():
                continue
            rel = str(candidate_path)
            counts[rel] += weight
            domain_coverage.setdefault(rel, set()).add(domain)

    for rel, covered_domains in domain_coverage.items():
        counts[rel] += max(0, len(covered_domains) - 1)
        parts = {part.lower() for part in Path(rel).parts}
        if parts & LOW_SIGNAL_PATH_SEGMENTS and not (covered_domains & {"frameworks", "boundaries", "dispatch-bindings", "routes", "handlers", "call-edges", "execution-slices"}):
            counts[rel] = max(0, counts[rel] - 4)
        if _is_support_hotfile_candidate(Path(rel)) and not (covered_domains & {"frameworks", "boundaries", "dispatch-bindings", "routes", "handlers", "registrations", "call-edges", "execution-slices", "startup"}):
            counts[rel] = max(0, counts[rel] - 10)

    return counts


def build_facts_payload(root: Path, analysis_mode: str = "full") -> dict[str, Any]:
    files = iter_project_files(root)
    repo_profile = load_repo_profile(root)
    frameworks = detect_frameworks(files, root)
    facts: list[dict[str, Any]] = []
    detectors_run: list[dict[str, Any]] = []
    framework_context = sorted(frameworks)

    for framework_name, fact in frameworks.items():
        facts.append(
            {
                **fact,
                "framework_context": [framework_name],
            }
        )
        detectors_run.append(
            {
                "id": f"{framework_name}-framework-detector",
                "domain": "frameworks",
                "class": fact["detector"]["class"],
                "framework_context": [framework_name],
                "status": "success",
            }
        )

    for path in files:
        text = read_text(path)
        if text is None:
            continue
        suffix = path.suffix.lower()
        if suffix == ".py":
            facts.extend(parse_python_file(path, root, text))
            detectors_run.extend(
                [
                    {
                        "id": "python-route-detector",
                        "domain": "routes",
                        "class": "ast",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "python-model-detector",
                        "domain": "models",
                        "class": "ast",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "python-client-detector",
                        "domain": "external-clients",
                        "class": "signature",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "python-import-graph",
                        "domain": "import-graph",
                        "class": "ast",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "python-middleware-detector",
                        "domain": "middleware",
                        "class": "ast",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "python-auth-detector",
                        "domain": "auth-surface",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "python-config-detector",
                        "domain": "config",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "python-job-detector",
                        "domain": "jobs",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "python-event-detector",
                        "domain": "events",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                ]
            )
        elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
            facts.extend(parse_js_ts_file(path, root, text))
            detectors_run.extend(
                [
                    {
                        "id": "js-route-detector",
                        "domain": "routes",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "js-client-detector",
                        "domain": "external-clients",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "js-import-graph",
                        "domain": "import-graph",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "js-middleware-detector",
                        "domain": "middleware",
                        "class": "ast",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "js-model-detector",
                        "domain": "models",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "js-auth-detector",
                        "domain": "auth-surface",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "js-config-detector",
                        "domain": "config",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "js-job-detector",
                        "domain": "jobs",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                    {
                        "id": "js-event-detector",
                        "domain": "events",
                        "class": "regex",
                        "framework_context": [],
                        "status": "success",
                    },
                ]
            )
        elif suffix == ".prisma":
            facts.extend(parse_prisma_file(path, root, text))
            detectors_run.append(
                {
                    "id": "prisma-model-detector",
                    "domain": "models",
                    "class": "regex",
                    "framework_context": [],
                    "status": "success",
                }
            )
        elif suffix == ".sql":
            facts.extend(parse_sql_file(path, root, text))
            detectors_run.append(
                {
                    "id": "sql-model-detector",
                    "domain": "models",
                    "class": "regex",
                    "framework_context": [],
                    "status": "success",
                }
            )
        elif suffix == ".go":
            facts.extend(parse_go_file(path, root, text))
            detectors_run.extend(
                [
                    {"id": "go-route-detector", "domain": "routes", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "go-gorm-model-detector", "domain": "models", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "go-registration-detector", "domain": "registrations", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "go-handler-detector", "domain": "handlers", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "go-dispatch-detector", "domain": "dispatch-bindings", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "go-boundary-detector", "domain": "boundaries", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "go-config-detector", "domain": "config", "class": "regex", "framework_context": [], "status": "success"},
                    {"id": "go-job-detector", "domain": "jobs", "class": "regex", "framework_context": [], "status": "success"},
                    {"id": "go-event-detector", "domain": "events", "class": "regex", "framework_context": [], "status": "success"},
                ]
            )
        elif suffix == ".cs":
            facts.extend(parse_csharp_file(path, root, text))
            detectors_run.extend(
                [
                    {"id": "csharp-route-detector", "domain": "routes", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "csharp-ef-model-detector", "domain": "models", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "csharp-registration-detector", "domain": "registrations", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "csharp-handler-detector", "domain": "handlers", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "csharp-dispatch-detector", "domain": "dispatch-bindings", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "csharp-boundary-detector", "domain": "boundaries", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "csharp-config-detector", "domain": "config", "class": "regex", "framework_context": [], "status": "success"},
                    {"id": "csharp-job-detector", "domain": "jobs", "class": "regex", "framework_context": [], "status": "success"},
                    {"id": "csharp-event-detector", "domain": "events", "class": "regex", "framework_context": [], "status": "success"},
                ]
            )
        elif suffix in {".java", ".kt", ".kts"}:
            facts.extend(parse_java_kotlin_file(path, root, text))
            detectors_run.extend(
                [
                    {"id": "java-kotlin-route-detector", "domain": "routes", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "java-kotlin-model-detector", "domain": "models", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "java-kotlin-registration-detector", "domain": "registrations", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "java-kotlin-handler-detector", "domain": "handlers", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "java-kotlin-dispatch-detector", "domain": "dispatch-bindings", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "java-kotlin-boundary-detector", "domain": "boundaries", "class": "structured", "framework_context": [], "status": "success"},
                    {"id": "java-kotlin-config-detector", "domain": "config", "class": "regex", "framework_context": [], "status": "success"},
                    {"id": "java-kotlin-job-detector", "domain": "jobs", "class": "regex", "framework_context": [], "status": "success"},
                    {"id": "java-kotlin-event-detector", "domain": "events", "class": "regex", "framework_context": [], "status": "success"},
                    {"id": "plugin-registration-detector", "domain": "registrations", "class": "signature", "framework_context": [], "status": "success"},
                    {"id": "plugin-dispatch-detector", "domain": "dispatch-bindings", "class": "signature", "framework_context": [], "status": "success"},
                    {"id": "plugin-boundary-detector", "domain": "boundaries", "class": "signature", "framework_context": [], "status": "success"},
                ]
            )
        elif suffix in {".cpp", ".cc", ".cxx", ".h", ".hpp"}:
            facts.extend(parse_generic_source_file(path, root, text))
            detectors_run.extend(
                [
                    {"id": "generic-registration-detector", "domain": "registrations", "class": "signature", "framework_context": [], "status": "success"},
                    {"id": "generic-handler-detector", "domain": "handlers", "class": "signature", "framework_context": [], "status": "success"},
                    {"id": "generic-dispatch-detector", "domain": "dispatch-bindings", "class": "signature", "framework_context": [], "status": "success"},
                    {"id": "generic-boundary-detector", "domain": "boundaries", "class": "signature", "framework_context": [], "status": "success"},
                    {"id": "generic-config-detector", "domain": "config", "class": "regex", "framework_context": [], "status": "success"},
                    {"id": "generic-job-detector", "domain": "jobs", "class": "regex", "framework_context": [], "status": "success"},
                    {"id": "generic-event-detector", "domain": "events", "class": "regex", "framework_context": [], "status": "success"},
                ]
            )

    joern_call_edges, joern_detector_run = extract_joern_call_edge_facts(root, repo_profile)
    if joern_call_edges:
        facts.extend(joern_call_edges)
    detectors_run.append(joern_detector_run)

    joern_data_touches, joern_data_touch_detector_run = extract_joern_data_touch_facts(root, repo_profile)
    if joern_data_touches:
        facts.extend(joern_data_touches)
    detectors_run.append(joern_data_touch_detector_run)

    joern_execution_slices, joern_execution_slice_detector_run = extract_joern_execution_slice_facts(root, repo_profile)
    if joern_execution_slices:
        facts.extend(joern_execution_slices)
    detectors_run.append(joern_execution_slice_detector_run)

    state_access_summary_facts, state_access_summary_detector_run = derive_joern_state_access_summary_facts(joern_data_touches)
    if state_access_summary_facts:
        facts.extend(state_access_summary_facts)
    detectors_run.append(state_access_summary_detector_run)

    control_hotspot_facts, control_hotspot_detector_run = derive_joern_control_hotspot_facts(joern_execution_slices)
    if control_hotspot_facts:
        facts.extend(control_hotspot_facts)
    detectors_run.append(control_hotspot_detector_run)

    hot_scores = file_hotness_scores(facts, root)
    hot_files: list[dict[str, Any]] = []
    for file_path, score in hot_scores.most_common(10):
        if score < 3:
            break
        rel = str(Path(file_path).relative_to(root)) if Path(file_path).is_absolute() and root in Path(file_path).parents else file_path
        hot_files.append(
            {
                "id": stable_id("hot-file", rel, str(score)),
                "kind": "hot-file",
                "domain": "hot-files",
                "summary": f"{rel} participates in {score} weighted architecture signals",
                "confidence": "medium" if score < 6 else "high",
                "framework_context": [],
                "source_files": [rel],
                "detector": {
                    "id": "hot-file-ranker",
                    "class": "inference",
                    "strength": 4,
                    "rule": "weighted-centrality",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "file": rel,
                    "score": score,
                    "fan_in": score,
                    "fan_out": 0,
                },
                "negative_evidence": [],
                "contradictions": [],
                "relationships": {
                    "component_ids": infer_component_ids(rel),
                    "depends_on_fact_ids": [],
                    "related_fact_ids": [],
                },
            }
        )

    if hot_files:
        facts.extend(hot_files)
        detectors_run.append(
            {
                "id": "hot-file-ranker",
                "domain": "hot-files",
                "class": "inference",
                "framework_context": [],
                "status": "success",
            }
        )

    for fact in facts:
        if fact.get("kind") != "framework" and not fact.get("framework_context"):
            fact["framework_context"] = framework_context
        if fact.get("kind") != "framework":
            raw_evidence = fact.get("raw_evidence")
            if isinstance(raw_evidence, dict) and framework_context and "framework_context" not in raw_evidence:
                raw_evidence["framework_context"] = framework_context

    domains: dict[str, list[dict[str, Any]]] = defaultdict(list)
    normalized_facts = [normalize_fact_record(fact) for fact in facts]
    for fact in normalized_facts:
        domains[fact["domain"]].append(fact)

    index_domains = [
        {
            "name": domain,
            "file": f"facts/{domain}.json",
            "count": len(items),
        }
        for domain, items in sorted(domains.items())
    ]

    return {
        "version": "1",
        "generated": _today(),
        "project": root.name,
        "analysis_mode": analysis_mode,
        "root": str(root),
        "index": {
            "domains": index_domains,
            "detectors_run": _dedupe_detector_runs(detectors_run),
        },
        "facts": _dedupe_facts(normalized_facts),
        "metadata": {
            "analyzed_at_sha": get_git_sha(root),
            "execution_plan_version": 1,
            "repo_profile": repo_profile,
            "bundle_versions": {
                "frameworks": "1",
                "facts": "1",
                "concepts": "1",
            },
        },
    }


def _today() -> str:
    from datetime import date

    return date.today().isoformat()


def _dedupe_facts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for fact in facts:
        fact_id = fact.get("id")
        if not fact_id:
            fact_id = stable_id(
                "fact",
                str((fact_payload(fact) or {}).get("kind") or ""),
                fact.get("domain", ""),
                json.dumps(fact_payload(fact), sort_keys=True, default=str),
            )
            fact["id"] = fact_id
        if fact_id in seen:
            continue
        seen.add(fact_id)
        deduped.append(fact)
    return deduped


def _dedupe_detector_runs(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    deduped: list[dict[str, Any]] = []
    for run in runs:
        key = (
            run.get("id"),
            run.get("domain"),
            run.get("class"),
            tuple(run.get("framework_context", [])),
            run.get("status"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(run)
    return deduped

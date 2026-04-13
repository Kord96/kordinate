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

from facts import (
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
    line_number_for_offset,
)


MAX_FILE_BYTES = 100 * 1024
ROOT = Path(__file__).resolve().parents[1]
FACT_DETECTORS = ROOT / "detectors" / "facts"
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

FRAMEWORK_PATTERNS = [
    (
        "fastapi",
        [
            r"from\s+fastapi\s+import",
            r"import\s+fastapi",
            r"\bFastAPI\s*\(",
            r"\bAPIRouter\s*\(",
            r"@\w+\.(get|post|put|delete|patch|options|head)\s*\(",
        ],
    ),
    (
        "flask",
        [
            r"from\s+flask\s+import",
            r"import\s+flask",
            r"\bFlask\s*\(",
            r"@\w+\.route\s*\(",
        ],
    ),
    (
        "express",
        [
            r"require\(['\"]express['\"]\)",
            r"import\s+express\b",
            r"\bexpress\s*\(",
            r"\bapp\.(get|post|put|delete|patch|use)\s*\(",
            r"\brouter\.(get|post|put|delete|patch|use)\s*\(",
        ],
    ),
    (
        "koa",
        [
            r"require\(['\"]koa['\"]\)",
            r"import\s+Koa\b",
            r"\bnew\s+Koa\s*\(",
            r"\brouter\.(get|post|put|delete|patch|use)\s*\(",
        ],
    ),
    (
        "fastify",
        [
            r"require\(['\"]fastify['\"]\)",
            r"import\s+fastify\b",
            r"\bfastify\s*\(",
            r"\bfastify\.(get|post|put|delete|patch|route)\s*\(",
        ],
    ),
    (
        "nestjs",
        [
            r"@Controller\b",
            r"@Get\s*\(",
            r"@Post\s*\(",
            r"@Put\s*\(",
            r"@Delete\s*\(",
            r"@Patch\s*\(",
        ],
    ),
    (
        "nextjs",
        [
            r"(^|/)(app|pages)/api/",
            r"export\s+(async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH)\b",
            r"export\s+\{\s*(GET|POST|PUT|DELETE|PATCH)\s*\}",
        ],
    ),
    (
        "sveltekit",
        [
            r"(^|/)src/routes/",
            r"\+server\.(ts|js|mjs|cjs)$",
            r"export\s+(async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH)\b",
        ],
    ),
    (
        "django",
        [
            r"from\s+django\.urls\s+import",
            r"urlpatterns\s*=",
            r"from\s+django\s+import",
            r"django\.setup\s*\(",
        ],
    ),
    (
        "gin",
        [
            r"gin\.Default\s*\(",
            r"gin\.New\s*\(",
            r"\brouter\.(GET|POST|PUT|DELETE|PATCH)\s*\(",
        ],
    ),
    (
        "chi",
        [
            r"chi\.NewRouter\s*\(",
            r"\br\.(Get|Post|Put|Delete|Patch)\s*\(",
        ],
    ),
    (
        "spring",
        [
            r"@RestController\b",
            r"@SpringBootApplication\b",
            r"@GetMapping\s*\(",
            r"@PostMapping\s*\(",
            r"@RequestMapping\s*\(",
        ],
    ),
    (
        "rails",
        [
            r"Rails\.application\.routes\.draw\b",
            r"^\s*resources\s+:\w+",
            r"^\s*namespace\s+:\w+",
            r"^\s*scope\s+['\"]/",
        ],
    ),
]

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


def parse_manifest_frameworks(root: Path) -> dict[str, list[str]]:
    frameworks: dict[str, list[str]] = defaultdict(list)

    def add(name: str, evidence: str) -> None:
        frameworks[name].append(evidence)

    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        for section in ("dependencies", "devDependencies", "peerDependencies"):
            deps = data.get(section, {}) if isinstance(data, dict) else {}
            if not isinstance(deps, dict):
                continue
            for dep in deps:
                lower = dep.lower()
                if lower == "fastapi":
                    add("fastapi", f"package.json:{section}")
                if lower == "express":
                    add("express", f"package.json:{section}")
                if lower == "koa":
                    add("koa", f"package.json:{section}")
                if lower == "fastify":
                    add("fastify", f"package.json:{section}")
                if lower.startswith("@nestjs/") or lower == "nestjs":
                    add("nestj", f"package.json:{section}")
                if lower == "next":
                    add("nextjs", f"package.json:{section}")
                if lower == "sveltekit":
                    add("sveltekit", f"package.json:{section}")
                if lower == "hono":
                    add("hono", f"package.json:{section}")
                if lower == "elysia":
                    add("elysia", f"package.json:{section}")
        if "scripts" in data and isinstance(data["scripts"], dict):
            scripts = " ".join(str(v) for v in data["scripts"].values())
            if "next" in scripts:
                add("nextjs", "package.json:scripts")

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        text = read_text(pyproject) or ""
        if re.search(r"\bfastapi\b", text, re.I):
            add("fastapi", "pyproject.toml")
        if re.search(r"\bflask\b", text, re.I):
            add("flask", "pyproject.toml")
        if re.search(r"\bdjango\b", text, re.I):
            add("django", "pyproject.toml")
        if re.search(r"\baiohttp\b", text, re.I):
            add("aiohttp", "pyproject.toml")

    requirements = root / "requirements.txt"
    if requirements.exists():
        text = read_text(requirements) or ""
        for name in ("fastapi", "flask", "django", "starlette", "aiohttp"):
            if re.search(rf"^\s*{re.escape(name)}(?:[<>=!~].*)?$", text, re.M | re.I):
                add(name, "requirements.txt")

    gemfile = root / "Gemfile"
    if gemfile.exists():
        text = read_text(gemfile) or ""
        if re.search(r"\brails\b", text, re.I):
            add("rails", "Gemfile")
        if re.search(r"\bsinatra\b", text, re.I):
            add("sinatra", "Gemfile")

    composer = root / "composer.json"
    if composer.exists():
        try:
            data = json.loads(composer.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        for section in ("require", "require-dev"):
            deps = data.get(section, {}) if isinstance(data, dict) else {}
            if not isinstance(deps, dict):
                continue
            for dep in deps:
                if "laravel/framework" in dep:
                    add("laravel", "composer.json")
                if "symfony/framework-bundle" in dep:
                    add("symfony", "composer.json")
                if "slim/slim" in dep:
                    add("slim", "composer.json")

    cargo = root / "Cargo.toml"
    if cargo.exists():
        text = read_text(cargo) or ""
        if re.search(r"\baxum\b", text, re.I):
            add("axum", "Cargo.toml")
        if re.search(r"\bactix_web\b", text, re.I):
            add("actix-web", "Cargo.toml")

    pom = root / "pom.xml"
    if pom.exists():
        text = read_text(pom) or ""
        if re.search(r"\bspring-boot\b|\bspringframework\b", text, re.I):
            add("spring", "pom.xml")
        if re.search(r"\bquarkus\b", text, re.I):
            add("quarkus", "pom.xml")

    go_mod = root / "go.mod"
    if go_mod.exists():
        text = read_text(go_mod) or ""
        if "github.com/gin-gonic/gin" in text:
            add("gin", "go.mod")
        if "github.com/go-chi/chi" in text:
            add("chi", "go.mod")
        if "github.com/labstack/echo" in text:
            add("echo", "go.mod")
        if "github.com/gofiber/fiber" in text:
            add("fiber", "go.mod")

    return frameworks


def detect_frameworks(files: Iterable[Path], root: Path) -> dict[str, dict[str, Any]]:
    evidence: dict[str, list[str]] = defaultdict(list)

    for file in files:
        if not is_framework_signal_file(file, root):
            continue
        text = read_text(file)
        if text is None:
            continue
        if file.suffix.lower() == ".py":
            for framework in detect_python_framework_signals(text):
                evidence[framework].append(f"{file.relative_to(root)}")
            continue
        for framework, patterns in FRAMEWORK_PATTERNS:
            if any(re.search(pattern, text, re.M) for pattern in patterns):
                evidence[framework].append(f"{file.relative_to(root)}")

    manifest_evidence = parse_manifest_frameworks(root)
    for name, sources in manifest_evidence.items():
        evidence[name].extend(sources)

    result: dict[str, dict[str, Any]] = {}
    for name in sorted(evidence):
        sources = sorted(set(evidence[name]))
        manifest_like = any(src.endswith(("package.json", "go.mod", "Cargo.toml", "pom.xml", "Gemfile", "composer.json", "pyproject.toml", "requirements.txt")) for src in sources)
        confidence = "high" if manifest_like or len(sources) >= 2 else "medium"
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
                "class": "manifest" if any(src.endswith(("package.json", "go.mod", "Cargo.toml", "pom.xml", "Gemfile", "composer.json")) for src in sources) else "signature",
                "strength": 5 if confidence == "high" else 3,
                "rule": None,
                "bundle": "detectors:frameworks",
            },
            "raw_evidence": {
                "framework": name,
                "signals": sources,
                "negative_signals": [],
            },
            "negative_evidence": [],
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
    if path.suffix.lower() in {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".scala", ".rb", ".php", ".cs", ".swift", ".dart", ".ex", ".exs"}:
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


def detect_python_framework_signals(text: str) -> set[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()

    frameworks: set[str] = set()
    imported_modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module:
                imported_modules.add(module)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for deco in node.decorator_list:
                if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute):
                    if deco.func.attr.lower() in {"get", "post", "put", "delete", "patch", "route"}:
                        frameworks.add("fastapi")
                elif isinstance(deco, ast.Attribute) and deco.attr.lower() in {"get", "post", "put", "delete", "patch", "route"}:
                    frameworks.add("fastapi")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "FastAPI":
                frameworks.add("fastapi")
            elif node.func.id == "Flask":
                frameworks.add("flask")

    imported_text = " ".join(sorted(imported_modules)).lower()
    if "fastapi" in imported_text:
        frameworks.add("fastapi")
    if "flask" in imported_text:
        frameworks.add("flask")
    if "django" in imported_text:
        frameworks.add("django")
    if "starlette" in imported_text:
        frameworks.add("starlette")
    if "aiohttp" in imported_text:
        frameworks.add("aiohttp")
    return frameworks


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


def file_hotness_scores(facts: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for fact in facts:
        for source in fact.get("source_files", []):
            counts[source.split(":", 1)[0]] += 1
        for component_id in fact.get("relationships", {}).get("component_ids", []):
            counts[component_id] += 1
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

    hot_scores = file_hotness_scores(facts)
    hot_files: list[dict[str, Any]] = []
    for file_path, score in hot_scores.most_common(10):
        if score < 2:
            break
        rel = str(Path(file_path).relative_to(root)) if Path(file_path).is_absolute() and root in Path(file_path).parents else file_path
        hot_files.append(
            {
                "id": stable_id("hot-file", rel, str(score)),
                "kind": "hot-file",
                "domain": "hot-files",
                "summary": f"{rel} participates in {score} extracted facts",
                "confidence": "medium" if score < 4 else "high",
                "framework_context": [],
                "source_files": [rel],
                "detector": {
                    "id": "hot-file-ranker",
                    "class": "inference",
                    "strength": 3,
                    "rule": "fan-in",
                    "bundle": "detectors:facts",
                },
                "raw_evidence": {
                    "file": rel,
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

    for fact in facts:
        if fact.get("kind") != "framework" and not fact.get("framework_context"):
            fact["framework_context"] = framework_context

    domains: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in facts:
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
        "facts": _dedupe_facts(facts),
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
                fact.get("kind", ""),
                fact.get("domain", ""),
                json.dumps(fact.get("raw_evidence", {}), sort_keys=True, default=str),
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

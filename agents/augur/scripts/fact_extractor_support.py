#!/usr/bin/env python3
"""Shared support for deterministic fact extraction.

The extractor is intentionally pragmatic:
- prefer manifests and AST for Python
- use regex heuristics for JS/TS and other common source files
- normalize raw matches into schema-shaped fact objects
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


MAX_FILE_BYTES = 100 * 1024

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
                "bundle": "bundles/detectors/frameworks/all.json",
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


def extract_auth_surfaces(text: str, suffix: str) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    patterns = [
        ("oauth-oidc", r"\boauth\b|\boidc\b|\bopenid\b"),
        ("jwt", r"\bjwt\b|\bbearer\b"),
        ("session-auth", r"\bsession\b|\bcookie\b"),
        ("api-key-auth", r"x-api-key|api[_-]?key"),
        ("rbac", r"\brbac\b|\brole\b|\bpermission\b"),
        ("route-guard", r"\bguard\b|\bauthorize\b|\brequireAuth\b|@UseGuards\b"),
    ]
    lowered = text.lower()
    for kind, pattern in patterns:
        if re.search(pattern, lowered, re.I):
            surfaces.append({"technology": kind, "auth": kind})
    return surfaces


def extract_config_sources(text: str, suffix: str) -> list[dict[str, Any]]:
    configs: list[dict[str, Any]] = []
    patterns = [
        ("env", r"process\.env|os\.environ|getenv\(|environ\["),
        ("dotenv", r"\bdotenv\b|load_dotenv"),
        ("yaml", r"\.ya?ml\b|safe_load\(|yaml\."),
        ("json", r"\.json\b|json\.load"),
        ("service-url", r"https?://[^\s\"'`>]+|[A-Z0-9_]+_URL\b"),
        ("secret", r"\bsecret\b|\btoken\b|\bpassword\b|\bapi[_-]?key\b"),
    ]
    lowered = text.lower()
    for source_type, pattern in patterns:
        if re.search(pattern, text if "URL" in pattern else lowered, re.I):
            configs.append({"source_type": source_type})
    return configs


def extract_jobs(text: str, suffix: str) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    patterns = [
        ("scheduler", r"\bcron\b|\bcrontab\b|\bschedule\b|\bapscheduler\b"),
        ("worker", r"\bworker\b|\bconsumer\b|\bcelery\b|\bbullmq\b|\bqueue\.process\b"),
        ("background-task", r"create_task\(|setInterval\(|BackgroundTasks\b"),
    ]
    lowered = text.lower()
    for job_type, pattern in patterns:
        if re.search(pattern, lowered, re.I):
            jobs.append({"job_type": job_type})
    return jobs


def extract_events(text: str, suffix: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    patterns = [
        ("publish", r"\bpublish\(|\bemit\(|producer\.send|kafka\.producer"),
        ("consume", r"\bconsume\(|\bon\(['\"]message|consumer\.run|kafka\.consumer"),
        ("webhook", r"\bwebhook\b"),
    ]
    lowered = text.lower()
    for event_type, pattern in patterns:
        if re.search(pattern, lowered, re.I):
            events.append({"event_type": event_type})
    return events


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
                    "bundle": "bundles/detectors/facts/all.json",
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

    routes = extract_python_routes(text)
    for idx, route in enumerate(routes, start=1):
        path_value = route["path"] or ""
        method = route["method"]
        handler = route["handler"]
        fact_id = stable_id("route", rel, str(idx), method, path_value, handler)
        facts.append(
            {
                "id": fact_id,
                "kind": "route",
                "domain": "routes",
                "summary": f"{method} {path_value or '(unresolved path)'} handled by {handler}",
                "confidence": "high" if path_value else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{idx}"],
                "detector": {
                    "id": "python-route-detector",
                    "class": "ast",
                    "strength": 5,
                    "rule": f"route-{method.lower()}",
                    "bundle": "bundles/detectors/facts/all.json",
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

    models = extract_models(text, path)
    for idx, model in enumerate(models, start=1):
        fact_id = stable_id("model", rel, model["name"], str(idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "model",
                "domain": "models",
                "summary": f"Detected {model['source']} model {model['name']}",
                "confidence": "high" if model["fields"] else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{idx}"],
                "detector": {
                    "id": f"python-{model['source']}-model-detector",
                    "class": "ast",
                    "strength": 5,
                    "rule": model["source"],
                    "bundle": "bundles/detectors/facts/all.json",
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

    for idx, client in enumerate(client_matches, start=1):
        fact_id = stable_id("client", rel, client["kind"], client["technology"], str(idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "external-client",
                "domain": "external-clients",
                "summary": f"Detected {client['kind']} client via {client['technology']}",
                "confidence": "high" if client["source"] == "import" else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "python-client-detector",
                    "class": "signature" if client["source"] == "import" else "regex",
                    "strength": 4,
                    "rule": client["technology"],
                    "bundle": "bundles/detectors/facts/all.json",
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

    for idx, surface in enumerate(extract_auth_surfaces(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("auth", rel, surface["technology"], str(idx)),
                "kind": "auth-surface",
                "domain": "auth-surface",
                "summary": f"Detected auth surface {surface['technology']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "python-auth-detector",
                    "class": "regex",
                    "strength": 3,
                    "rule": surface["technology"],
                    "bundle": "bundles/detectors/facts/all.json",
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
                    "bundle": "bundles/detectors/facts/all.json",
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
                    "bundle": "bundles/detectors/facts/all.json",
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
                    "bundle": "bundles/detectors/facts/all.json",
                },
                "raw_evidence": event,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

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
                    "bundle": "bundles/detectors/facts/all.json",
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

    routes = extract_js_routes(text)
    for idx, route in enumerate(routes, start=1):
        fact_id = stable_id("route", rel, str(idx), route["method"], route["path"], route["handler"])
        facts.append(
            {
                "id": fact_id,
                "kind": "route",
                "domain": "routes",
                "summary": f"{route['method']} {route['path'] or '(file route)'} handled by {route['handler']}",
                "confidence": "high" if route["path"] else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{idx}"],
                "detector": {
                    "id": "js-route-detector",
                    "class": "regex",
                    "strength": 4,
                    "rule": route["decorator"],
                    "bundle": "bundles/detectors/facts/all.json",
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

    models = extract_models(text, path)
    for idx, model in enumerate(models, start=1):
        fact_id = stable_id("model", rel, model["name"], str(idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "model",
                "domain": "models",
                "summary": f"Detected {model['source']} model {model['name']}",
                "confidence": "high" if model["fields"] else "medium",
                "framework_context": [],
                "source_files": [f"{rel}:{idx}"],
                "detector": {
                    "id": f"js-{model['source']}-model-detector",
                    "class": "regex",
                    "strength": 4,
                    "rule": model["source"],
                    "bundle": "bundles/detectors/facts/all.json",
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

    for idx, client in enumerate(extract_js_clients(text), start=1):
        fact_id = stable_id("client", rel, client["kind"], client["technology"], str(idx))
        facts.append(
            {
                "id": fact_id,
                "kind": "external-client",
                "domain": "external-clients",
                "summary": f"Detected {client['kind']} client via {client['technology']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "js-client-detector",
                    "class": "regex",
                    "strength": 4,
                    "rule": client["technology"],
                    "bundle": "bundles/detectors/facts/all.json",
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

    for idx, surface in enumerate(extract_auth_surfaces(text, path.suffix.lower()), start=1):
        facts.append(
            {
                "id": stable_id("auth", rel, surface["technology"], str(idx)),
                "kind": "auth-surface",
                "domain": "auth-surface",
                "summary": f"Detected auth surface {surface['technology']}",
                "confidence": "medium",
                "framework_context": [],
                "source_files": [f"{rel}:1"],
                "detector": {
                    "id": "js-auth-detector",
                    "class": "regex",
                    "strength": 3,
                    "rule": surface["technology"],
                    "bundle": "bundles/detectors/facts/all.json",
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
                    "bundle": "bundles/detectors/facts/all.json",
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
                    "bundle": "bundles/detectors/facts/all.json",
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
                    "bundle": "bundles/detectors/facts/all.json",
                },
                "raw_evidence": event,
                "negative_evidence": [],
                "contradictions": [],
                "relationships": relationships,
            }
        )

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
                    "bundle": "bundles/detectors/facts/all.json",
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
                    "bundle": "bundles/detectors/facts/all.json",
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
                    "bundle": "bundles/detectors/facts/all.json",
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

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    ".turbo",
    ".venv",
    "venv",
    "__pycache__",
    ".gradle",
    ".idea",
    ".vscode",
    "coverage",
}

MARKER_RULES = [
    ("go", ["go.mod"]),
    ("javascript", ["package.json", "tsconfig.json", "tsconfig.web.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json"]),
    ("java", ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts", "gradlew"]),
    ("python", ["pyproject.toml", "requirements.txt", "requirements-dev.txt", "setup.py", "Pipfile", "poetry.lock"]),
    ("csharp", ["*.csproj", "*.sln"]),
    ("swift", ["Package.swift"]),
    ("php", ["composer.json"]),
    ("ruby", ["Gemfile"]),
    ("kotlin", ["*.kts"]),
]

EXTENSION_RULES = {
    ".go": "go",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".java": "java",
    ".py": "python",
    ".cs": "csharp",
    ".swift": "swift",
    ".php": "php",
    ".rb": "ruby",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".rs": "rust",
}


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def scan_markers(root: Path) -> Counter[str]:
    hits: Counter[str] = Counter()
    for language, patterns in MARKER_RULES:
        for pattern in patterns:
            matched = list(root.glob(pattern))
            if matched:
                hits[language] += 5 * len(matched)
    return hits


def scan_extensions(root: Path, limit: int = 10000) -> Counter[str]:
    hits: Counter[str] = Counter()
    scanned = 0
    for path in root.rglob("*"):
        if scanned >= limit:
            break
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        scanned += 1
        language = EXTENSION_RULES.get(path.suffix.lower())
        if language:
            hits[language] += 1
    return hits


def detect_frameworks(root: Path) -> list[str]:
    found: set[str] = set()
    package_json = root / "package.json"
    if package_json.exists():
        text = _safe_read(package_json).lower()
        for dep, fw in {
            '"express"': "express",
            '"fastify"': "fastify",
            '"koa"': "koa",
            '"next"': "nextjs",
            '"hono"': "hono",
            '"elysia"': "elysia",
        }.items():
            if dep in text:
                found.add(fw)
        if "@nestjs/" in text or '"nestjs"' in text:
            found.add("nestjs")

    pyproject = root / "pyproject.toml"
    requirements = root / "requirements.txt"
    py_text = (_safe_read(pyproject) + "\n" + _safe_read(requirements)).lower()
    for dep, fw in {
        "fastapi": "fastapi",
        "flask": "flask",
        "django": "django",
        "aiohttp": "aiohttp",
    }.items():
        if dep in py_text:
            found.add(fw)

    go_mod = root / "go.mod"
    go_text = _safe_read(go_mod)
    for dep, fw in {
        "github.com/gin-gonic/gin": "gin",
        "github.com/go-chi/chi": "chi",
        "github.com/labstack/echo": "echo",
        "github.com/gofiber/fiber": "fiber",
    }.items():
        if dep in go_text:
            found.add(fw)

    pom = root / "pom.xml"
    gradle = root / "build.gradle"
    gradle_kts = root / "build.gradle.kts"
    jvm_text = "\n".join(_safe_read(p) for p in (pom, gradle, gradle_kts)).lower()
    if re.search(r"\bspring-boot\b|\bspringframework\b", jvm_text):
        found.add("spring")
    if "quarkus" in jvm_text:
        found.add("quarkus")

    composer = root / "composer.json"
    php_text = _safe_read(composer).lower()
    if "laravel/framework" in php_text:
        found.add("laravel")
    if "symfony/framework-bundle" in php_text:
        found.add("symfony")

    gemfile = root / "Gemfile"
    ruby_text = _safe_read(gemfile).lower()
    if "rails" in ruby_text:
        found.add("rails")
    if "sinatra" in ruby_text:
        found.add("sinatra")

    cargo = root / "Cargo.toml"
    cargo_text = _safe_read(cargo).lower()
    if "axum" in cargo_text:
        found.add("axum")
    if "actix_web" in cargo_text:
        found.add("actix-web")

    return sorted(found)


def detect_build_systems(root: Path) -> list[str]:
    systems: list[str] = []
    marker_map = {
        "go": ["go.mod"],
        "npm": ["package.json", "package-lock.json"],
        "pnpm": ["pnpm-lock.yaml"],
        "yarn": ["yarn.lock"],
        "maven": ["pom.xml"],
        "gradle": ["build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts", "gradlew"],
        "python": ["pyproject.toml", "requirements.txt", "Pipfile", "poetry.lock", "setup.py"],
        "cargo": ["Cargo.toml"],
        "dotnet": ["*.csproj", "*.sln"],
        "composer": ["composer.json"],
        "bundler": ["Gemfile"],
        "swiftpm": ["Package.swift"],
    }
    for system, patterns in marker_map.items():
        for pattern in patterns:
            if list(root.glob(pattern)):
                systems.append(system)
                break
    return systems


def detect_repo_profile(root: Path) -> dict:
    marker_hits = scan_markers(root)
    extension_hits = scan_extensions(root)
    combined = marker_hits + extension_hits
    dominant = combined.most_common(1)[0][0] if combined else None
    secondary = [name for name, _score in combined.most_common()[1:4]]
    return {
        "dominant_language": dominant,
        "secondary_languages": secondary,
        "language_scores": dict(combined.most_common()),
        "frameworks": detect_frameworks(root),
        "build_systems": detect_build_systems(root),
        "repo_kind": "mixed" if len([k for k, v in combined.items() if v > 0]) > 1 else "single-language",
    }


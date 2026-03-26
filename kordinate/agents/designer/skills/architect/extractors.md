# Extractors

Level 3 resource for the architect skill. Defines file collection patterns.

## Include Patterns

Source files to read for analysis:

**Python**: `*.py`
**JavaScript/TypeScript**: `*.js`, `*.jsx`, `*.ts`, `*.tsx`
**Go**: `*.go`
**Rust**: `*.rs`
**Config/Infra**: `Dockerfile`, `docker-compose*.yml`, `*.yaml`, `*.yml` (in deploy/, manifests/, k8s/, kubernetes/, charts/, .github/), `Makefile`
**Documentation**: `README.md`, `README.rst` (top-level only)
**Package manifests**: `package.json`, `pyproject.toml`, `requirements.txt`, `setup.py`, `go.mod`, `Cargo.toml`

## Exclude Patterns

Skip entirely:

**Directories**: `node_modules/`, `vendor/`, `venv/`, `.venv/`, `__pycache__/`, `.git/`, `.github/` (except workflows), `.next/`, `dist/`, `build/`, `.cache/`, `.tmp/`, `site/`, `coverage/`, `.tox/`, `.mypy_cache/`, `.pytest_cache/`

**Files**: `*.min.js`, `*.min.css`, `*.map`, `*.pyc`, `*.pyo`, `*.so`, `*.dll`, `*.class`, `*.lock`, `yarn.lock`, `package-lock.json`, `poetry.lock`, `*.svg`, `*.png`, `*.jpg`, `*.gif`, `*.ico`, `*.woff`, `*.ttf`, `*.eot`

**Content**: Skip files larger than 100KB. Skip generated files (containing "auto-generated", "do not edit" in first 5 lines).

## Test Files

**Include test files** in the collection but tag them. Tests reveal what the system considers important and how components interact. Files matching `test_*`, `*_test.*`, `*.test.*`, `*.spec.*`, `tests/`, `__tests__/` are tagged as test files.

## Priority Order (for large projects)

When a project exceeds 500 source files after filtering, read in this priority:

1. README and package manifests
2. Entry points (`__main__.py`, `app.py`, `main.py`, `index.ts`, `server.ts`, Dockerfile)
3. Route/handler definitions
4. Model/schema definitions
5. Config files
6. K8s manifests
7. Core business logic (files with highest import fan-in, excluding utilities)
8. Tests (sample, not all)
9. Everything else until token budget is reached

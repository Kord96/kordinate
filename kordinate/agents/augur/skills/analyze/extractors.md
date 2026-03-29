# Extractors

Level 3 resource for the architect skill. Referenced from step 2 (gather sources). Defines file collection patterns.

## How to collect

Glob `$ROOT` recursively for include patterns, filtering out exclude patterns. Read matched files into context. For languages not listed here, include `*.<ext>` for the project's primary language(s) detected in step 1.

## Include Patterns

Source files to read for analysis:

**Python**: `*.py`
**JavaScript/TypeScript**: `*.js`, `*.jsx`, `*.ts`, `*.tsx`
**Go**: `*.go`
**Rust**: `*.rs`
**C/C++**: `*.c`, `*.cpp`, `*.h`, `*.hpp`
**JVM**: `*.java`, `*.kt`, `*.scala`
**Zig**: `*.zig`
**Elixir**: `*.ex`, `*.exs`
**Other**: `*.rb`, `*.php`, `*.cs`, `*.swift`, `*.dart`, `*.lua`, `*.hs`, `*.ml`
**Schemas/IDL**: `*.proto`, `*.graphql`, `*.gql`, `*.sql` (in migrations/, schema/, sql/, db/ only)
**Config/Infra**: `Dockerfile`, `docker-compose*.yml`, `*.yaml`, `*.yml` (in deploy/, manifests/, k8s/, kubernetes/, charts/, .github/), `Makefile`, `Justfile`, `Earthfile`, `Taskfile.yml`, `Procfile`, `Tiltfile`, `Caddyfile`, `nginx.conf`
**CI**: `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/config.yml`, `bitbucket-pipelines.yml`, `.travis.yml` (reveal build/deploy architecture)
**Documentation**: `README.md`, `README.rst` (top-level only), `.env.example`, `.env.sample` (structure, not secrets)
**Package manifests**: `package.json`, `pyproject.toml`, `requirements.txt`, `setup.py`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `build.gradle.kts`, `Gemfile`, `composer.json`, `Package.swift`, `mix.exs`, `build.zig.zon`

## Exclude Patterns

Skip entirely:

**Directories**: `node_modules/`, `vendor/`, `venv/`, `.venv/`, `__pycache__/`, `.git/`, `.github/` (except workflows), `.next/`, `dist/`, `build/`, `.cache/`, `.tmp/`, `site/`, `coverage/`, `.tox/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `target/` (Rust/Maven), `bin/`, `obj/` (.NET), `.terraform/`, `.gradle/`, `.cargo/`, `.nx/`, `__snapshots__/`, `.idea/`, `.vscode/`

**Files**: `*.min.js`, `*.min.css`, `*.map`, `*.pyc`, `*.pyo`, `*.so`, `*.dll`, `*.class`, `*.jar`, `*.wasm`, `*.lock`, `yarn.lock`, `package-lock.json`, `poetry.lock`, `Cargo.lock`, `*.svg`, `*.png`, `*.jpg`, `*.gif`, `*.ico`, `*.woff`, `*.woff2`, `*.ttf`, `*.eot`

**Content**: Skip files larger than 100KB. Skip generated files (containing "auto-generated", "do not edit" in first 5 lines).

## Test Files

**Include test files** in the collection but tag them. Tests reveal what the system considers important and how components interact. Files matching `test_*`, `*_test.*`, `*.test.*`, `*.spec.*`, `tests/`, `__tests__/` are tagged as test files.

## Priority Order (for large projects)

When a project exceeds 500 source files after filtering, read in this priority:

1. README and package manifests
2. Entry points (`__main__.py`, `app.py`, `main.py`, `index.ts`, `server.ts`, `Main.java`, `Program.cs`, `main.go`, `main.rs`, `main.zig`, `lib/<app>.ex`, Dockerfile)
3. Background worker entry points (additional `__main__.py` files in subdirectories, `Procfile` entries, `docker-compose` service entrypoints, `celery.py`, `worker.py`, `consumer.py`, `scheduler.py`). These are architecturally distinct processes that may have separate dependency graphs and failure modes.
4. Route/handler definitions
5. Model/schema definitions
6. Config files
7. K8s manifests and docker-compose files (reveal service topology and process count)
8. Core business logic (files with highest import fan-in, excluding utilities)
9. Tests (sample, not all)
10. Everything else until token budget is reached

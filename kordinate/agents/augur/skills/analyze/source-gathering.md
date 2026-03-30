# Source Gathering and Component Identification

Level 3 resource for the analyze skill. Referenced from steps 1 (gather sources) and 5 (identify components and groups). Defines what to collect, how to filter, and how to organize.

---

## Part 1: File Collection

Glob `$ROOT` recursively for include patterns, filtering out exclude patterns. Read matched files into context. For languages not listed here, include `*.<ext>` for the project's primary language(s) detected in step 1.

### Include Patterns

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

### Exclude Patterns

**Directories**: `node_modules/`, `vendor/`, `venv/`, `.venv/`, `__pycache__/`, `.git/`, `.github/` (except workflows), `.next/`, `dist/`, `build/`, `.cache/`, `.tmp/`, `site/`, `coverage/`, `.tox/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `target/` (Rust/Maven), `bin/`, `obj/` (.NET), `.terraform/`, `.gradle/`, `.cargo/`, `.nx/`, `__snapshots__/`, `.idea/`, `.vscode/`

**Files**: `*.min.js`, `*.min.css`, `*.map`, `*.pyc`, `*.pyo`, `*.so`, `*.dll`, `*.class`, `*.jar`, `*.wasm`, `*.lock`, `yarn.lock`, `package-lock.json`, `poetry.lock`, `Cargo.lock`, `*.svg`, `*.png`, `*.jpg`, `*.gif`, `*.ico`, `*.woff`, `*.woff2`, `*.ttf`, `*.eot`

**Content**: Skip files larger than 100KB. Skip generated files (containing "auto-generated", "do not edit" in first 5 lines).

### Test Files

**Include test files** but tag them. Tests reveal what the system considers important and how components interact. Files matching `test_*`, `*_test.*`, `*.test.*`, `*.spec.*`, `tests/`, `__tests__/` are tagged as test files.

### Priority Order (for large projects)

When a project exceeds 500 source files after filtering, read in this priority:

1. README and package manifests
2. Entry points (`__main__.py`, `app.py`, `main.py`, `index.ts`, `server.ts`, `Main.java`, `Program.cs`, `main.go`, `main.rs`, `main.zig`, `lib/<app>.ex`, Dockerfile)
3. Background worker entry points (additional `__main__.py` files in subdirectories, `Procfile` entries, `docker-compose` service entrypoints, `celery.py`, `worker.py`, `consumer.py`, `scheduler.py`)
4. Route/handler definitions
5. Model/schema definitions
6. Config files
7. K8s manifests and docker-compose files (reveal service topology and process count)
8. Core business logic (files with highest import fan-in, excluding utilities)
9. Tests (sample, not all)
10. Everything else until token budget is reached

---

## Part 2: Component Identification

The goal is to surface abstractions that define the system's shape, not every module.

### Filtering Criteria

**Include as top-level components:**
- Entry points (servers, CLI, main) — where actors meet the system
- Business-domain abstractions — the core "what it does"
- Client libraries that wrap external services — if you wrote the code, it's a component

**Move to `external_dependencies`, NOT components:**
- Infrastructure you deploy but didn't write (Kafka, Redis, PostgreSQL, MinIO, Elasticsearch)
- Third-party services you call (OAuth providers, SMTP, payment APIs)
- These go in the atlas `external_dependencies` section with criticality and resilience info
- The **client code** that connects to them (e.g., kafka.py, redis_client.py) belongs in the component that uses it, not as a separate component

**Skip as top-level components:**
- Utilities, logging, config modules — high fan-in plumbing, not structure
- When in doubt, prefer business-domain over infrastructure

### Per-Component Extraction

For each component, capture:
- **id**: kebab-case, unique
- **name**: human-readable (not a module path)
- **type**: one of `service | library | worker | api | frontend | cli | scheduler | store | gateway | broker`
- **description**: one sentence of what it does
- **modules**: source files that implement it
- **abstraction**: levels from `abstractions.md` (e.g., `[data, messaging]`)
- **patterns**: from detection output or concept catalog
- **depends_on**: other component ids (directional)

### Relationship Mapping

`depends_on` captures directional dependencies: if A calls, imports, or consumes from B, then A depends_on B.

- **Yes**: A imports B's module, A calls B's API, A reads from B's store, A consumes B's events
- **No**: both A and B import a shared utility (incidental coupling, not structural)
- **No**: A and B happen to run in the same process (co-location, not dependency)

For richer relationship detail (what flows, transport, direction), use `data_flows` and `events` rather than encoding it in `depends_on`.

### Group Assignment

After identifying components, assign each to exactly one of **3-5 top-level groups**. This is a hard constraint.

Groups are structural clusters — not business capabilities, not deployment units. A group should contain components that share a deployment boundary, data flow path, or architectural concern.

Rules:
- Follow C4 Container model: top-level groups are runtime boundaries (Server, Browser, External), not code modules
- Synthetic `external` and `actors` groups count toward the 3-5 limit
- Small projects (<15 nodes) should aim for 3 groups
- If two groups have only 1-2 nodes each, they belong together
- Each group should have **2-5 components**. If a group has 6+, either split it into two groups or consolidate components. If a group has 1, merge it into another group
- After drafting, count groups. If >5, merge the two most closely related. Repeat until ≤5

Each group informs story composition in Phase 2 — choose groupings that tell a coherent story about the system's shape.

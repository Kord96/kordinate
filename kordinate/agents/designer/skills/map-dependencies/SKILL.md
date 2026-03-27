---
name: map-dependencies
description: "Build a dependency graph -- internal modules, external services, infrastructure, reverse deps. Supports Python, JS/TS, Go."
argument-hint: "<project> [--reverse] [--depth N]"
curated: true
scope: global
---

# map-dependencies

Build a dependency graph for a project -- internal modules, external services, infrastructure resources, and reverse dependencies from sibling projects. Output is consumed by `/architect` to populate `architecture.yaml`.

## Arguments

`$ARGUMENTS` -- Required: `<project>`. Optional: `[--reverse]` to scan sibling projects for inbound references, `[--depth N]` to limit internal module graph depth (default: unlimited).

The project directory must exist at `~/<project>/` or `~/repos/<project>/`.

## Steps

1. Parse project name and flags from `$ARGUMENTS`. If project missing, show usage and exit.

2. Locate the project directory. Check `~/<project>/`, then `~/repos/<project>/`. If not found, report the paths checked and exit.

3. **Detect project language** -- inspect the project root for language markers:
   - **Python**: `pyproject.toml`, `setup.py`, `requirements.txt`, `__init__.py`
   - **JS/TS**: `package.json`, `tsconfig.json`, `.js`/`.ts`/`.tsx` files
   - **Go**: `go.mod`, `go.sum`, `.go` files
   - **Mixed**: multiple indicators -- map each language separately, then merge

   If no recognizable markers, report what was found and exit with a note that the skill supports Python, JS/TS, and Go.

4. **Discover modules and map imports** -- find internal modules and trace their dependencies using the patterns in [patterns.md](patterns.md) (Module Discovery and Import Patterns sections).

   Build a directed graph: `A -> B` means A depends on B. Respect `--depth N` if set -- stop traversal at depth N. Then flag:
   - **Circular dependencies**: report the full cycle path. Cap detection at 5 levels deep -- beyond that, note total depth and move on.
   - **Hub modules**: imported by >50% of other modules. These are coupling hotspots.

5. **Detect external services** -- scan source files for client library usage per [patterns.md](patterns.md) (External Service Detection section). Also check ORM schema files (`prisma/schema.prisma`, `drizzle.config.ts`, `ormconfig.ts`) for declared providers and connection sources. For each service found, record: type (use concept vocabulary from [report-template.md](report-template.md): `database`, `cache`, `message-broker`, etc.), technology (PostgreSQL, Redis, Kafka, etc.), target (from connection strings, env vars, or config if visible), and which files use it.

6. **Scan infrastructure** -- check k8s manifests at `manifests/`, `deploy/`, `k8s/`, `helm/`, `charts/`:
   - PVCs, StatefulSets, ConfigMaps, Secrets, Service endpoints, init containers, sidecars
   - Helm `values.yaml` for service references, resource names, and env injections
   - Terraform/Pulumi files (`.tf`, `Pulumi.yaml`) at `infra/`, `terraform/`, `iac/` for provisioned resources (RDS, ElastiCache, S3 buckets, SQS queues)

   If none found, note "No k8s/IaC manifests found at standard paths" and move on.

7. **Discover inter-service dependencies** -- scan config files for service references per [patterns.md](patterns.md) (Inter-service Config Patterns section). Check `.env`, `.env.example`, `config.yaml`, `settings.py`, `docker-compose.yml`, and IaC files for:
   - Service URLs (env vars ending in `_URL`, `_HOST`, `_ENDPOINT`, `_DSN`)
   - Database connection strings
   - Queue/topic names
   - `depends_on` in docker-compose
   - Terraform `data` sources and `resource` outputs referencing other services

8. **(--reverse only) Reverse dependency scan** -- scan sibling directories (`~/`, `~/repos/`) for imports or references to this project:
   - Language imports matching the project's module/package name
   - Config references (env vars, URLs containing the project name)
   - K8s manifest references (Service names, ExternalName entries)

   Performance: this scans all siblings. For repos with 10+ sibling projects, warn that scan may consume significant context. If context pressure is high, suggest `context: fork` for the next invocation.

9. **Build ASCII dependency graph** -- collapse leaf modules into their parent where a parent has only leaf children. Choose graph style based on module count:
   - Under 6 modules: box diagram (see [report-template.md](report-template.md) for example)
   - 6+ modules: flat list format (box diagrams with many cross-cutting edges become unreadable)

    ```
    api -> service, auth
    service -> models, cache
    auth -> models

    External: PostgreSQL, Redis, S3
    ```

10. **Write the report** to `<project-repo>/.claude/agent-memory/designer/dependencies.md` using the template in [report-template.md](report-template.md). Overwrite any existing report -- this is a point-in-time snapshot, not cumulative. Create the directory if needed. Delegate to scribe if guard-md blocks. Include all sections that produced findings; omit Inter-service Dependencies if none found, omit Reverse Dependencies if `--reverse` was not used.

11. **Report** -- summarize to the user: module count, external service count, circular deps found (with cycle paths), hub modules (with names), detected language(s), and the report file path.

## Edge Cases

- **Monorepo with shared packages**: If the project root contains workspace config (`pnpm-workspace.yaml`, `package.json` with `workspaces`, `go.work`), resolve the workspace member globs to directories and treat each member as a module. For JS/TS also check `tsconfig.json` `references` as an authoritative dependency declaration between packages. Shared packages (e.g., `packages/shared/`, `libs/common/`) are internal dependencies -- graph them like any other module but tag them as `shared` in the Role column.
- **Vendored dependencies**: Skip `vendor/`, `third_party/`, and `_vendor/` directories entirely for module discovery and import tracing. They are not project code. If a vendored package is imported, record the import target (e.g., `github.com/foo/bar`) as an external dependency, not an internal module.
- **Git submodules**: Check for `.gitmodules`. Submodule directories contain external code -- do not traverse them for internal module discovery. If project source imports from a submodule path, record it as an external dependency with a note "(git submodule)" in the report.
- **Build-generated code**: Skip directories matching `gen/`, `generated/`, `proto/gen/`, `__generated__/`. If imports reference generated code, note the import but do not trace into the generated files.

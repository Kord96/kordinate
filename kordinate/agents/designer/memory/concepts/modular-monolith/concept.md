---
description: Modular Monolith architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [architectural]
---
# Modular Monolith

## Recognition

How to identify this pattern in code.

### Signatures

- Single deployable unit with internal module boundaries (`modules/`, `packages/`, `domains/`)
- Explicit module interfaces or public API surfaces with restricted cross-module imports
- Inter-module communication through defined contracts, events, or mediator -- not direct class imports
- Module-level dependency rules enforced by linting, architecture tests, or build constraints
- Shared kernel or common module for cross-cutting types used by multiple modules
- Single Dockerfile or deployment artifact containing all modules
- Java: multi-module Gradle/Maven build (`settings.gradle` with `include` for multiple subprojects, parent `pom.xml` with `<modules>`) producing a single deployable artifact
- Java: Gradle `buildSrc/` with shared build logic across modules, but single `application` plugin in one root module
- Java: module-level `package-info.java` with visibility restrictions, `@ArchTest` (ArchUnit) enforcing module boundaries
- Go: single `main.go` with `internal/` packages organized by domain (e.g., `internal/auth/`, `internal/billing/`, `internal/orders/`)
- Python: single package with `__init__.py` subpackages organized by domain, single entry point

### Structural indicators (presence of 2+ suggests modular monolith)

- Multiple top-level domain directories (3+) within a single deployable unit
- A `common/` or `shared/` module alongside domain modules
- Single build output (one JAR/binary/container) from multi-module source
- No service-to-service HTTP/gRPC calls between modules (distinguishes from microservices)

### Confidence

- **high** -- Single deployment with enforced module boundaries, explicit public APIs per module, and architecture tests preventing cross-boundary imports
- **medium** -- Directory structure with `modules/` or `packages/` and some import restrictions but no enforcement tooling
- **low** -- Monolith with logical grouping by feature directory but no formal boundary enforcement

## Architecture

Look for strong module boundaries within a single deployable, with communication through contracts not direct coupling.

### Review Checklist

- Each module exposes a well-defined public API and hides internal implementation details
- Cross-module dependencies flow in one direction or through shared abstractions
- Architecture tests or lint rules enforce module boundary violations at build time
- Inter-module communication uses events, mediator, or interfaces -- not direct internal class references
- Database tables are logically partitioned by module even if they share a physical database

### Anti-patterns

- Modules importing internal classes from other modules, bypassing the public API
- Circular dependencies between modules that prevent independent reasoning about each
- No enforcement mechanism -- boundaries exist in documentation only and erode over time
- All modules sharing a single god-object or global state that couples them implicitly

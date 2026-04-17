---
description: Modular Monolith architectural pattern
type: pattern
graphable: true
abstraction:
- architectural
status: primary
scope: cross-cutting
relationships:
  related_to:
  - layered
  - hexagonal
  - microservices
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
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

### Relationship To Other Concepts

- Related to [layered](/concepts/layered) and [hexagonal](/concepts/hexagonal) because modular monoliths often use one or both to structure internals while staying in one deployment unit.
- Related to [microservices](/concepts/microservices) as the main alternative when modules are split into separately deployable services.

### Boundary

Use `modular-monolith` when one deployable application is intentionally divided into strong internal modules with enforced boundaries.

Do not use it for any ordinary monolith. The defining feature is explicit modular discipline inside one deployment boundary.

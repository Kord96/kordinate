---
description: Circular Dependency anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
graphable: false
---
# Circular Dependency

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Module A imports module B which imports module A (direct cycle)
- Transitive cycles: A imports B, B imports C, C imports A
- `ImportError` or `AttributeError` at runtime due to partially initialized modules
- `from __future__ import annotations` used specifically to break import cycles
- `TYPE_CHECKING` blocks (`if TYPE_CHECKING: import ...`) to separate runtime from type-time imports
- Deferred imports inside function bodies to avoid top-level circular references
- Build tools reporting dependency cycle warnings

### Confidence

- **high** -- direct A-imports-B-imports-A cycle, runtime ImportError traced to circular imports, function-level imports with comments explaining the cycle
- **medium** -- `TYPE_CHECKING` imports or `from __future__ import annotations` used to work around import issues, transitive cycles visible in dependency graphs
- **low** -- modules that seem conceptually intertwined and might form cycles under future changes

## Impact

Creates fragile import ordering, makes modules impossible to test or refactor independently, and causes mysterious runtime failures.

### Symptoms

- Import order matters: rearranging imports or moving code between files causes runtime crashes
- Unit testing a single module pulls in a chain of unrelated modules
- Refactoring one module forces changes in its cycle partners
- IDE tooling and static analysis struggle to resolve types across the cycle
- New developers encounter confusing errors when adding imports that close a cycle

### Remediation

- Extract the shared concepts into a new module that both sides depend on (dependency inversion)
- Use interfaces or protocols: depend on abstractions rather than concrete implementations
- Apply the Dependency Inversion Principle: high-level modules define interfaces, low-level modules implement them
- Merge tightly coupled modules if they truly represent one concept split artificially
- Use dependency graph visualization tools to detect and monitor cycles in CI

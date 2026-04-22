---
kind: concept
name: tight-coupling
signatures: {}
source:
  memory_concept: memory/catalog/concepts/tight-coupling.md
type: anti-pattern
abstraction: []
scope: backend
status: supporting
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Concrete class references everywhere with no interfaces or protocols between components
- Constructors that create their own dependencies internally (`self.db = Database()`) instead of receiving them via injection
- Direct database calls and HTTP requests embedded in business logic methods
- Changing one class signature breaks many other classes that reference it directly
- Extensive use of `isinstance` checks against concrete types to branch behavior

### Confidence

- **high** -- business logic directly instantiates infrastructure (database connections, HTTP clients, file handles) and changing one class cascades compilation or test failures across 5+ other files
- **medium** -- no dependency injection framework or manual injection pattern, concrete types used in method signatures instead of abstractions
- **low** -- classes reference each other by name but the coupling might be intentional and stable

## Impact

Cannot test, swap, or evolve components independently because every piece is wired directly to its collaborators.

### Symptoms

- Unit tests require real databases, network connections, or complex mocks because dependencies cannot be substituted
- Swapping an implementation (e.g., switching from PostgreSQL to SQLite for testing) requires modifying business logic code
- A single interface change ripples across the codebase
- Components cannot be reused in different contexts because they hard-code their environment
- Feature flags and A/B tests are difficult because alternatives cannot be injected

### Remediation

- Introduce interfaces or protocols at component boundaries and depend on those rather than concrete classes
- Apply constructor injection: pass dependencies in rather than creating them internally
- Use a composition root or lightweight DI container to wire dependencies at application startup
- Isolate infrastructure behind adapter interfaces (ports and adapters / hexagonal architecture)
- Write tests that verify coupling: if a unit test needs more than 2-3 test doubles, the unit is too coupled

### Relationship To Other Concepts

- Related to [dependency-injection](/concepts/dependency-injection) because injected boundaries are one common remedy for tight coupling.
- Related to [hexagonal](/concepts/hexagonal) because ports-and-adapters architectures exist partly to reduce direct dependence on infrastructure details.
- Related to [leaky-abstraction](/concepts/leaky-abstraction) when coupling persists because abstractions fail to hide implementation details.

### Boundary

Use `tight-coupling` when modules or classes depend so directly on each other’s concrete details that they cannot evolve, test, or swap independently.

Do not use it for every direct dependency; the issue is rigidity and lack of meaningful isolation.

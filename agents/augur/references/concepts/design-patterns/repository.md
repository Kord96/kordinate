---
kind: concept
name: repository
signatures:
  concept: repository
  positive:
    strong:
    - Repository class or interface with CRUD/query methods
    - framework repository primitives used behind service/domain layers
    medium:
    - data access abstraction not explicitly named Repository
    weak:
    - thin wrapper around raw queries
  negative:
  - direct queries scattered outside the abstraction
  - repository returns raw ORM internals everywhere
  notes:
  - Names alone are not sufficient; look for separation of storage concerns.
source:
  memory_concept: memory/catalog/concepts/repository.md
type: pattern
abstraction:
- design
- data
scope: backend
status: primary
review_questions:
  threshold: 6
  entries:
  - id: repository-domain-facing-interface
    prompt: Does the repository expose a stable data-access contract to the domain
      or service layer?
    weight: 3
    signals:
    - Repository
    - JpaRepository
    - '@Repository'
  - id: repository-storage-separation
    prompt: Is storage logic encapsulated here rather than leaking direct queries
      into services or controllers?
    weight: 3
    signals:
    - session.query
    - prisma
    - SELECT
monitoring:
  applies_to:
  - component
  - dependency
  health_signals:
  - name: repository.error.rate
    description: Failure rate of repository operations, grouped by repository or aggregate
      boundary.
  - name: repository.latency
    description: Latency distribution for repository operations that cross a persistence
      boundary.
  - name: repository.slow_query.rate
    description: Rate of repository calls crossing slow-query or saturation thresholds.
  business_metrics:
  - name: repository.write.success.rate
    description: Fraction of repository-backed writes that complete successfully on
      the primary persistence path.
  - name: repository.read.freshness
    description: Freshness or staleness of reads when repository calls depend on caches,
      replicas, or asynchronous projections.
  gaps:
  - If repository calls are not visible separately from application logic, persistence
    regressions are hard to isolate.
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Classes ending in `Repository` or `Repo` (e.g., `UserRepository`, `OrderRepo`)
- CRUD methods: `find()`, `find_by_id()`, `save()`, `delete()`, `list()`
- Interface or abstract base class defining data access contract
- Domain objects have no knowledge of storage mechanism
- SQLAlchemy repository classes wrapping session queries
- Spring Data `@Repository` annotation or `JpaRepository` interface
- Separate `repositories/` directory or module

### Confidence

- **high** -- classes named `*Repository` with CRUD methods that accept and return domain objects
- **medium** -- data access abstracted behind an interface but not explicitly named Repository
- **low** -- service layer delegates to a class that wraps raw queries

## Architecture

Look for clean separation between domain logic and data access with a consistent query interface.

### Review Checklist

- Repository returns domain objects, not raw database rows or ORM models
- Repository interface is defined independent of the storage implementation
- Query logic lives inside the repository, not leaked into services or controllers
- Repositories are injected as dependencies, not instantiated inline
- Bulk operations and pagination are handled without bypassing the repository

### Anti-patterns

- Repository methods that return ORM-specific objects (leaking persistence concerns)
- Fat repositories with business logic mixed into query methods
- One repository per table instead of per aggregate root
- Bypassing the repository with direct queries elsewhere in the codebase

### Relationship To Other Concepts

- Related to [aggregate](/concepts/aggregate) when repositories persist and load aggregate roots rather than isolated tables.
- Related to [data-mapper](/concepts/data-mapper) when persistence mapping is kept separate from domain entities and the repository provides the domain-facing collection interface.
- Related to [unit-of-work](/concepts/unit-of-work) when repository operations share one transactional coordination boundary.

### Boundary

Use `repository` when the architectural point is storage access being abstracted behind a domain-facing query and persistence interface.

Do not use it just because a class touches a database. DAO wrappers, raw query helpers, and ORM model methods alone are not enough unless they establish a clear repository boundary.

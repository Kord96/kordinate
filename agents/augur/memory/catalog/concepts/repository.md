---
description: Repository architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- design
- data
status: primary
scope: backend
relationships:
  related_to:
  - aggregate
  - data-mapper
  - unit-of-work
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# Repository

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

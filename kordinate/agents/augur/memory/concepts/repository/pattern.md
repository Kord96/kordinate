---
description: Repository architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, data]
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

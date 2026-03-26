---
description: Domain-Driven Design architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
---
# Domain-Driven Design (DDD)


## Recognition

How to identify this pattern in code.

### Signatures

- `Entity`, `ValueObject`, or `AggregateRoot` base classes or interfaces in domain layer
- `DomainEvent` classes published from aggregate operations
- `Repository` interfaces defined in the domain layer, implemented in infrastructure
- `domain/` package or directory structure separating domain logic from infrastructure
- Bounded context directories or modules with explicit boundaries (e.g., `ordering/`, `shipping/`, `inventory/`)

### Confidence

- **high** -- aggregate roots enforcing invariants, domain events published on state changes, repository interfaces in the domain layer, and bounded context boundaries with anti-corruption layers
- **medium** -- domain layer with entities and value objects but aggregates do not enforce invariants strictly, or bounded contexts share some infrastructure
- **low** -- `domain/` package exists with entity-like classes but no explicit aggregates, events, or bounded context separation

## Architecture

Look for clear bounded context boundaries with no leaking of internal models.

### Review Checklist

- Each bounded context owns its data and exposes only domain events or APIs
- Aggregates enforce invariants — no external code mutates aggregate state directly
- Ubiquitous language is consistent within a context (naming matches domain terms)
- Anti-corruption layers translate between contexts — no shared domain objects
- Context map exists documenting upstream/downstream relationships

### Anti-patterns

- Shared database tables across bounded contexts
- Domain objects imported directly from another context's internals
- Anemic domain model — aggregates are plain data bags with logic elsewhere
- God aggregate that grows unbounded instead of splitting into sub-contexts

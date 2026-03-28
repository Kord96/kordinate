---
description: Domain-Driven Design architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [architectural, design]
---
# Domain-Driven Design (DDD)


## Recognition

How to identify this pattern in code.

### Signatures

- `AggregateRoot` or `ValueObject` base classes/interfaces in a domain layer
- `DomainEvent` classes published from aggregate operations
- Java: packages named `domain.model`, `domain.service`, `domain.event` with DDD building blocks
- Java: Axon Framework `@Aggregate`, `@AggregateIdentifier`, `@CommandHandler`, `@EventSourcingHandler`
- Go: `domain/` package with entity, value object, and repository interface definitions separate from infrastructure
- Bounded context directories with explicit boundaries (e.g., `ordering/`, `shipping/`, `identity/`)
- Ubiquitous language: class/struct names that map directly to business domain concepts (not technical terms)

### Negative signals (not sufficient for detection)

- The word `Entity` alone (JPA `@Entity`, HTML entity, database entity) is NOT DDD. Look for DDD-specific building blocks like `AggregateRoot`, `ValueObject`, `DomainEvent`.
- A `Repository` interface alone is the repository pattern, not necessarily DDD. DDD requires multiple building blocks together.
- A `domain/` directory alone is not DDD -- many projects use `domain/` as a generic package name without DDD practices.

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

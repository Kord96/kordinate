---
description: Ddd architectural pattern
curated: true
scope: global
---
# Domain-Driven Design (DDD)


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

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO

---
kind: concept
name: data-mapper
signatures:
  concept: data-mapper
  positive:
    strong:
    - explicit mapper classes translating between domain entities and persistence
      rows
    - plain domain objects with separate persistence mapping layer
    medium:
    - repositories or mappers isolate most persistence translation
    weak:
    - helper functions map records, but domain models still know the ORM
  negative:
  - entities inherit directly from ORM base classes and own persistence behavior
  - mapping logic is scattered through services with no clear mapper boundary
  notes:
  - Distinguish this from active-record; Data Mapper keeps persistence out of the
    domain model.
type: pattern
abstraction:
- design
- data
scope: backend
status: primary
review_questions:
  threshold: 6
  entries:
  - id: data-mapper-separate-mapping-layer
    prompt: Is persistence translation handled in explicit mapper classes or functions
      separate from the domain model?
    weight: 3
    signals:
    - Mapper
    - toEntity
    - toPersistence
  - id: data-mapper-domain-decoupled
    prompt: Are domain entities free of ORM base classes and persistence APIs?
    weight: 3
    signals:
    - from_row
    - mapper
    - repository
monitoring:
  applies_to:
  - component
  - state
  health_signals: []
  business_metrics: []
  gaps:
  - Data Mapper is structural; monitor the persistence boundary it supports, not the
    concept directly.
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Separate mapper classes that transfer data between domain objects and database rows
- Domain models have zero persistence logic (no `save()`, no `query()`)
- Explicit mapping functions: `to_entity()`, `from_row()`, `map_to_model()`
- SQLAlchemy classical mapping: `mapper()` calls separate from model definitions
- TypeORM entity decorators with repository pattern alongside
- Dedicated `mappers/` directory or mapping configuration files
- Domain objects are plain classes or dataclasses with no ORM base class

### Confidence

- **high** -- domain models are plain objects and a separate mapper handles all persistence translation
- **medium** -- ORM entities exist but domain logic uses separate DTOs or value objects mapped from them
- **low** -- mapping functions exist but domain objects still inherit from an ORM base

## Architecture

Look for domain models completely decoupled from the database, with an explicit mapping layer in between.

### Review Checklist

- Domain objects have no import of any ORM or database library
- Mapper handles both directions: domain-to-persistence and persistence-to-domain
- Complex relationships (aggregates, value objects) are mapped correctly, not flattened
- Mapper is tested independently with both domain and persistence fixtures
- Schema changes require mapper updates but never domain model changes

### Anti-patterns

- Domain objects importing or inheriting from ORM classes (mapper becomes pointless)
- Mapper that simply copies fields 1:1 with no structural difference (unnecessary indirection)
- Mapping logic scattered across services instead of centralized in mapper classes
- Leaking database column names into the domain model vocabulary

### Relationship To Other Concepts

- Related to [repository](/concepts/repository) because repositories often expose domain-facing access while mappers handle the persistence translation underneath.
- Related to [unit-of-work](/concepts/unit-of-work) when object state changes are tracked and flushed through one transactional boundary.
- Usually prefer this over [active-record](/concepts/active-record) when persistence logic is intentionally separated from domain objects.

### Boundary

Use `data-mapper` when the architecture deliberately keeps domain objects persistence-ignorant and translates them through a dedicated mapping layer.

Do not use it for any serialization or DTO mapping code. The key distinction is mapping between domain objects and persistence representations.

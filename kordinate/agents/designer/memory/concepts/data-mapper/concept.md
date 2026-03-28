---
description: Data Mapper architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design, data]
---
# Data Mapper

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
- Java: MapStruct `@Mapper` annotation with `@Mapping` field definitions
- Java: ModelMapper, Dozer, or Orika mapper configuration

### Negative signals (not sufficient for detection)

- Classes named `*Mapper` that perform non-mapping operations (e.g., Jackson `ObjectMapper` for JSON serialization, MyBatis SQL mappers, codec/converter classes)
- Generic `Mapper` suffix on utility classes that transform data formats rather than mapping between domain and persistence layers

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

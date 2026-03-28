---
description: Value Object architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: false
abstraction: [design]
---
# Value Object

## Recognition

How to identify this pattern in code.

### Signatures

- `@dataclass(frozen=True)` or `@attr.s(frozen=True)` in Python
- `record` types in Java 16+ or C# -- look for `public record ClassName(` declarations
- Java: Lombok `@Value` annotation (creates immutable class with equals/hashCode by value)
- Java: classes with `private final` fields only, `equals()`/`hashCode()` based on all fields, no setters
- Kotlin: `data class` declarations (automatic value semantics)
- `__eq__` and `__hash__` implemented based on all fields, not identity
- No setter methods or mutating operations on the object
- `frozenset` or `tuple` used instead of mutable collections
- Factory methods that return new instances instead of modifying existing ones
- Classes named `*Value`, `*Amount`, `*Range`, `*Address`, `*Money`, `*Quantity`
- Go: small structs with value semantics (passed by value, compared with `==`), no ID field

### Negative signals (not sufficient for detection)

- Java `record` declarations alone are NOT evidence of the value-object pattern as an architectural concern. Java 16+ records are a language feature used for DTOs, configuration, events, API responses -- not necessarily DDD value objects. The pattern requires intentional DDD design where value objects represent domain concepts with equality by value and no identity.
- Go `struct` types are always value types by default -- this does not make them value objects. Look for intentional DDD value object design.
- Lombok `@Value` is also commonly used for simple data carriers, not necessarily DDD value objects.
- The word `Value` in method or variable names (e.g., `getValue()`, `defaultValue`, `valueOfField`) is generic programming, not the pattern.

### Confidence

- **high** -- Immutable class with equality by value, no ID field, and a factory method for transformations
- **medium** -- Frozen dataclass or record type with no setters, but equality semantics not explicitly defined
- **low** -- Plain class that happens to have no setters but is compared by reference or has an ID field

## Architecture

Look for immutable objects that are compared by their field values rather than by identity.

### Review Checklist

- Object is immutable after construction (no setters, no mutable internal state)
- Equality is based on all significant fields, not object identity
- Hash code is consistent with equality (same fields used)
- Validation happens at construction time -- invalid states are impossible
- Transformations return new instances rather than mutating in place

### Anti-patterns

- Value object with an `id` field that participates in equality checks
- Mutable fields hidden behind an immutable facade (e.g., internal mutable list)
- Equality defined on a subset of fields, breaking substitutability
- Value objects that grow to hold behavior unrelated to the value they represent

See also: ddd

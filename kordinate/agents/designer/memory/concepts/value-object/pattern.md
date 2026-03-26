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
- `record` types in Java 16+ or C#
- `__eq__` and `__hash__` implemented based on all fields, not identity
- No setter methods or mutating operations on the object
- `frozenset` or `tuple` used instead of mutable collections
- Factory methods that return new instances instead of modifying existing ones
- Classes named `*Value`, `*Amount`, `*Range`, `*Address`, `*Money`, `*Quantity`

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

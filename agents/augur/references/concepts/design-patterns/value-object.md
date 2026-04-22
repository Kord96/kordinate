---
kind: concept
name: value-object
signatures: {}
source:
  memory_concept: memory/catalog/concepts/value-object.md
type: pattern
abstraction:
- design
scope: backend
status: primary
---

# Explanation

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

### Relationship To Other Concepts

- Related to [ddd](/concepts/ddd) because value objects are a core tactical DDD building block.
- Related to [aggregate](/concepts/aggregate) because aggregates often compose immutable value objects to model constrained state.

### Boundary

Use `value-object` when the code models immutable domain values defined by their fields rather than by identity.

Do not use it for any small DTO or helper struct. The important signal is value-based equality and domain meaning, not just a small immutable class.

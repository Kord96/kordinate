---
description: Builder architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- design
status: primary
scope: backend
relationships:
  related_to:
  - abstract-factory
  - factory
  - fixture-builder
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Builder

## Recognition

How to identify this pattern in code.

### Signatures

- Classes ending in `Builder`, `Config`, or `Options` with fluent setter methods
- Methods returning `self` or `this` to enable chaining
- Terminal `build()`, `create()`, or `make()` method that produces the final object
- Python: setter methods with `return self`, `@dataclass` with builder wrapper
- JS/TS: method chaining patterns, optional `Director` class orchestrating build steps
- Go: functional options pattern (`With*()` functions), or `*Builder` structs with `Build()` method

### Confidence

- **high** -- class named `*Builder` with fluent methods and a terminal `build()` returning a different type
- **medium** -- method chaining returning `self`/`this` with a finalizing method
- **low** -- constructor with many optional parameters or a config dict

## Architecture

Look for separation between construction steps and the final product representation.

### Review Checklist

- Builder validates required fields in `build()`, not silently producing incomplete objects
- Builder is independent of the product's internal representation
- Fluent methods are idempotent (calling the same setter twice overwrites, not appends)
- Builder can be reused to create multiple instances without state leakage between builds
- Director (if present) encapsulates a specific construction sequence, not arbitrary logic

### Anti-patterns

- Builder that exposes product internals (setters map 1:1 to private fields)
- No validation in `build()` -- produces invalid objects that fail later at runtime
- Builder and product tightly coupled -- changing the product breaks the builder
- God-builder with dozens of methods that should be split into multiple builders

### Relationship To Other Concepts

- Related to [abstract-factory](/concepts/abstract-factory) and [factory](/concepts/factory) because all three encapsulate object creation with different tradeoffs.
- Related to [fixture-builder](/concepts/fixture-builder) when the builder idiom is specialized for tests or sample data creation rather than production object construction.

### Boundary

Use `builder` when object construction is intentionally staged or configured through a fluent or stepwise assembly API before producing the final result.

Do not use it for any options object or helper factory. The important signal is deferred, structured construction of a complex product.

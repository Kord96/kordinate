---
description: Builder architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
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

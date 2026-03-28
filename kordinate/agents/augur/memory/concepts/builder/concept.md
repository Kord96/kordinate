---
description: Builder architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
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
- Fluent API without `Builder` naming: method-chaining like `.row().add().text()` or `.field().value().color()` that incrementally constructs a complex structure (e.g., keyboard builders, query builders, form builders)
- Domain-specific builders: `KeyboardBuilder`, `QueryBuilder`, `MessageBuilder`, `EmbedBuilder` with incremental `.add*()` methods

### Negative signals (not builder pattern)

- Java: Lombok `@Builder` on a simple DTO/entity without custom build logic is annotation-driven boilerplate, not the Builder pattern
- Java: `Stream.builder()`, `StringBuilder`, `ProcessBuilder` are JDK utility builders, not architectural builder patterns
- Mere presence of `.builder()` calls without a custom Builder class with multi-step construction is not sufficient
- Python: `.build()` on Mailable, Notification, or Message classes that simply finalize configuration options is not builder -- it is just a setup/finalize lifecycle method. Builder requires a separate Builder class or multi-step fluent construction producing a different type
- TypeScript/Python: `.build()` as a lifecycle method on a class (e.g., `mailable.build()`, `task.build()`) where the object configures itself is not builder pattern. Builder pattern requires constructing a separate product object through incremental steps
- Query builders in ORMs (`.where().order_by().limit()`) are the builder pattern only when they construct a separate query object, not when they are simply method chaining on the query itself
- Java: `.builder()` in test code constructing simple objects (DTO, config) with Lombok or Proto builders is boilerplate, not the pattern. The pattern requires intentional multi-step construction with meaningful build logic.
- Go: `func New*()` constructors are standard Go, not the builder pattern. Look for explicit `*Builder` struct with `Build()` method or functional options (`With*()` functions) as a conscious design choice.
- The mere presence of `Builder` class names (e.g., `StringBuilder`, `ProcessBuilder`, `ServerBuilder`) from standard libraries or frameworks is framework usage, not an architectural pattern choice.
- TypeScript: `.build()` on a schema or config object (e.g., `z.object({}).build()`, `schema.build()`, `createTRPCRouter({})`) is framework API, not the builder pattern. The builder pattern requires a separate Builder class with incremental `.with*()` or `.add*()` methods constructing a product.

### Confidence

- **high** -- custom `*Builder` class with fluent methods, multi-step construction, and a terminal `build()` returning a different type
- **medium** -- method chaining returning `self`/`this` with a finalizing method and non-trivial construction logic
- **low** -- constructor with many optional parameters, config dict, or Lombok `@Builder` without custom build steps

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

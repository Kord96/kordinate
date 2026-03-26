---
description: Factory Method architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Factory

## Recognition

How to identify this pattern in code.

### Signatures

- Classes ending in `Factory`, `Creator`, or `Provider`
- Methods named `create`, `make`, `build`, `new_*`, or `get_*` that return interfaces/base types
- Switch/match statements on a type discriminator to select which concrete class to instantiate
- Python: `class *Factory` with `create()` methods returning protocol/ABC instances
- Java/TS: `interface *Factory` with generic creation methods
- Go: `New*()` free functions returning interfaces

### Confidence

- **high** -- class named `*Factory` with `create()` returning an interface type, plus multiple concrete implementations
- **medium** -- function that switches on a type string to return different implementations of the same interface
- **low** -- constructor-like function returning a base class or union type

## Architecture

Look for correct abstraction: callers depend on the factory interface, never on concrete product classes.

### Review Checklist

- Factory returns interfaces/protocols, not concrete types
- Adding a new product type does not require modifying existing factory code (open/closed)
- Factory creation logic is centralized, not duplicated across callers
- Error handling for unknown or unsupported product types is explicit

### Anti-patterns

- Factory that returns concrete classes, defeating the abstraction
- Giant switch/match that must be edited for every new type (violation of open/closed)
- Factory with side effects beyond object creation (network calls, disk I/O)
- Caller immediately casting the factory result to a concrete type

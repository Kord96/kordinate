---
kind: concept
name: bridge
signatures: {}
type: pattern
abstraction:
- design
scope: backend
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Separating abstraction from implementation so both can vary independently
- Abstraction holding a reference to an implementor interface
- Platform-specific implementations behind a stable API
- `*Impl` classes or interfaces (`Renderer`, `RendererImpl`, `OpenGLRenderer`)
- Constructor injection of the implementation into the abstraction
- Two parallel class hierarchies (one for abstraction, one for implementation)

### Confidence

- **high** -- Abstraction class holding a reference to an `Impl` interface, with multiple concrete implementations that can be swapped independently of the abstraction hierarchy
- **medium** -- Interface-based dependency injection where the abstraction and implementation evolve in separate packages or modules
- **low** -- Simple interface extraction without a separate abstraction hierarchy (closer to strategy than bridge)

## Architecture

Look for two independent hierarchies connected by composition: an abstraction hierarchy delegating to an implementation hierarchy.

### Review Checklist

- Abstraction and implementation can vary independently without modifying each other
- Implementation is injected, not hardcoded in the abstraction
- The bridge interface is minimal and stable (changes are rare)
- Both hierarchies are tested independently
- New implementations can be added without modifying existing abstractions
- The indirection is justified by actual variation on both sides

### Anti-patterns

- Only one implementation exists with no realistic expectation of a second (unnecessary abstraction)
- Abstraction leaking implementation details through its interface
- Tight coupling between abstraction and implementation hierarchies despite the bridge
- Confusing bridge with simple interface extraction or strategy pattern

### Relationship To Other Concepts

- Related to [abstract-factory](/concepts/abstract-factory) when a bridge needs families of implementations selected independently from abstractions.
- Related to [adapter](/concepts/adapter) because both introduce indirection, though bridge is about decoupling parallel hierarchies rather than translating one interface into another.
- Related to [strategy](/concepts/strategy) when implementations vary independently behind a stable abstraction surface.

### Boundary

Use `bridge` when abstractions and implementations vary independently and are explicitly decoupled through composition.

Do not use it for simple interface extraction or wrappers. The important signal is two axes of variation kept independent.

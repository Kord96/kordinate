---
description: Decorator/Wrapper architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Decorator/Wrapper

## Recognition

How to identify this pattern in code.

### Signatures

- Object wrapping another object while exposing the same interface
- `@decorator` syntax in Python (function or class decorators)
- Middleware wrapping in web frameworks (`app.use()`, handler chains)
- Logging, caching, or auth wrappers around core logic
- Classes named `*Decorator`, `*Wrapper`, `Logging*`, `Cached*`
- Nested composition: `new AuthDecorator(new LoggingDecorator(new Service()))`
- `functools.wraps`, higher-order functions returning enhanced versions of the input

### Confidence

- **high** -- Class implementing the same interface as the wrapped object, delegating calls and adding behavior before/after
- **medium** -- `@decorator` annotations or middleware chains that wrap request/response processing
- **low** -- Higher-order function that adds behavior but does not preserve the original interface contract

## Architecture

Look for decorators preserving the wrapped object's interface and each decorator handling exactly one concern.

### Review Checklist

- Decorator implements the same interface as the component it wraps
- Each decorator adds exactly one responsibility (logging, caching, auth -- not all combined)
- Decoration order is intentional and documented when order matters
- Decorated object is unaware it is being wrapped -- no back-references or tight coupling
- Stack depth is bounded -- deeply nested decorators add latency and obscure debugging

### Anti-patterns

- Decorator that modifies the wrapped object's interface (callers must know about the decorator)
- God decorator that adds logging, caching, auth, and validation in a single wrapper
- Circular decoration where decorator A wraps B which wraps A
- Decorators with hidden side effects that change behavior in non-obvious ways when composed

See also: proxy (controls access vs adds behavior)

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

- Classes named `*Decorator`, `*Wrapper` implementing the same interface as the wrapped object
- Nested composition: `new AuthDecorator(new LoggingDecorator(new Service()))`
- Python: `@decorator` syntax with `functools.wraps`, higher-order functions returning enhanced versions of the input
- Go: `func(http.Handler) http.Handler` wrapping pattern, middleware that takes and returns the same interface
- Go: Interceptor Bind methods that accept and return the same interface type (e.g., `Bind(reader Reader) Reader`) adding behavior while preserving the contract
- Java: classes named `*Decorator` or `*Wrapper` implementing the same interface as the constructor argument

### Negative signals (not sufficient for detection)

- The word `Wrapper` or `wrap` alone (e.g., line wrapping, text wrapping, error wrapping) is NOT the decorator pattern
- `Logging*` or `Cached*` class names without a shared interface with the wrapped object are utilities, not decorators
- Java annotations like `@Override`, `@Component`, `@Bean` are not the decorator pattern -- look for classes that wrap another instance of the same interface
- Middleware chains (`app.use()`, handler chains) are the middleware pattern, not decorator, unless each middleware implements the same interface as the handler it wraps
- Java: `@interface` (annotation type declarations) are annotation definitions, not the decorator GoF pattern. Java annotations add metadata, not runtime behavior wrapping.
- Go: `Wrapper` or `wrapper` as field names in structs (e.g., wrapping a protobuf message, wrapping an error) is standard composition, not the decorator pattern.

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

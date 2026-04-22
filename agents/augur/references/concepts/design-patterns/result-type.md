---
kind: concept
name: result-type
signatures: {}
source:
  memory_concept: memory/catalog/concepts/result-type.md
type: pattern
abstraction:
- design
- error-handling
scope: backend
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `Result<T, E>`, `Ok()`, `Err()` in Rust code
- `Either<L, R>`, `Left()`, `Right()` from fp-ts, Arrow (Kotlin), or Cats (Scala)
- `match` or `fold` on result types to handle success and failure branches
- No exception throwing for expected/recoverable failures
- Railway-oriented programming: chained `.map()`, `.flatMap()`, `.and_then()` on results
- Custom `Result` or `Outcome` classes with `is_ok()` / `is_err()` methods in Python or TypeScript
- `returns` library in Python with `Result`, `Success`, `Failure`

### Confidence

- **high** — Consistent use of `Result`/`Either` across module boundaries, with `match`/`fold` at call sites and no exceptions for domain errors
- **medium** — Result type used in some modules but exceptions still thrown in others for the same category of errors
- **low** — Functions returning tuples like `(value, error)` or nullable error fields without a formal result type

## Architecture

Look for explicit error paths encoded in return types rather than exception-based control flow for expected failures.

### Review Checklist

- Domain errors are represented as typed variants in the error channel, not generic strings or exception classes
- Result types are propagated through the call chain, not unwrapped immediately at each layer
- Error mapping transforms low-level errors into domain-appropriate errors at boundary crossings
- The `match`/`fold` at the top level handles all error variants exhaustively
- Unexpected errors (panics, runtime exceptions) are still handled separately from typed result errors

### Anti-patterns

- Wrapping every possible error in a Result including panics and programming bugs that should crash
- Calling `.unwrap()` or `.get()` everywhere, discarding the error channel and defeating the purpose
- Mixing Result returns and exception throwing for the same class of errors within a module
- Deeply nested `match` blocks instead of composing results with `map`/`flatMap` chains

### Relationship To Other Concepts

- Related to [null-object](/concepts/null-object) as another alternative to raw nulls, though result types preserve explicit success/failure distinction.
- Related to [error-code-returns](/concepts/error-code-returns) because result types often replace primitive error codes with typed success/failure variants.
- Related to [property-testing](/concepts/property-testing) when generated tests assert laws across success and failure branches of a result abstraction.

### Boundary

Use `result-type` when operations return explicit success/failure values as part of the type system rather than throwing exceptions or returning raw error codes.

Do not use it for any tuple-like return. The key signal is typed outcome modeling with explicit error composition.

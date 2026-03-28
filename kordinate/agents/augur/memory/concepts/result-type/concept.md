---
description: Result/Either Type architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: false
abstraction: [design, error-handling]
---
# Result/Either Type

## Recognition

How to identify this pattern in code.

### Signatures

- `Result<T, E>`, `Ok()`, `Err()` in Rust code
- `Either<L, R>`, `E.left()`, `E.right()` from fp-ts, Arrow (Kotlin), or Cats (Scala)
- `match` or `fold` on result types to handle success and failure branches explicitly
- Custom `Result` or `Outcome` classes with `is_ok()` / `is_err()` / `isOk()` / `isErr()` methods
- Railway-oriented programming: chained `.map()`, `.flatMap()`, `.and_then()` on result types
- `returns` library in Python with `Result`, `Success`, `Failure`
- Go: `(value, error)` return tuples as the standard error handling pattern

**Not this pattern:** The presence of `Either` from fp-ts in a codebase that also uses `pipe()`, `TaskEither`, and monadic composition is the monad pattern -- result-type specifically means using errors-as-values instead of exceptions as the primary error strategy. Also, `try/catch` blocks that return `{ success: true/false }` are not result-type unless they use a formal union type with distinct success/failure branches.

**Not this pattern:** A class named `TaskiqResult`, `QueryResult`, `SearchResult`, `FetchResult`, or similar where `Result` is part of a domain noun (the result of a task/query/search) is not the Result/Either type pattern. The pattern requires a typed union with explicit success/failure branches used as a primary error-handling strategy across the codebase. A Pydantic model or dataclass named `*Result` that holds return data fields is just a response DTO.

### Confidence

- **high** -- Consistent use of `Result`/`Either` across module boundaries, with `match`/`fold` at call sites and no exceptions for domain errors
- **medium** -- Result type used in some modules but exceptions still thrown in others for the same category of errors
- **low** -- Functions returning `(value, error)` tuples or nullable error fields without a formal result type

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

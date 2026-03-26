---
description: Monad/Railway-Oriented Programming architectural pattern
curated: true
scope: global
preloaded: none
---
# Monad/Railway-Oriented Programming

## Recognition

How to identify this pattern in code.

### Signatures

- `bind()`, `flatMap()`, `>>=`, `and_then()`, `chain()` methods for sequencing operations
- `Maybe` / `Option` / `Optional` types wrapping nullable values
- `Result` / `Either` / `Try` types representing success-or-failure
- `map()` and `bind()`/`flatMap()` on container types for chaining transformations
- `do` notation (Haskell), for-comprehensions (Scala), `?` operator (Rust)
- Operations that short-circuit on the first failure without explicit try/catch
- Libraries: `returns` (Python), `fp-ts` (TypeScript), `cats`/`zio` (Scala), `dry-monads` (Ruby)

### Confidence

- **high** -- Explicit `Result`/`Either` types with `bind`/`flatMap` chaining, error channel propagated without exceptions, and library usage (returns, fp-ts, cats)
- **medium** -- `Optional`/`Option` used consistently to avoid nulls with `map` chaining, but error types are not structured
- **low** -- Functions that return tuples like `(value, error)` or use early returns for error handling without a formal monadic type

## Architecture

Look for chained operations on container types that propagate failure automatically without explicit branching.

### Review Checklist

- Success and failure paths are explicit types, not exceptions or null checks
- Operations compose via `bind`/`flatMap`, not nested if-else or try-catch
- Error types carry enough context to diagnose failures at the end of the chain
- The "happy path" reads as a clean pipeline without interleaved error handling
- Side effects are pushed to the edges, keeping the chain pure
- Terminal handling (fold/match/unwrap) happens at the boundary, not mid-chain

### Anti-patterns

- Unwrapping (`unwrap()`, `get()`, `!`) in the middle of a chain, defeating the safety guarantee
- Mixing exceptions and monadic error handling in the same code path
- Overly nested `flatMap` calls instead of using for-comprehensions or do-notation
- Using monadic types for simple cases where a plain if-else would be clearer

---
description: Monad/Railway-Oriented Programming architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: false
abstraction: [design, error-handling]
---
# Monad/Railway-Oriented Programming

## Recognition

How to identify this pattern in code.

### Signatures

- Explicit monadic library imports: `fp-ts` (`pipe`, `E.chain`, `TE.map`), `cats`/`zio` (Scala), `dry-monads` (Ruby), `returns` (Python)
- `bind()`, `flatMap()`, `>>=`, `and_then()`, `chain()` methods composing monadic types across function boundaries
- `do` notation (Haskell), for-comprehensions (Scala)
- `Maybe`/`Option`/`IO` monadic types with explicit `map`/`flatMap` chains
- `pipe()` from `fp-ts/function` composing `Either`/`TaskEither`/`Option` operations

> For `Result`/`Either` as error handling, see result-type. This pattern focuses on monadic composition (bind/chain) across any monad, not just error types.

**Not this pattern:** `.map()` and `.filter()` on arrays, or `Promise.then()` chaining, is standard language usage. The monad pattern requires explicit monadic types (Either, TaskEither, Option, IO) composed via `bind`/`flatMap`/`chain` from a functional programming library. Ad-hoc `.map()` calls are not monadic composition.

### Confidence

- **high** -- Explicit FP library imports (fp-ts, cats, returns) with monadic types composed via `bind`/`flatMap`/`chain`/`pipe`
- **medium** -- `Option`/`Maybe` used consistently with `map`/`flatMap` chaining, but from a less common library
- **low** -- Custom container types with `map()` and `flatMap()` but no established FP library

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

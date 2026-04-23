---
kind: concept
name: monad
signatures: {}
type: pattern
abstraction:
- design
- error-handling
scope: backend
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `bind()`, `flatMap()`, `>>=`, `and_then()`, `chain()` methods for monadic composition
- `do` notation (Haskell), for-comprehensions (Scala)
- `Maybe` / `Option` chaining with `map()` and `bind()`/`flatMap()`
- `IO` monad for sequencing side effects
- `returns` library `flow()` for composing monadic pipelines (Python)
- Libraries: `fp-ts` (TypeScript), `cats`/`zio` (Scala), `dry-monads` (Ruby)

> For `Result`/`Either` as error handling, see result-type. This pattern focuses on monadic composition (bind/chain) across any monad, not just error types.

### Confidence

- **high** -- Explicit monadic types composed via `bind`/`flatMap`/`>>=` with `do` notation or for-comprehensions, and library usage (returns, fp-ts, cats)
- **medium** -- `Option`/`Maybe` used consistently with `map`/`flatMap` chaining but no broader monadic composition
- **low** -- Container types with `map()` but no `bind`/`flatMap`, or ad-hoc chaining without formal monadic structure

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

### Relationship To Other Concepts

- Related to [result-type](/concepts/result-type) because many practical monadic APIs in application code appear as result or option composition.
- Related to [future-promise](/concepts/future-promise) because promises often expose monadic chaining semantics over deferred computations.
- Related to [pipeline-filter](/concepts/pipeline-filter) when monadic composition is used to build linear transformation flows with contextual effects.

### Boundary

Use `monad` when computations are explicitly modeled as composable context-carrying values with bind or flatMap-style chaining semantics.

Do not use it for every fluent API or callback chain that merely looks sequential.

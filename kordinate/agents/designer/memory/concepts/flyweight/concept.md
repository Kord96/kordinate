---
description: Flyweight architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Flyweight

## Recognition

How to identify this pattern in code.

### Signatures

- Factory returning cached immutable instances keyed by intrinsic state, with extrinsic state passed at usage time
- `intern()` methods (string interning, symbol tables)
- `WeakValueDictionary` or `WeakHashMap` for automatic eviction of unused flyweights
- Separation of intrinsic (shared) and extrinsic (context-dependent) state in object design
- Python: `__slots__` to minimize per-instance memory on high-volume objects
- Object cache keyed by identity/intrinsic state returning shared instances

**Not this pattern:** General caching (e.g., query cache, HTTP cache, memoization) is not the flyweight pattern. Flyweight specifically shares immutable object instances to reduce memory when many similar objects exist. A `Map<string, Result>` cache is cache-aside, not flyweight. Also, a `shared` variable or singleton instance is not flyweight unless it separates intrinsic from extrinsic state.

### Confidence

- **high** -- Factory returning cached immutable instances keyed by intrinsic state, with extrinsic state passed in at usage time
- **medium** -- Object pool or interning mechanism that reuses instances but without explicit intrinsic/extrinsic separation
- **low** -- Memoization that reduces object creation for identical inputs

## Architecture

Look for a factory that manages shared immutable instances, separating intrinsic state (shared) from extrinsic state (caller-provided).

### Review Checklist

- Flyweight objects are truly immutable (no mutable intrinsic state)
- Extrinsic state is passed in by the caller, not stored on the flyweight
- Factory ensures identity: same intrinsic state always returns the same instance
- Memory savings are measurable and justified (pattern adds complexity)
- Thread safety of the flyweight pool is addressed in concurrent environments
- Weak references or eviction policy prevents the pool from becoming a memory leak

### Anti-patterns

- Mutable state on flyweight instances, causing shared state corruption
- Storing extrinsic state on the flyweight, defeating the sharing benefit
- Flyweight pool growing unbounded without eviction (memory leak disguised as optimization)
- Applying the pattern where object count is small (premature optimization)

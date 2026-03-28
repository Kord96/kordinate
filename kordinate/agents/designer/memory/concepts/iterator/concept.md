---
description: Iterator architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Iterator

## Recognition

How to identify this pattern in code.

### Signatures

- Custom iterator implementations: classes implementing `Symbol.iterator`/`Symbol.asyncIterator` (JS/TS), `__iter__`/`__next__` (Python), `Iterator` trait (Rust)
- Generator functions: `function*`/`yield` (JS/TS), `def` with `yield` (Python), `async function*` for async iteration
- Lazy evaluation chains: `itertools` (Python), Rust iterator adaptors (`.map().filter().collect()`), Java `Stream` API
- Custom collection types that expose iteration without revealing internal structure
- Cursor-based traversal over large data sets with `next()`/`hasNext()` protocol

**Not this pattern:** Using `.forEach()`, `.map()`, `.filter()` on built-in arrays/collections is standard library usage, not the iterator pattern. The iterator pattern is about implementing custom lazy traversal over a data structure -- providing sequential access without exposing the underlying representation. Every language has `forEach`; that alone is not evidence of this pattern.

### Confidence

- **high** -- custom class implementing the iterator protocol (`Symbol.iterator`, `__iter__`/`__next__`, `Iterator` trait) with lazy element production
- **medium** -- generator function using `yield` to lazily produce elements on demand from a custom data source
- **low** -- custom traversal method that hides internal structure but returns eagerly evaluated results

## Architecture

Look for lazy evaluation and separation of traversal logic from the underlying collection.

### Review Checklist

- Iterator is lazy (elements produced on demand, not pre-computed into a list)
- Iterator protocol is correctly implemented (raises `StopIteration` / returns `None` at end)
- External iteration does not expose collection internals (no index-based access to backing store)
- Iterator supports composition (map, filter, chain) without materializing intermediate collections
- Resource cleanup on early termination (generators with cleanup in `finally`, `__del__`, or context manager)

### Anti-patterns

- Eagerly loading entire dataset into memory when lazy iteration would suffice
- Iterator that mutates the underlying collection during traversal
- Missing `StopIteration` / end signal causing infinite loops
- Custom iterator reimplementing what standard library itertools already provides

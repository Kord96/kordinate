---
description: Iterator architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Iterator

## Recognition

How to identify this pattern in code.

### Signatures

- Python: `__iter__()` / `__next__()` protocol, `yield` generators, `itertools` usage
- JS/TS: `Symbol.iterator`, `next()` returning `{ value, done }`, generators with `function*`/`yield`
- Rust: `Iterator` trait with `next()` returning `Option<Item>`, `IntoIterator`, iterator adaptors
- Go: `for range` over channels, iterator functions returning `func() (T, bool)`
- Java: `Iterator<T>` interface, `Iterable<T>`, `Stream` API
- Lazy evaluation: `itertools.chain`, `map`/`filter`/`reduce` chains, `Stream.of().filter().map()`

### Confidence

- **high** -- class implementing the iterator protocol (`__iter__`/`__next__` or `Iterator` trait) with lazy element production
- **medium** -- generator function using `yield` to produce elements on demand
- **low** -- method returning a list that could be lazy but is eagerly evaluated

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

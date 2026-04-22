---
kind: concept
name: singleton
signatures: {}
source:
  memory_concept: memory/catalog/concepts/singleton.md
type: pattern
abstraction:
- design
scope: backend
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Class variable `_instance`, `__instance`, or `instance`
- Static method `getInstance()`, `get_instance()`, or `shared()`
- Python: `__new__` override checking for existing instance, `@singleton` decorator, module-level instance
- Java/TS: `private constructor` with `static getInstance()`
- Go: `sync.Once` with package-level `var instance`
- Rust: `lazy_static!` or `once_cell::sync::Lazy`

### Confidence

- **high** -- private constructor plus static `getInstance()` with lazy initialization and instance caching
- **medium** -- module-level instance variable with no public constructor, or `__new__` override
- **low** -- global variable used as a shared resource across the codebase

## Architecture

Look for thread safety and verify the singleton is genuinely needed over dependency injection.

### Review Checklist

- Thread-safe initialization (double-checked locking, `sync.Once`, module import)
- No mutable global state that makes testing impossible
- Clear justification for singleton over injected dependency
- Singleton lifecycle is explicit (creation, optional teardown for tests)
- Subclassing is either properly supported or explicitly prevented

### Anti-patterns

- Singleton used as a global grab bag (config, logger, cache, and DB all in one)
- No way to reset or replace the instance in tests
- Lazy initialization with race conditions in multi-threaded contexts
- Hidden dependencies -- classes reach for the singleton instead of receiving it via injection

### Relationship To Other Concepts

- Related to [dependency-injection](/concepts/dependency-injection) because singletons are often overused where injected shared services would be safer and easier to test.
- Related to [service-manager](/concepts/service-manager) when one global instance coordinates lifecycle for a shared service.
- Related to [tight-coupling](/concepts/tight-coupling) because hidden singleton access creates hard-wired global dependencies.

### Boundary

Use `singleton` when one globally shared instance is intentionally enforced as the only instance of a type.

Do not use it for ordinary process-wide services that are simply created once by composition or dependency injection without singleton access semantics.

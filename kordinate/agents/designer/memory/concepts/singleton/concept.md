---
description: Singleton architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Singleton

## Recognition

How to identify this pattern in code.

### Signatures

- Class variable `_instance` with static `getInstance()` and private/protected constructor
- Python: `__new__` override checking for existing instance, `@singleton` decorator, metaclass with `__call__` override
- Python: module-level instance with `_instance` guard: `if _instance is None: _instance = create()`
- Python: Borg pattern: `_shared_state = {}` with `self.__dict__ = self._shared_state` in `__init__`
- Java/TS: `private constructor` with `static getInstance()` enforcing single instance
- Go: `sync.Once` with package-level `var instance` and `GetInstance()` function -- requires both `sync.Once` AND a `var instance` or lazy initialization pattern

### Negative signals (not sufficient for detection)

- Go `sync.Once` used for one-time initialization (e.g., loading config, initializing a logger) without a `GetInstance()` access pattern is initialization, not singleton
- Go package-level `var` without `sync.Once` or access control is a global variable, not a singleton pattern
- Rust: `lazy_static!` or `once_cell::sync::Lazy` for shared global state
- Java: `@Singleton` annotation in DI frameworks (Spring `@Component`, CDI `@ApplicationScoped`, Guice `@Singleton`) is DI scope configuration, not the singleton design pattern. The pattern requires explicit private constructor + static getInstance().
- Go: `var instance` at package level without controlled access (private constructor equivalent + lazy init) is a package-level variable, standard in Go, not the singleton pattern.

**Not this pattern:** Module-level `export const logger = new Logger()` in Node.js/TypeScript is standard module scoping, not the singleton pattern. Node modules are cached by the runtime, making every module-level variable naturally "single instance" -- this is not intentional singleton design. The singleton pattern requires deliberate enforcement: private constructor, lazy initialization check, or thread-safe access control. Similarly, a global database connection or Redis client instantiated once is typical setup, not a design pattern choice.

### Confidence

- **high** -- private constructor plus static `getInstance()` with lazy initialization and instance caching
- **medium** -- `__new__` override or registry-based instance management preventing multiple instantiations
- **low** -- module-level instance explicitly documented as "the single shared instance" with no public constructor

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

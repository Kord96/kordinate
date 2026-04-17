---
description: Null Object architectural pattern
type: pattern
testable: true
graphable: false
abstraction:
- design
status: primary
scope: backend
relationships:
  related_to:
  - result-type
  - strategy
  - singleton
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Null Object

## Recognition

How to identify this pattern in code.

### Signatures

- No-op implementations of interfaces: `NullLogger`, `NoOpCache`, `NullMetrics`
- `NoOp*` or `Null*` or `Noop*` class prefixes implementing a production interface
- Default objects that satisfy an interface contract but perform no work
- Absence of `if x is None` / `if x == null` guard checks at call sites
- Dependency injection frameworks wiring null objects as defaults when no real implementation is configured
- `DevNull*` or `Blackhole*` implementations for sinks (writers, loggers, event emitters)

### Confidence

- **high** — Explicit null object classes implementing the same interface as their real counterparts, injected via DI or used as defaults
- **medium** — Default parameter values that are no-op lambdas or empty objects (e.g., `logger=lambda *a: None`)
- **low** — Scattered `or default` / `?? fallback` expressions that approximate null object behavior inline

## Architecture

Look for polymorphic no-op implementations that eliminate null checks by providing safe default behavior.

### Review Checklist

- Null objects implement the full interface contract, not just the methods currently called
- Null objects are clearly named to signal their intent (prefix with `Null`, `NoOp`, or `Noop`)
- Call sites depend on the interface, never checking which implementation (real vs null) they received
- Null objects are stateless and safe to share as singletons
- Logging or metrics null objects optionally support a debug mode that records calls for testing

### Anti-patterns

- Null objects that silently swallow errors that should be surfaced (hiding real failures)
- Partial null implementations that throw `NotImplementedError` on some methods
- Using null objects where an Optional/Maybe type would be more appropriate (when absence itself is meaningful)
- Null objects with side effects or mutable state that break the expectation of inert behavior

### Relationship To Other Concepts

- Related to [result-type](/concepts/result-type) as another way to model absence or failure explicitly, though result types preserve distinction while null objects substitute inert behavior.
- Related to [strategy](/concepts/strategy) when a no-op strategy implementation acts as the null object.
- Related to [singleton](/concepts/singleton) because null-object implementations are often reused as one shared inert instance.

### Boundary

Use `null-object` when absence is modeled by an inert implementation of the same interface rather than by null checks or option wrappers.

Do not use it for every default implementation. The key signal is replacing null-handling with a safe do-nothing or neutral object.

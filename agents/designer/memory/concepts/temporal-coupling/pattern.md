---
description: Temporal Coupling anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
graphable: false
---
# Temporal Coupling

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Methods that must be called in a specific order (`init()` before `run()`, `connect()` before `query()`) but nothing in the type system enforces it
- Setup methods that silently fail or produce wrong results if called out of order
- Undocumented call sequences that only long-time contributors know
- Objects that are partially initialized after construction and require separate `configure()` or `setup()` calls
- Comments like "must call X before Y" or "call after init" scattered in the codebase
- State machine transitions with no explicit state tracking

### Confidence

- **high** -- calling methods out of order produces a runtime error or silent corruption, and the required order is not enforced by the API
- **medium** -- documentation or comments describe required call order, but the compiler/type system allows violations
- **low** -- a two-step initialization exists but the second step is always called immediately after construction

## Impact

Subtle bugs arise when methods are called in the wrong order, and nothing catches the mistake until runtime -- or worse, the mistake causes silent data corruption.

### Symptoms

- `NullPointerException` or `AttributeError` on fields that should have been set by a prior method call
- Tests pass individually but fail when run in a different order because shared setup was assumed
- Integration bugs appear only when components are wired together in a slightly different sequence
- Onboarding developers trigger errors that existing developers "just know" to avoid
- Race conditions in concurrent code because the required sequence is not atomic

### Remediation

- Use the type system to enforce order: return a new type from each step (Builder pattern, typestate pattern)
- Make constructors fully initialize objects: require all dependencies at construction time
- Combine steps that must happen together into a single method or factory
- If multi-step setup is unavoidable, validate preconditions at the start of each method and fail fast with a clear message
- Replace implicit state transitions with an explicit state machine that rejects invalid transitions

---
kind: concept
name: temporal-coupling
signatures: {}
type: anti-pattern
abstraction: []
scope: backend
status: supporting
family: anti-patterns
---

# Explanation

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

### Relationship To Other Concepts

- Related to [workflow-state-machine](/concepts/workflow-state-machine) because explicit state transitions are one way to make ordering constraints visible instead of implicit.
- Related to [builder](/concepts/builder) when staged construction is used to enforce valid call sequences through types or phased APIs.
- Related to [service-manager](/concepts/service-manager) because lifecycle APIs often suffer from hidden ordering requirements if startup and shutdown contracts are unclear.

### Boundary

Use `temporal-coupling` when correct behavior depends on undocumented or weakly enforced call ordering between operations.

Do not use it for explicit protocols or state machines where the required ordering is first-class and enforced.

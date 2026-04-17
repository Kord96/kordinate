---
description: Misleading Names anti-pattern
type: anti-pattern
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - inconsistent-naming
  - hidden-side-effects
  - leaky-abstraction
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Misleading Names

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `get*` methods that mutate state or have side effects (database writes, cache invalidation, HTTP calls)
- `is*` or `has*` functions returning non-boolean values (strings, integers, objects)
- `create*` that returns an existing object from cache or lookup instead of constructing a new one
- `validate()` methods that also save, send, or transform data beyond validation
- `check*` functions that silently fix the problem they detect
- `find*` methods that create records when none are found (find-or-create hidden behind a find name)

### Confidence

- **high** -- a `get*` method contains INSERT/UPDATE statements, HTTP calls, or file writes
- **medium** -- a method named for one action (validate, check, find) also performs a second unrelated action
- **low** -- method names use vague verbs (handle, process, do) that could mean anything

## Impact

Readers assume wrong behavior from the name, leading to unintended side effects, double writes, and bugs that survive code review because the name looked correct.

### Symptoms

- Calling a getter triggers unexpected state changes or performance degradation
- Code reviewers approve dangerous calls because the method name sounds safe
- Developers duplicate logic because they do not realize a misnamed method already does what they need
- Tests pass in isolation but fail in sequence because a "read" method mutated shared state
- Debug sessions are prolonged because side effects hide behind innocent-looking names

### Remediation

- Rename methods to reflect all their behavior: `getOrCreateUser`, `validateAndSave`, `ensureExists`
- Split methods that do multiple things: separate `validate()` from `save()`
- Enforce naming conventions in code review checklists: getters must be pure, `is*` must return boolean
- Add linting rules that flag `get*` methods containing write operations
- Document side effects in docstrings when renaming is not immediately feasible

### Relationship To Other Concepts

- Related to [inconsistent-naming](/concepts/inconsistent-naming) because misleading names often coexist with broader naming drift.
- Related to [hidden-side-effects](/concepts/hidden-side-effects) when a harmless-sounding name conceals mutation or external work.
- Related to [leaky-abstraction](/concepts/leaky-abstraction) when inaccurate names expose or disguise the wrong boundary semantics.

### Boundary

Use `misleading-names` when a symbol’s name actively creates the wrong expectation about behavior, return shape, or responsibility.

Do not use it for names that are merely verbose, stylistically awkward, or inconsistent with local convention.

---
description: Prototype architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- design
status: primary
scope: backend
relationships:
  related_to:
  - builder
  - factory
  - fixture-builder
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Prototype

## Recognition

How to identify this pattern in code.

### Signatures

- Creating objects by cloning existing instances rather than constructing from scratch
- `clone()` methods on domain objects
- `copy()` / `deepcopy()` (Python `copy` module)
- `Object.assign()` or spread operator (`{...obj}`) for object creation from templates
- Prototype chains in JavaScript (`Object.create()`)
- Prototype registry or catalog of pre-configured instances
- `Cloneable` interface (Java)

### Confidence

- **high** -- Explicit `clone()` method with a prototype registry that returns copies of pre-configured template objects
- **medium** -- `deepcopy()` or spread-based cloning used to create variants of a base configuration or template
- **low** -- Generic object copying without a clear prototype/template intent (could be defensive copying)

## Architecture

Look for pre-configured template objects that are cloned to create new instances, avoiding costly construction.

### Review Checklist

- Deep copy vs shallow copy semantics are explicitly chosen and documented
- Mutable nested objects are deep-copied to prevent shared-state bugs
- Prototype registry is initialized with valid, complete template objects
- Clone method maintains class invariants (cloned object is in a valid state)
- Circular references in the object graph are handled during cloning

### Anti-patterns

- Shallow copy of objects with mutable nested state, causing unintended sharing
- Clone method that skips initialization logic required by the class contract
- Using prototype pattern when a simple constructor or factory would suffice
- No prototype registry, requiring callers to manage their own template instances

### Relationship To Other Concepts

- Related to [builder](/concepts/builder) and [factory](/concepts/factory) because all three manage object creation with different tradeoffs.
- Related to [fixture-builder](/concepts/fixture-builder) when reusable object templates are cloned and adjusted in tests.

### Boundary

Use `prototype` when new objects are created by cloning or copying an existing prototype instance rather than building from scratch.

Do not use it for any copy constructor or serializer clone. The key signal is prototype-based creation as the architectural idiom.

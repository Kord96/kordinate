---
description: Leaky Abstraction anti-pattern
type: anti-pattern
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - adapter
  - hexagonal
  - data-mapper
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Leaky Abstraction

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Implementation details in interface signatures (SQL fragments in repository method names, HTTP headers in domain object fields, file paths in service interfaces)
- Callers catching implementation-specific exceptions through abstraction layers (e.g., catching `psycopg2.IntegrityError` when calling a repository method)
- Domain objects containing serialization-specific annotations (JSON tags, ORM column mappings) that tie them to a particular storage or transport mechanism
- Callers needing to know about internal state or call methods in a specific order for the abstraction to work correctly
- "Pass-through" methods that expose every parameter of the underlying implementation

### Confidence

- **high** -- SQL in repository method signatures, infrastructure exceptions leaking through domain boundaries, callers must understand the implementation to use the abstraction correctly
- **medium** -- domain objects carry ORM or serialization annotations, method parameters mirror the underlying library's API 1:1
- **low** -- abstraction works but its naming or structure hints at the implementation behind it (e.g., `RedisCache` instead of `Cache`)

## Impact

The abstraction provides no real isolation, so changes to the underlying implementation ripple through all callers.

### Symptoms

- Swapping the underlying implementation requires changing callers despite the abstraction layer
- Callers contain defensive code that handles quirks of the specific implementation behind the abstraction
- Domain model cannot be understood without knowing the database schema or API format
- Tests for higher layers break when lower-layer implementation details change
- The abstraction's interface grows to mirror the underlying library's full API surface

### Remediation

- Define interfaces in terms of domain concepts, not implementation mechanisms (e.g., `find_active_users()` not `query("SELECT * FROM users WHERE active = true")`)
- Translate implementation-specific exceptions into domain exceptions at the boundary
- Separate domain models from persistence models: map between them at the adapter layer
- Apply the Interface Segregation Principle: expose only what callers need, not everything the implementation can do
- Test the abstraction boundary: verify that callers work with any conforming implementation, not just the current one

### Relationship To Other Concepts

- Related to [adapter](/concepts/adapter) because poor adapters often let underlying implementation details leak through supposedly stable interfaces.
- Related to [hexagonal](/concepts/hexagonal) because ports-and-adapters architectures try to prevent infrastructure details from leaking into the core.
- Related to [data-mapper](/concepts/data-mapper) when mapping layers are used specifically to keep persistence concerns out of domain-facing abstractions.

### Boundary

Use `leaky-abstraction` when an abstraction still forces callers to understand underlying implementation details in order to use it correctly.

Do not use it for abstractions that are merely thin; the issue is hidden detail escaping across the boundary.

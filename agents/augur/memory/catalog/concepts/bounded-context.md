---
description: Bounded Context architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- architectural
- design
status: primary
scope: cross-cutting
relationships:
  related_to:
  - ddd
  - anti-corruption-layer
  - database-per-service
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Bounded Context

## Recognition

How to identify this pattern in code.

### Signatures

- Domain model, language, and invariants clearly scoped to one subsystem or service boundary
- Separate modules or services such as `billing`, `inventory`, or `shipping` with distinct models
- Translation layers between contexts instead of shared internal entities
- Team or service ownership aligned with a domain boundary
- Persistence and API contracts separated by context rather than one global enterprise model

### Confidence

- **high** -- one domain boundary owns its own language, data, APIs, and translation points to neighbors
- **medium** -- domain modules exist with mostly separate models, but some internals still leak across boundaries
- **low** -- folders or namespaces suggest contexts, but one global model still dominates behavior

## Architecture

Look for explicit domain boundaries where terms and models are intentionally local rather than universal.

### Review Checklist

- Context boundaries are documented in code structure or contracts
- Internal entities are not imported directly across contexts
- Translation at boundaries is explicit and owned
- Data ownership follows the context boundary

### Anti-patterns

- One canonical model shared across unrelated business areas
- Cross-context table sharing or direct entity reuse
- Context names exist in folders only, with no behavioral separation

### Relationship To Other Concepts

- Related to [ddd](/concepts/ddd) because bounded contexts are one of the main strategic structures in domain-driven design.
- Related to [anti-corruption-layer](/concepts/anti-corruption-layer) when translation protects one context from another's model.
- Related to [database-per-service](/concepts/database-per-service) when persistence boundaries follow context ownership.

### Boundary

Use `bounded-context` when a domain boundary with its own language and model is architecturally significant on its own.

Do not use it for any module split. The important signal is semantic boundary, not packaging alone.

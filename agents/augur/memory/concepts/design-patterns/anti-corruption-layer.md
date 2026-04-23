---
kind: concept
name: anti-corruption-layer
signatures: {}
type: pattern
abstraction:
- integration
- design
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `*Translator`, `*Mapper`, `*Adapter` classes at integration boundaries
- Separate model/DTO classes for the external system distinct from the internal domain model
- A facade or gateway wrapping an external API that returns internal domain objects
- Package or module named `integration`, `external`, `anticorruption`, or `acl`
- Mapping functions converting between external and internal representations
- External API clients isolated behind an interface the domain depends on

### Confidence

- **high** -- Dedicated translation layer with separate external and internal models, explicit mapper classes, domain never imports external types
- **medium** -- Adapter wrapping an external client that converts responses, but external types occasionally leak into domain code
- **low** -- Direct external API calls with inline field mapping in the service layer, no dedicated translation module

## Architecture

Look for a boundary translation layer that isolates internal domain models from external system models.

### Review Checklist

- External models never appear in internal domain code or interfaces
- Translation logic is centralized in mapper/translator classes, not scattered across services
- The ACL has its own test suite validating mapping correctness
- Changes to the external API require updates only in the ACL, not in domain logic
- Error handling translates external failures into domain-appropriate exceptions
- The ACL defines the interface it exposes to the domain, not the other way around

### Anti-patterns

- External DTOs used directly inside domain logic, coupling the domain to the external system
- Translation logic duplicated across multiple services instead of centralized
- ACL that grows business logic beyond translation (should only translate, not decide)
- No ACL at all -- domain objects mirror the external system's schema one-to-one

See also: adapter (implementation mechanism)

### Relationship To Other Concepts

- Related to [adapter](/concepts/adapter) because adapters are a common implementation technique for an anti-corruption layer, but the ACL is the broader integration boundary pattern.
- Related to [hexagonal](/concepts/hexagonal) when external systems are isolated behind ports and adapters.
- Related to [gateway-backends](/concepts/gateway-backends) when the system hides or reshapes external service behavior behind a controlled integration edge.

### Boundary

Use `anti-corruption-layer` when the important architectural choice is protecting the internal domain model from the vocabulary or schema of an external system.

Do not use it for every mapper or wrapper. A simple adapter becomes an ACL only when it clearly enforces a model boundary between internal and external concepts.

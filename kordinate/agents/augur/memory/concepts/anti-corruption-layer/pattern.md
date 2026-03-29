---
description: Anti-Corruption Layer architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [integration, design]
---
# Anti-Corruption Layer

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

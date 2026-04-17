---
description: Hexagonal architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- architectural
status: primary
scope: cross-cutting
relationships:
  related_to:
  - adapter
  - anti-corruption-layer
  - layered
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# Hexagonal (Ports & Adapters)

## Recognition

How to identify this pattern in code.

### Signatures

- `ports/` and `adapters/` directory structure separating interface definitions from implementations
- Interfaces or protocols with a `Port` suffix (`OrderRepositoryPort`, `NotificationPort`)
- Classes with an `Adapter` suffix implementing port interfaces (`PostgresOrderRepositoryAdapter`)
- Domain layer with no framework imports (no `requests`, `boto3`, `flask`, or DB driver imports)
- Explicit separation of "driving" (inbound) and "driven" (outbound) adapters
- Dependency injection wiring adapters to ports at application startup
- In-memory adapter implementations used in tests as port substitutes

### Confidence

- **high** -- `ports/` and `adapters/` directories with `Port`-suffixed interfaces and `Adapter`-suffixed implementations, domain layer free of infrastructure imports
- **medium** -- Driving/driven adapter separation with dependency injection, but without strict naming conventions
- **low** -- Domain layer isolated from infrastructure by convention, without explicit port interfaces or adapter directory structure

## Architecture

Look for clean separation between domain logic and infrastructure.

### Review Checklist

- Ports are defined as interfaces/protocols, not concrete classes
- Adapters implement exactly one port — no multi-port adapters
- Domain layer has zero imports from infrastructure packages
- Tests use in-memory adapters, not mocks of concrete classes

### Anti-patterns

- Domain code importing `requests`, `boto3`, or DB drivers directly
- "Port" interfaces that leak infrastructure details (SQL, HTTP headers)
- Adapter logic bleeding into domain services

### Relationship To Other Concepts

- Related to [adapter](/concepts/adapter) because adapters sit at the edge of hexagonal systems to connect ports to external technologies.
- Related to [anti-corruption-layer](/concepts/anti-corruption-layer) when external boundaries are translated before reaching the domain core.
- Related to [layered](/concepts/layered) as another structuring approach, though hexagonal emphasizes ports and dependency direction more strongly than simple layers.

### Boundary

Use `hexagonal` when domain logic is intentionally isolated behind ports and infrastructure concerns plug in through adapters at the edges.

Do not use it for any codebase with interfaces or adapters. The key signal is inward dependency flow toward a protected domain core.

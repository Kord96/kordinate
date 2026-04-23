---
kind: concept
name: hexagonal
signatures:
  concept: hexagonal
  positive:
    strong:
    - ports and adapters structure
    - domain layer without infrastructure imports
    medium:
    - RepositoryPort interface
    - PostgresAdapter class
    - dependency injection wiring
    weak:
    - service/repository boundary with some adapter naming
  negative:
  - infrastructure imports inside domain layer
  - route handlers directly using persistence drivers
  notes:
  - Architecture-level concept; broad matches should usually trigger questions.
type: pattern
abstraction:
- architectural
scope: cross-cutting
status: primary
review_questions:
  threshold: 6
  entries:
  - id: hexagonal-ports-adapters-structure
    prompt: Is there a ports/ and adapters/ directory structure with Port-suffixed
      interfaces and Adapter-suffixed implementations?
    weight: 3
    signals:
    - ports/ directory
    - adapters/ directory
    - RepositoryPort interface
    - PostgresAdapter class
  - id: hexagonal-domain-free-of-infra
    prompt: Is the domain layer free of infrastructure imports like HTTP libraries,
      database drivers, or cloud SDKs?
    weight: 3
    signals:
    - no requests import in domain
    - no boto3 in domain
    - no DB driver in domain
  - id: hexagonal-di-wiring
    prompt: Are adapters wired to ports via dependency injection at application startup?
    weight: 2
    signals:
    - inject adapter at startup
    - bind port to adapter
    - DI container wiring
  - id: hexagonal-test-adapters
    prompt: Do tests use in-memory adapter implementations rather than mocking concrete
      infrastructure classes?
    weight: 1
    signals:
    - InMemoryRepository in tests
    - fake adapter for testing
    - test adapter implements port
monitoring:
  applies_to:
  - component
  health_signals:
  - name: adapter.error.rate
    description: Error rate per adapter boundary to expose which edge of the hexagon
      is failing.
  - name: adapter.latency
    description: Latency per port or adapter boundary to surface slow infrastructure
      interactions.
  business_metrics: []
  gaps:
  - If ports and adapters are not measured separately, infrastructure regressions
    look like generic application failures.
family: design-patterns
---

# Explanation

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

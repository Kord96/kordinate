---
description: Hexagonal architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [architectural]
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
- Java: `domain/` + `infrastructure/` or `domain/` + `adapter/` package structure with interfaces in domain, implementations in infrastructure
- Java: `application/` + `domain/` + `infrastructure/` three-layer packaging (Clean Architecture / DDD layering)
- Java: `usecase/` or `interactor/` packages separated from framework code
- Java: Spring `@Repository` interfaces in domain packages, JPA/JDBC implementations in infrastructure packages

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

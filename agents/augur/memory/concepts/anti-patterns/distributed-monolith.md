---
kind: concept
name: distributed-monolith
signatures: {}
type: anti-pattern
abstraction: []
scope: cross-cutting
status: supporting
family: anti-patterns
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Microservices sharing a single database (multiple services with connection strings to the same DB)
- Services that must be deployed together or in a specific order
- Synchronous call chains across 5+ services to complete a single request
- Shared libraries containing business logic imported by multiple services
- No independent deployability (deploying service A breaks service B)
- Distributed transactions or two-phase commit across services
- Shared data models or generated client code tightly coupling service interfaces
- A single CI pipeline that builds and deploys all services together

### Confidence

- **high** -- multiple services share a database schema, require coordinated deployment, and communicate via synchronous chains of 5+ hops
- **medium** -- shared business logic libraries exist, or services cannot be deployed independently without integration test failures
- **low** -- services share a code repository or CI pipeline, or cross-service calls are predominantly synchronous

## Impact

Microservice complexity with monolith coupling, yielding the worst properties of both architectures: network latency, operational overhead, and deployment fragility.

### Symptoms

- Deploying one service requires simultaneously deploying others
- A single service failure cascades across the entire system
- Cross-service debugging requires tracing through many synchronous hops
- Schema changes in the shared database require coordinated updates across teams
- Teams cannot release independently despite having separate services

### Remediation

- Assign each service its own database or schema with clear ownership boundaries
- Replace synchronous call chains with asynchronous messaging (events, message queues)
- Extract shared business logic into each service's codebase (duplication over coupling)
- Establish independent CI/CD pipelines per service with contract tests at boundaries
- Define service boundaries using domain-driven design bounded contexts

### Relationship To Other Concepts

- Related to [microservices](/concepts/microservices) as the negative contrast where the system looks like microservices operationally but retains monolithic coupling.
- Related to [api-gateway](/concepts/api-gateway) because a gateway can hide tightly coupled backend services behind one clean edge without fixing internal coupling.
- Related to [shared-database](/concepts/shared-database) when multiple nominal services are still coupled through one persistence boundary.

### Boundary

Use `distributed-monolith` when the system is split into multiple deployable services but still behaves as one tightly coupled monolith in releases, data ownership, or runtime dependencies.

Do not use it for any service architecture with some coupling. The label should be reserved for materially monolithic coordination costs hiding behind distributed packaging.

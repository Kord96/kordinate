---
description: Distributed Monolith anti-pattern
curated: true
scope: global
preloaded: none
---
# Distributed Monolith

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

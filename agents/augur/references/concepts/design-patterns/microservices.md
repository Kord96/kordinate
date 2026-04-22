---
kind: concept
name: microservices
signatures: {}
source:
  memory_concept: memory/catalog/concepts/microservices.md
type: pattern
abstraction:
- architectural
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Multiple independently deployable services, each with its own Dockerfile or build target
- Service-per-directory repo layout or monorepo with explicit service boundaries (`services/`, `apps/`)
- Separate Kubernetes Deployments, docker-compose services, or serverless stacks per service
- Inter-service communication via HTTP/REST, gRPC, or async messaging (Kafka, RabbitMQ, NATS)
- `docker-compose.yml` with multiple service definitions and internal networking
- Per-service database or schema ownership (no shared tables across services)
- API contracts defined via OpenAPI specs, protobuf definitions, or AsyncAPI schemas

### Confidence

- **high** -- Multiple services with independent Dockerfiles, separate deployments, and inter-service HTTP/gRPC calls
- **medium** -- Monorepo with service directories and shared CI but separate build targets
- **low** -- Multiple entry points in a single repo with some network calls between them

## Architecture

Look for proper service boundaries, independent deployability, and well-defined inter-service contracts.

### Review Checklist

- Each service owns its data store and does not share database tables with other services
- Inter-service communication uses explicit contracts (protobuf, OpenAPI) not ad-hoc HTTP calls
- Services can be deployed, scaled, and rolled back independently
- Failure in one service does not cascade to others (circuit breakers, timeouts, retries in place)
- Service discovery mechanism exists (DNS, service mesh, registry)
- Distributed tracing and correlation IDs propagate across service boundaries

### Anti-patterns

- Shared database across services (distributed monolith disguised as microservices)
- Synchronous call chains spanning three or more services for a single user request
- Services that cannot be deployed without coordinating releases of other services
- No contract testing between services, relying on integration environments to catch breaks

### Relationship To Other Concepts

- Related to [api-gateway](/concepts/api-gateway) because many microservice systems expose a shared ingress layer in front of multiple services.
- Related to [event-driven](/concepts/event-driven) because asynchronous communication is common in microservice systems even though it is not required.
- Related to [distributed-monolith](/concepts/distributed-monolith) as the main negative contrast where service boundaries exist operationally but not organizationally or architecturally.
- Usually prefer this over [distributed-monolith](/concepts/distributed-monolith) only when services are genuinely independently deployable and loosely coupled.

### Boundary

Use `microservices` when the system is intentionally decomposed into independently deployable services with clear ownership and service boundaries.

Do not use it just because multiple services exist. If releases, data ownership, or runtime coupling are still effectively monolithic, prefer [distributed-monolith](/concepts/distributed-monolith).

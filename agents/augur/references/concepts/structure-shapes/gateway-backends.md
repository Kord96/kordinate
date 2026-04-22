---
kind: concept
name: gateway-backends
signatures: {}
source:
  memory_concept: memory/catalog/concepts/gateway-backends.md
type: structure-shape
abstraction:
- architectural
- api
scope: backend
status: primary
---

# Explanation

## Recognition

### Signatures

- API gateway (Kong, AWS API Gateway, Traefik, nginx) routing to multiple services
- BFF (Backend-for-Frontend) pattern: one gateway per client type
- Path-based routing: `/api/users/*` → user service, `/api/orders/*` → order service
- GraphQL gateway federating multiple subgraphs
- Reverse proxy with upstream configuration
- Load balancer distributing to multiple instances of the same service
- Service registry (Consul, Eureka) used by gateway for discovery
- Rate limiting, auth, and logging applied at gateway level
- `docker-compose.yml` with a gateway service and multiple backend services

### Confidence

- **high** — explicit gateway service (nginx/Kong/Traefik) with routing rules to multiple distinct backend services
- **medium** — application-level router dispatching to internal service modules (monolith acting as gateway)
- **low** — multiple services exist but no central entry point (each service exposed directly)

## Architecture

Look for one entry layer dispatching traffic to multiple backend services or subsystems behind it.

### Review Checklist

- The gateway or entry layer is distinct from the backend services it fronts
- Routing rules and upstream ownership are explicit enough to map service boundaries
- Cross-cutting concerns stay near the gateway rather than leaking business logic upward
- Service discovery or upstream selection is visible where it materially affects routing
- The shape reflects a real entrypoint topology, not just a project folder name

### Anti-patterns

- Calling any reverse proxy a gateway-backends structure without multiple meaningful backend targets
- Hiding business logic inside the gateway while still labeling it as pure routing structure
- Treating one monolith with internal modules as gateway-backends unless it really brokers requests across backend boundaries
- Using this structure shape when [api-gateway](/concepts/api-gateway) or [bff](/concepts/bff) would be the more semantically precise concept

### Relationship To Other Concepts

- Related to [api-gateway](/concepts/api-gateway) because gateway-backends is often the structural shape created by an API gateway fronting multiple services.
- Related to [bff](/concepts/bff) when the entry layer is specialized per frontend rather than shared.
- Related to [microservices](/concepts/microservices) when the backend services are independently deployed service boundaries.

### Boundary

Use `gateway-backends` when the important observation is the structural topology of one entry layer routing to multiple backend services.

Do not use it when you can identify a more specific semantic pattern such as [api-gateway](/concepts/api-gateway) or [bff](/concepts/bff). This concept is primarily a structure shape.

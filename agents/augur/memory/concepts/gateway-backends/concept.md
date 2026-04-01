---
description: Gateway-backends structure — single entry point routing to multiple backend services
type: structure-shape
abstraction: [architectural, api]
---
# Gateway-Backends

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

---
kind: concept
name: bff
signatures: {}
source:
  memory_concept: memory/catalog/concepts/bff.md
type: pattern
abstraction:
- api
- architectural
scope: backend
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Separate API layers per frontend type: `/api/mobile/*`, `/api/web/*`, `/api/admin/*`
- Distinct services or modules named `mobile-bff`, `web-bff`, `admin-gateway`
- Response shaping logic tailored to specific frontend needs (mobile gets compact payloads, web gets richer data)
- Aggregation of multiple microservice calls into a single frontend-optimized response
- Frontend-specific authentication flows (cookie-based for web, token-based for mobile)
- Different API versioning or deprecation timelines per frontend

### Confidence

- **high** -- separate deployable services per frontend type, each aggregating calls to shared backend microservices
- **medium** -- single API with frontend-specific routes or middleware that shape responses differently per client type
- **low** -- `User-Agent` based response variation or a single monolithic API serving all frontends

## Architecture

Look for a dedicated API aggregation layer per frontend with clear separation of frontend-specific concerns from shared backend services.

### Review Checklist

- Each BFF is owned by the frontend team that consumes it
- BFF contains only aggregation and response shaping logic, not business rules
- Shared business logic lives in backend services, not duplicated across BFFs
- Each BFF has independent deployment and scaling from other BFFs
- Authentication and session management are appropriate for each frontend's platform constraints

### Anti-patterns

- Putting business logic in the BFF instead of shared backend services (logic duplication)
- Single BFF serving all frontends (defeats the purpose, becomes a generic API gateway)
- BFF-to-BFF calls (BFFs should only call downstream services, never each other)
- Frontend teams blocked by a shared BFF team (BFF should be frontend-team owned)

### Relationship To Other Concepts

- Related to [api-gateway](/concepts/api-gateway) because both broker frontend traffic, but a BFF is optimized for one frontend or client experience rather than shared ingress infrastructure.
- Related to [component](/concepts/component) because BFFs often exist to serve distinct UI surfaces or applications.
- Related to [rest](/concepts/rest) because many BFFs expose resource-oriented HTTP APIs while aggregating downstream calls.

### Boundary

Use `bff` when a backend layer exists specifically to serve one frontend or client experience with tailored aggregation and response shaping.

Do not use it for generic API layers, shared ingress proxies, or ordinary microservices that are not organized around a frontend boundary.

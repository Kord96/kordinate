---
description: Backend for Frontend architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Backend for Frontend

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

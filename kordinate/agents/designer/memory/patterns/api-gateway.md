# API Gateway


## Architecture

Look for the gateway being a thin routing/policy layer with no business logic.

### Review Checklist

- Gateway handles cross-cutting concerns only: auth, rate limiting, routing
- No business logic in the gateway — it delegates to backend services
- Timeouts and circuit breakers configured for each upstream backend
- Request/response transformation is minimal and well-documented
- Gateway failure mode is defined (fail open vs. fail closed)

### Anti-patterns

- Business logic creeping into the gateway (becomes a monolith bottleneck)
- Gateway as single point of failure with no redundancy or health checks
- Tight coupling between gateway routing rules and backend implementation details

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO

---
description: God Endpoint anti-pattern
type: anti-pattern
graphable: false
---
# God Endpoint

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Single API route handling multiple unrelated operations via an `action` or `type` parameter
- URLs like `POST /api?action=createUser&action=sendEmail` or `POST /rpc` with an operation field in the body
- Large switch/case or if-else chain on an operation type inside one handler function
- One endpoint accepting wildly different request/response shapes depending on the action
- API documentation for a single route that spans multiple pages covering unrelated operations

### Confidence

- **high** -- a single handler function dispatches to 5+ unrelated operations based on a string parameter, each with different input/output schemas
- **medium** -- one endpoint handles 3+ distinct operations via a type/action field with a switch statement
- **low** -- an endpoint has 2 operation modes with some shared logic but growing toward more

## Impact

Impossible to document, cache, rate-limit, or evolve operations independently because they share a single undifferentiated route.

### Symptoms

- API documentation is confusing because one endpoint does many unrelated things
- HTTP caching is impossible since the same URL returns different data based on the request body
- Rate limiting cannot be applied per-operation because all operations share the same route
- Authorization checks become a tangled mess of per-action permission logic inside one handler
- Monitoring and alerting cannot distinguish between healthy and failing operations since they share one metric

### Remediation

- Split each operation into its own endpoint with a distinct URL path and HTTP method
- Use RESTful resource-based URLs or well-defined RPC service methods with separate routes
- Apply the Single Responsibility Principle at the endpoint level: one route, one operation
- Implement a lightweight router or controller layer that maps actions to dedicated handler functions
- Migrate incrementally by adding new dedicated endpoints and deprecating the god endpoint with a compatibility shim

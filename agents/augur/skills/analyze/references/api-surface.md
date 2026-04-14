# API Surface

Use this reference when the project exposes HTTP, GraphQL, gRPC, WebSocket, or SSE interfaces.

## Capture

- endpoint or operation id
- method or operation type
- path or service/method name
- handler location
- auth posture
- validation posture

## Watch For

- handlers doing database work directly
- handlers orchestrating business logic inline
- inconsistent auth models
- missing validation at the boundary
- missing shared error handling

API adapters should delegate to domain or service layers rather than own business rules.

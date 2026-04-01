---
description: Hexagonal — testing guidance
---
## Testing

Verify that domain logic is fully decoupled from infrastructure by testing ports and adapters independently.

### Unit Tests

- Test domain services using in-memory adapter stubs — assert business rules without any infrastructure
- Verify that port interfaces reject invalid inputs at the boundary (e.g., malformed DTOs never reach domain)
- Assert that domain layer compiles and passes tests with zero infrastructure imports
- Test adapter output mapping — confirm adapters translate domain objects to infrastructure formats correctly

### Integration Tests

- Test each adapter against its real infrastructure target (actual DB, HTTP endpoint, message broker)
- Verify that swapping one adapter for another (e.g., Postgres to SQLite) produces identical domain behavior
- Test the full request path from inbound adapter through domain to outbound adapter

### Failure Injection

- Simulate outbound adapter failure (DB down, API timeout) and verify domain layer receives a port-defined error, not an infrastructure exception
- Kill an infrastructure dependency mid-operation and confirm the domain transaction rolls back cleanly
- Introduce latency in an adapter and verify domain-level timeouts trigger correctly

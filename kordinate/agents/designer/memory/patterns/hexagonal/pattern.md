---
description: Hexagonal architectural pattern
curated: true
scope: global
preloaded: none
---
# Hexagonal (Ports & Adapters)


## Architecture

Look for clean separation between domain logic and infrastructure.

### Review Checklist

- Ports are defined as interfaces/protocols, not concrete classes
- Adapters implement exactly one port — no multi-port adapters
- Domain layer has zero imports from infrastructure packages
- Tests use in-memory adapters, not mocks of concrete classes

### Anti-patterns

- Domain code importing `requests`, `boto3`, or DB drivers directly
- "Port" interfaces that leak infrastructure details (SQL, HTTP headers)
- Adapter logic bleeding into domain services

## Monitoring

Track port and adapter health to catch infrastructure failures before they leak into the domain.

### Key Metrics

- `adapter_call_duration_seconds` (histogram) — latency per adapter, broken down by port
- `adapter_errors_total` (counter) — failures per adapter (connection errors, timeouts)
- `domain_call_total` (counter) — domain service invocations vs adapter invocations (ratio check)
- `adapter_health` (gauge) — availability state per adapter (1=healthy, 0=degraded)

### Alerts

- Adapter error rate exceeding threshold for any single port
- Domain-to-adapter call ratio inversion (infra calls dominating domain calls)
- Adapter latency p99 exceeding SLA for a sustained period

## Deployment

Adapter swaps during rollout can break port contracts if old and new adapters behave differently.

### Rollout Implications

- Rolling updates may run old and new adapter implementations simultaneously — ensure both satisfy the same port interface version
- Swapping an adapter (e.g., switching from REST to gRPC for a port) should be a separate deployment from business logic changes
- If adapter configuration is injected at startup, verify new config is available before rolling new pods
- Database adapters with schema changes require migration to complete before the new adapter version rolls out

### Pre-deploy Checklist

- Verify port interface version compatibility between outgoing and incoming adapter implementations
- Run integration tests with the new adapter against a staging instance of the external dependency
- Confirm adapter configuration (connection strings, timeouts) is present in the target environment

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

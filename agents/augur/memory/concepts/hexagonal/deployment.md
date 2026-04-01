---
description: Hexagonal — deployment guidance
---
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

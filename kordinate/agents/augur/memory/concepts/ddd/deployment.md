---
description: Domain-Driven Design — deployment guidance
curated: true
scope: global
preloaded: none
---
## Deployment

Bounded context boundaries and aggregate schema changes require careful coordination during rollouts.

### Rollout Implications

- Aggregate schema changes need database migrations applied before new code rolls out — never deploy code expecting a schema that does not yet exist
- Deploying a bounded context that emits new domain events requires downstream consumers to handle unknown event fields gracefully
- Anti-corruption layer changes must be backward-compatible — old and new versions of the ACL may run simultaneously during rollout
- Shared-nothing contexts can deploy independently, but contexts with synchronous dependencies need ordered rollouts

### Pre-deploy Checklist

- Verify database migrations for aggregate schema changes are applied and backward-compatible
- Confirm downstream bounded contexts can tolerate new or changed domain events
- Check that anti-corruption layer translations handle both old and new upstream formats

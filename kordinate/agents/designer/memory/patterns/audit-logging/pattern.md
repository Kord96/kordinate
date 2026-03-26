---
description: Audit Logging architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
---
# Audit Logging

## Recognition

How to identify this pattern in code.

### Signatures

- `AuditLog` model, table, or collection storing who-did-what-when
- Fields: `actor`, `action`, `target`, `timestamp` (and optionally `before`/`after` state)
- Audit middleware intercepting requests or database operations
- `@audited` or `@audit_log` decorators on endpoints or service methods
- Append-only write pattern -- no UPDATE or DELETE on the audit table
- Compliance logging for regulatory requirements (SOC2, HIPAA, GDPR)
- Separate audit storage or write-ahead log distinct from application logs

### Confidence

- **high** -- dedicated audit table with actor/action/target/timestamp fields and append-only writes
- **medium** -- structured logging of user actions but stored in general application logs, not a dedicated audit trail
- **low** -- `logger.info` calls that include user and action but no structured schema or immutability guarantee

## Architecture

Look for an immutable, structured record of every significant action with actor attribution.

### Review Checklist

- Audit records are append-only -- no mechanism to update or delete entries
- Every state-changing operation is captured with actor, action, target, and timestamp
- Audit log is stored separately or with different retention than application logs
- Sensitive fields are redacted or masked in audit records
- Audit writes do not block the primary operation (async or fire-and-forget with delivery guarantee)
- Tamper detection is in place (checksums, hash chains, or write-once storage)

### Anti-patterns

- Audit records stored in the same mutable table as application data
- Missing actor attribution -- logs show what happened but not who did it
- Audit writes in the critical path causing latency on every user action
- No retention policy -- audit data grows unbounded without archival or rotation

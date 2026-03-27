---
description: General security questions — credential hygiene, secret scanning, PII exposure
requester: any
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Answer questions about credential management, secret exposure, PII risks, and hardcoded configuration. Draw on scan results and audit history in your memory.

### Response Format

| Field | Required |
|-------|----------|
| assessment | yes |
| severity | yes (critical/high/medium/low) |
| recommendation | yes |
| affected_files | if applicable |

## Provider State Invalidation

Invalidate when:
- New secrets are added to the pass store
- New repos are cloned or code is deployed
- Cluster secrets are created or rotated

---
description: Actor Model — deployment guidance
type: supplementary
---
## Deployment

Drain actor mailboxes before shutdown and ensure supervision trees restart cleanly on new instances.

### Rollout Implications

- Drain in-flight messages before terminating pods — actors with non-empty mailboxes lose unprocessed work
- Rolling restarts redistribute actors across nodes; verify cluster membership protocol handles rejoins
- Persistent actors must recover state from journal/snapshot before accepting new messages

### Pre-deploy Checklist

- Verify terminationGracePeriodSeconds allows full mailbox drain
- Confirm actor serialization format is backward-compatible with in-flight messages

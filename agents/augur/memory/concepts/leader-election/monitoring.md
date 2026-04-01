---
description: Leader Election — monitoring guidance
type: supplementary
---
## Monitoring

Track leader identity, lease health, and election frequency to detect split-brain or stale leaders.

### Key Metrics

- `leader_identity` (info gauge) — current leader node identity, exposed as a label
- `leader_lease_renewals_total` (counter) — successful lease renewals by the current leader
- `leader_elections_total` (counter) — number of election events (should be rare in steady state)
- `leader_lease_ttl_remaining_seconds` (gauge) — time until the current lease expires

### Alerts

- No leader detected for longer than the lease TTL (election stuck or all candidates down)
- Frequent re-elections (flapping leadership indicating network instability)
- Two nodes reporting leader status simultaneously (split-brain, fencing failure)
- Lease renewal failures approaching TTL expiry (leader about to lose leadership)

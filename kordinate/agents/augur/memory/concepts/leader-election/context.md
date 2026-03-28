## Testing

Verify correct election, fencing, and failover behavior under normal and partitioned conditions.

### Unit Tests

- Start multiple candidates and assert exactly one wins the election
- Verify that the leader renews its lease and followers do not attempt to take over while the lease is valid
- Assert that fencing tokens or epoch numbers increment on each new election

### Integration Tests

- Kill the leader process and verify a follower wins the new election within the expected TTL window
- Simulate a network partition between leader and the coordination store and confirm the leader steps down after lease expiry
- Restore the partition and verify the old leader does not reclaim leadership using a stale fencing token

### Failure Injection

- Introduce clock skew between nodes and verify the election protocol still produces a single leader
- Simulate a slow leader that cannot renew its lease in time and confirm followers take over cleanly

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

## Deployment

Coordinate rollouts with leader lease lifecycle to avoid split-brain or prolonged leaderless windows.

### Rollout Implications

- Rolling updates should terminate the leader pod last to minimize unnecessary re-elections
- New pods must be able to participate in elections before old pods are terminated (readiness-gated)
- If the leader pod is killed mid-lease, followers should detect the expired lease and elect a new leader within the TTL
- Avoid deploying all replicas simultaneously -- staggered rollout prevents a leaderless gap

### Pre-deploy Checklist

- Verify the lease TTL is shorter than the deployment's pod termination grace period
- Confirm the leader releases its lease on graceful shutdown (preStop hook or signal handler)
- Test that a new version can win elections against the old version without protocol incompatibility


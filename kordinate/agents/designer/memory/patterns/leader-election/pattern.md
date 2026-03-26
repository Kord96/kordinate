---
description: Leader Election architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Leader Election

## Recognition

How to identify this pattern in code.

### Signatures

- Leader/follower role assignment logic with election protocol
- K8s `Lease` objects used for leader election (`coordination.k8s.io/v1` API)
- etcd-based election using key TTL and compare-and-swap
- ZooKeeper sequential ephemeral nodes for election recipes
- Only-leader-writes pattern (followers redirect or reject write operations)
- Leader health monitoring with automatic re-election on failure
- Libraries: `client-go/tools/leaderelection`, `curator` (ZooKeeper), `etcd/clientv3/concurrency`

### Confidence

- **high** -- explicit leader election protocol with Lease/lock objects, leader-only execution paths, and automatic failover
- **medium** -- single-writer pattern with a lock mechanism but no formal election protocol or follower behavior
- **low** -- application runs as a single replica to avoid concurrency (implicit leader by deployment constraint)

## Architecture

Look for a correct election protocol with leader fencing and graceful failover to a follower on leader loss.

### Review Checklist

- Leader lease has a TTL and is renewed periodically (stale leaders are detected)
- Fencing tokens or epoch numbers prevent split-brain (old leader cannot act after losing leadership)
- Followers detect leader failure and trigger re-election within an acceptable time window
- Leader performs graceful handoff when shutting down (releases lease proactively)
- Election state is observable (metrics or logs indicating current leader identity and transitions)

### Anti-patterns

- No fencing mechanism allowing two nodes to believe they are leader simultaneously (split-brain)
- Leader lease TTL too long (slow failover) or too short (frequent unnecessary re-elections)
- Business logic assumes leader identity is permanent (no handling of leadership loss mid-operation)
- Using a single replica instead of proper election (no fault tolerance)

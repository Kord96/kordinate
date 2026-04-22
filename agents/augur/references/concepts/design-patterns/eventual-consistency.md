---
kind: concept
name: eventual-consistency
signatures: {}
source:
  memory_concept: memory/catalog/concepts/eventual-consistency.md
type: pattern
abstraction:
- data
- integration
- resilience
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Writes acknowledged before every downstream projection, cache, or subscriber reflects the change
- Read models, search indexes, caches, or replicas updating asynchronously
- Reconciliation, retry, or replay processes closing consistency gaps over time
- Product behavior tolerating stale reads or delayed visibility
- Outbox, CDC, event-driven projections, or async replication connecting write and read paths

### Confidence

- **high** -- architecture explicitly accepts temporary divergence between authoritative write state and downstream views
- **medium** -- asynchronous projections or cache refresh paths exist, but tolerated inconsistency windows are only implicit
- **low** -- background jobs create occasional lag without architectural acknowledgement of consistency tradeoffs

## Architecture

Look for deliberate acceptance of temporary inconsistency as a tradeoff for autonomy, scale, or availability.

### Review Checklist

- Source of truth is explicit
- Lagging projections or replicas are observable
- Product and API semantics account for stale or delayed reads
- Reconciliation exists for dropped or delayed updates

### Anti-patterns

- Claiming strong consistency while relying on async propagation
- No visibility into replication lag or projection backlog
- Business workflows assuming immediate read-after-write where the architecture cannot guarantee it

### Relationship To Other Concepts

- Related to [dual-writes](/concepts/dual-writes) because eventual consistency is often the tradeoff accepted when state propagates asynchronously.
- Related to [cqrs](/concepts/cqrs) when read models intentionally lag behind the write model.
- Related to [optimistic-update](/concepts/optimistic-update) when clients temporarily assume success ahead of authoritative confirmation.

### Boundary

Use `eventual-consistency` when temporary divergence between the source of truth and derived state is an intentional architectural property.

Do not use it for any background job or cache. The key signal is explicit tolerance for delayed convergence.

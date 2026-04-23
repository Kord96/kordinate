---
kind: concept
name: cell-based
signatures: {}
type: structure-shape
abstraction:
- architectural
- deployment
scope: cross-cutting
status: primary
family: structure-shapes
---

# Explanation

## Recognition

### Signatures

- Multiple identical deployments serving different customer segments or regions
- Shard-nothing architecture: each cell has its own database, cache, and queue
- Cell routing: requests routed to the correct cell by tenant ID, region, or hash
- Blast radius isolation: failure in one cell doesn't affect others
- Independent deployment: cells can be updated one at a time (canary per cell)
- Cell-level configuration: each cell can have different feature flags or limits
- AWS Cell-Based Architecture patterns or similar cloud-native cell designs
- `cell_id` or `shard_id` in routing logic and configuration

### Confidence

- **high** — explicit cell architecture with independent data stores, cell routing, and independent deployment
- **medium** — multi-region deployment with region-specific resources but shared control plane
- **low** — sharded database with application-level routing but shared application tier

### Relationship To Other Concepts

- Related to [sharding](/concepts/sharding) because cell-based systems often partition tenants or traffic into independently operated slices.
- Related to [tenant-isolation](/concepts/tenant-isolation) because cells are one operational way to contain blast radius across customer or regional boundaries.
- Related to [canary](/concepts/canary) because independent cells make staged rollout and failure containment easier.

### Boundary

Use `cell-based` when the system is intentionally partitioned into mostly self-sufficient cells that can route, scale, deploy, and fail independently.

Do not use it for ordinary horizontal scaling or regional replicas that still depend on one shared control or data plane.

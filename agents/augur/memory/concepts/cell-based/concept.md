---
description: Cell-based structure — independent cells that can scale, deploy, and fail independently
type: structure-shape
abstraction: [architectural, deployment]
---
# Cell-Based

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

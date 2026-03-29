---
description: Spatial Partitioning — testing guidance
type: supplementary
---
# Testing

- Test insert, query, and remove operations with objects at partition boundaries and overlapping cells
- Verify range and radius queries return all candidates within the search area (no false negatives)
- Test degenerate cases: all objects at the same position, objects at extreme coordinates
- Benchmark query performance against a brute-force O(n^2) baseline to confirm the structure provides speedup
- Test incremental updates when objects move — verify the structure stays correct without full rebuild
- Assert bounded tree depth or cell count to prevent degenerate performance on clustered data
- Test memory allocation: verify no per-frame heap churn in hot paths (object pools, pre-allocated nodes)
- Verify that the query interface returns broad-phase candidates, not narrow-phase final results

---
description: MapReduce architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
---
# MapReduce

## Recognition

How to identify this pattern in code.

### Signatures

- Parallel map phase followed by a reduce/aggregate phase
- `map()` and `reduce()` applied over distributed or partitioned data
- Hadoop-style jobs with Mapper and Reducer classes
- Spark RDDs, `groupByKey()`, `reduceByKey()`, `aggregateByKey()`
- Batch computation frameworks splitting work into map and combine steps
- Shuffle/sort phase between map and reduce
- Partitioned input data with parallel worker execution

### Confidence

- **high** -- Explicit MapReduce job definition with separate Mapper and Reducer implementations, or Spark transformations ending in an action
- **medium** -- Data partitioned across workers with a map phase followed by aggregation, even without framework-specific APIs
- **low** -- A `map()` followed by `reduce()` on local data without distribution or parallelism

## Architecture

Look for correct data partitioning, idempotent map functions, and an associative/commutative reduce operation.

### Review Checklist

- Map function is pure and stateless -- same input always produces the same intermediate key-value pairs
- Reduce function is associative and commutative where required (combiner correctness)
- Data partitioning strategy avoids skew (no single reducer overwhelmed by a hot key)
- Intermediate data (shuffle) has bounded size or spill-to-disk strategy
- Job is idempotent -- re-running produces identical results
- Failure of individual map or reduce tasks triggers retry, not full job restart

### Anti-patterns

- Stateful map functions that depend on processing order or accumulate cross-record state
- All data funneled to a single reducer (defeats parallelism)
- No combiner when one is possible (unnecessary shuffle volume)
- Reduce logic that is not associative, producing different results depending on partition grouping

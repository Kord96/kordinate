---
kind: concept
name: bloom-filter
signatures: {}
type: pattern
abstraction:
- data
scope: domain
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Probabilistic membership test: `add()` and `might_contain()` (or `__contains__` returning possible matches)
- Multiple independent hash functions applied to the same element
- Underlying bit array (bitset) with fixed size
- False positive rate configuration parameter (e.g., `error_rate=0.01`)
- No delete or remove support (standard Bloom filter)
- Libraries: `pybloom`, `pybloomfilter`, `bloom-filter` (Node), Guava `BloomFilter` (Java)
- Redis `BF.ADD`, `BF.EXISTS` commands (RedisBloom module)
- Counting Bloom filter variant with decrement support

### Confidence

- **high** -- Bit array with multiple hash functions, explicit false positive rate, and no deletion
- **medium** -- Probabilistic set membership check with configurable accuracy but unclear internals
- **low** -- Hash-based lookup with possible false positives that may be a Bloom filter

## Architecture

Look for correct probabilistic semantics where false positives are acceptable but false negatives are not.

### Review Checklist

- False positive rate is configured based on expected element count and acceptable error margin
- Bit array size and hash function count are derived from the target false positive rate
- No code path assumes `might_contain()` means "definitely contains"
- Filter is sized for the expected dataset -- undersized filters degrade to near-100% false positive rate
- Membership checks that return true are followed by a definitive lookup (database, cache)
- Filter is not used where deletion is required (use counting Bloom filter or cuckoo filter instead)

### Anti-patterns

- Treating a Bloom filter positive as a definitive answer without secondary verification
- Undersizing the filter for the dataset, causing unacceptable false positive rates
- Attempting to remove elements from a standard (non-counting) Bloom filter
- Using a Bloom filter where exact membership is required (correctness over performance)

### Relationship To Other Concepts

- Related to [search-index](/concepts/search-index) because Bloom filters are often used to cheaply avoid expensive downstream lookups before index or storage access.
- Related to [cache-aside](/concepts/cache-aside) when approximate membership helps skip cache-miss amplification or pointless cache checks.
- Related to [sharding](/concepts/sharding) when approximate membership or routing hints reduce unnecessary shard probes.

### Boundary

Use `bloom-filter` when the system uses probabilistic set membership to cheaply reject definitely-absent items before doing more expensive work.

Do not use it for any hashing or bitset structure. The important signal is probabilistic membership with false positives but no false negatives.

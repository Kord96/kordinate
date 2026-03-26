---
description: Trie (Prefix Tree) — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test insert, search, and `starts_with` for exact matches, prefix matches, and missing keys
- Verify terminal markers: `search("app")` must return false when only `"apple"` was inserted
- Test deletion: removing a key that is a prefix of other keys must not affect the longer keys
- Test with empty strings, single-character keys, and very long keys
- Verify that shared prefixes are stored efficiently (not duplicated at every node)
- Test concurrent access if the trie is shared across threads (read/write safety)
- Benchmark against a hash set for the target workload to confirm the trie provides a real benefit
- Test compressed variants (radix, Patricia) with keys that share long prefixes

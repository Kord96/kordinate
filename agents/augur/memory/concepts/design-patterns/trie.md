---
kind: concept
name: trie
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

- Node-per-character tree structure with children stored in a dict or fixed-size array
- `insert()`, `search()`, `starts_with()` (or `has_prefix()`) methods
- `TrieNode` class with a `children` mapping and an `is_end` / `is_terminal` flag
- Autocomplete or typeahead search implementations
- IP routing table or CIDR prefix matching (bitwise trie)
- Prefix-based filtering or longest-prefix-match logic
- `pygtrie`, `datrie` (Python), `trie-memoize` (Node), Apache Commons `PatriciaTrie` (Java)
- Compressed variants: radix tree, Patricia trie, PATRICIA

### Confidence

- **high** -- Node-per-character tree with `insert`/`search`/`starts_with` and terminal markers
- **medium** -- Prefix matching logic with tree traversal but no explicit `TrieNode` class
- **low** -- Nested dictionary structure used for prefix lookups that may be a trie

## Architecture

Look for correct prefix-based operations with efficient shared-prefix storage.

### Review Checklist

- Each node stores only the branching structure, not full copies of keys
- Terminal/end-of-word markers correctly distinguish complete keys from prefixes
- Memory usage is considered -- standard tries can be sparse; compression (radix) is used when appropriate
- Deletion correctly handles non-leaf nodes that are prefixes of other keys
- Character set is bounded and known (alphabet size affects node children storage choice)
- Thread safety is addressed if the trie is accessed concurrently

### Anti-patterns

- Storing full keys at every node instead of leveraging shared prefixes
- Missing terminal markers -- `search("app")` incorrectly returns true when only `"apple"` was inserted
- Using a standard trie for large alphabets without compression (excessive memory waste)
- Implementing deletion by simply unsetting the terminal flag without pruning orphaned branches

### Relationship To Other Concepts

- Related to [search-index](/concepts/search-index) because tries are often used as efficient prefix indexes for autocomplete or term lookup.
- Related to [key-value-model](/concepts/key-value-model) because trie structures can act as a specialized key lookup model optimized for shared prefixes.
- Related to [lexer-parser](/concepts/lexer-parser) when prefix trees are used for keyword recognition or token matching.

### Boundary

Use `trie` when keys are organized in a prefix tree so lookups and prefix queries share common path structure.

Do not use it for generic trees, maps, or any text index that does not rely on explicit prefix sharing.

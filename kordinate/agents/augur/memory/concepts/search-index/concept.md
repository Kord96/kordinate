---
description: Search and inverted index pattern for full-text retrieval
type: domain-model
abstraction: [data, search]
---
# Search Index

## Recognition

How to identify this pattern in code.

### Signatures

- Elasticsearch client usage: `Elasticsearch()`, `client.index()`, `client.search()`, index mappings
- Solr configuration: `solrconfig.xml`, `schema.xml`, `SolrClient` or `SolrQuery` usage
- Meilisearch client: `meilisearch`, `client.index('...')`, `search()` calls
- Typesense client: `typesense`, collection schema definitions, `search_parameters`
- Python: `whoosh.index`, `tantivy` bindings, `haystack` search backend
- JS/TS: `@elastic/elasticsearch`, `meilisearch`, `typesense` package imports
- Go: `bleve` index creation, `olivere/elastic` client, `tantivy-go` bindings
- Rust: `tantivy::Index`, `tantivy::schema::Schema`, `IndexWriter` and `IndexReader`
- `analyzer`, `tokenizer`, `filter` configuration in index settings
- `inverted_index`, `index_name`, `mapping`, `field_type: text` declarations

### Confidence

- **high** -- Elasticsearch/Solr/Meilisearch client with index mappings, analyzers, and search queries with relevance scoring
- **medium** -- Tantivy or Whoosh index with custom tokenizers and full-text query parsing
- **low** -- SQL `LIKE '%term%'` queries or basic `tsvector` usage without dedicated search infrastructure

## Architecture

### When to use
- Full-text search across large document collections with relevance ranking
- Faceted navigation and filtering (e-commerce, catalogs, content platforms)
- Autocomplete, typeahead, and fuzzy matching requirements

### Anti-patterns
- Using the search index as the primary data store instead of syncing from a source of truth
- Not handling index lag — search results may be stale relative to the primary database
- Over-indexing every field, leading to bloated indices and slow write throughput

### Complements
- [cqrs](/concepts/cqrs) — search index often serves as the read model in a CQRS architecture
- [change-data-capture](/concepts/change-data-capture) — CDC feeds keep search indices in sync with the primary store
- [pagination](/concepts/pagination) — search results require cursor or offset-based pagination

## Impact

Search indices introduce an eventually-consistent read path that must be kept in sync with the authoritative data store. Monitoring must track index lag, query latency percentiles, and indexing throughput to ensure search quality does not degrade silently.

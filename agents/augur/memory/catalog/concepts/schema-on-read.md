---
description: Schema-on-Read anti-pattern
type: anti-pattern
testable: true
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - input-validation
  - stringly-typed
  - insecure-deserialization
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Schema-on-Read

## Recognition

How to identify this anti-pattern in code.

### Signatures

- JSON blobs stored in database columns without a defined schema
- `data["field"]` or `data.get("field")` access patterns with no prior validation
- `JSONB` columns accessed with string keys scattered throughout the codebase
- No Pydantic model, dataclass, or TypedDict used to deserialize JSON data
- `**kwargs` or `dict` passed through multiple layers without type narrowing
- API responses consumed as raw dicts without schema validation
- Configuration loaded from JSON/YAML and accessed with string keys directly
- Migration-free schema changes: new fields added to JSON blobs with no versioning

### Confidence

- **high** -- `JSONB` or `JSON` columns accessed via string keys in 10+ locations with no validation model, and `KeyError` exceptions in production logs
- **medium** -- JSON data consumed as raw dicts without Pydantic/dataclass deserialization, but no production errors yet
- **low** -- a few `data["key"]` accesses without validation, or dynamic config loaded from JSON without a schema

## Impact

Runtime KeyError exceptions, no type safety at boundaries, and schema drift as producers and consumers evolve independently.

### Symptoms

- `KeyError` or `TypeError` exceptions in production when accessing JSON fields
- Developers must read database contents to understand the structure of stored data
- Different parts of the codebase assume different shapes for the same JSON data
- Adding a new field requires searching all consumers to update their access patterns
- No IDE autocompletion or type checking for data extracted from JSON columns

### Remediation

- Define Pydantic models, dataclasses, or TypedDicts for all JSON structures at system boundaries
- Validate JSON data on read from the database or API, rejecting or defaulting missing fields
- Use JSON Schema or OpenAPI specifications to document and enforce the expected shape
- Add migration scripts or versioning when the JSON schema evolves
- Replace string-key access with typed attribute access through validated models

### Relationship To Other Concepts

- Related to [input-validation](/concepts/input-validation) because schema-on-read problems are often mitigated by validating payloads when they cross boundaries.
- Related to [stringly-typed](/concepts/stringly-typed) when untyped JSON or dict access becomes the only effective schema.
- Related to [insecure-deserialization](/concepts/insecure-deserialization) because unvalidated dynamic payload interpretation increases safety and correctness risks at read time.

### Boundary

Use `schema-on-read` when structure is deferred until consumption time, leaving many readers to reinterpret loosely typed data independently.

Do not use it for all flexible schemas or document stores; the issue is repeated late binding with weak shared validation.

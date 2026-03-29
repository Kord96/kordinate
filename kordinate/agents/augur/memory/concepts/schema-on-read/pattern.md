---
description: Schema-on-Read anti-pattern
type: anti-pattern
testable: true
graphable: false
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

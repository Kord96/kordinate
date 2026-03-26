---
description: Input Validation architectural pattern
curated: true
scope: global
preloaded: none
---
# Input Validation

## Recognition

How to identify this pattern in code.

### Signatures

- Schema validation at the API boundary before business logic executes
- `pydantic` BaseModel with field validators (Python)
- `joi` or `zod` schemas (JavaScript/TypeScript)
- `@Valid` or `@Validated` annotations (Java/Spring)
- `marshmallow` or `cerberus` schema definitions (Python)
- Request validation middleware in the HTTP pipeline
- HTML input sanitization (DOMPurify, bleach)
- SQL parameterized queries (`?` placeholders, `$1` bind parameters)

### Confidence

- **high** -- dedicated validation schemas on all API endpoints with reject-on-invalid behavior
- **medium** -- validation present on some endpoints but inconsistent coverage across the API surface
- **low** -- inline type checks or assertions scattered through business logic instead of boundary validation

## Architecture

Look for validation enforced at system boundaries with reject-early semantics.

### Review Checklist

- All external input is validated at the API boundary before reaching business logic
- Validation schemas are declarative and co-located with the endpoint definition
- Error responses include specific field-level validation messages
- String inputs are sanitized for injection (SQL, XSS, command injection)
- Numeric and collection inputs have bounds (min/max, max length)
- Validation logic is not duplicated between client and server -- server is authoritative

### Anti-patterns

- Validation scattered deep in business logic instead of at the boundary
- Trusting client-side validation as the only check
- Generic "invalid input" errors with no indication of which field or why
- String concatenation for SQL or shell commands instead of parameterization

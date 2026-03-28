---
description: Input Validation architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [security, api]
---
# Input Validation

## Recognition

How to identify this pattern in code.

### Signatures

- Schema validation at the API boundary before business logic executes
- `pydantic` BaseModel with field validators (Python)
- `joi` or `zod` schemas (JavaScript/TypeScript)
- `@Valid` or `@Validated` annotations on controller method parameters (Java/Spring)
- `marshmallow` or `cerberus` schema definitions (Python)
- Request validation middleware in the HTTP pipeline
- HTML input sanitization (DOMPurify, bleach)
- SQL parameterized queries (`?` placeholders, `$1` bind parameters)
- Java: `jakarta.validation` / `javax.validation` constraint annotations (`@NotNull`, `@Size`, `@Pattern`)
- Go: `go-playground/validator`, `ozzo-validation` libraries

### Negative signals (not sufficient for detection)

- The word `validate` alone is NOT input validation. Many contexts use validation without API-boundary concerns: schema validation in tests, data integrity checks in domain logic, assertion helpers, config validation at startup.
- `Validator` as a test or spec helper (e.g., Spock `Validator`, JUnit assertion helpers) is testing infrastructure, not the input-validation pattern.
- Internal consistency checks (`validateState()`, `assertValid()`) within domain objects are invariant enforcement, not API input validation.
- Go `validate` struct tags without an HTTP handler context may be domain validation, not the boundary pattern.
- TypeScript/Python: `validate` or `Validator` in a cron expression validator, JSON schema validator library, or event validation utility is domain validation, not the input-validation architectural pattern. The pattern requires validation at the external API boundary (HTTP request, CLI input, user form) as a systematic practice, not just one-off value checks.
- Pydantic `BaseModel` used purely as a data transfer object without being tied to API request parsing is serialization, not input validation.

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

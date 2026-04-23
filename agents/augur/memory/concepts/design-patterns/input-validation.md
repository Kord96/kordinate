---
kind: concept
name: input-validation
signatures:
  concept: input-validation
  positive:
    strong:
    - request schema validation before handler logic
    - declarative validation library usage on API inputs
    medium:
    - validation middleware or annotations on selected endpoints
    weak:
    - inline assertions scattered in handlers
  negative:
  - validation only in business logic
  - client-side-only validation
  notes:
  - Parameterized SQL alone is not enough to claim full input-validation.
type: pattern
abstraction:
- security
- api
scope: backend
status: primary
review_questions:
  threshold: 5
  entries:
  - id: input-validation-boundary
    prompt: Is validation applied at the request or API boundary before business logic?
    weight: 3
    signals:
    - BaseModel
    - zod
    - '@Valid'
  - id: input-validation-reject-invalid
    prompt: Does invalid input trigger a reject-early response rather than deep business-logic
      checks?
    weight: 2
    signals:
    - ValidationError
    - bad request
monitoring:
  applies_to:
  - flow
  - component
  health_signals:
  - name: validation.failure.rate
    description: Rate of rejected requests or payloads due to schema or contract violations.
  - name: malformed_input.rate
    description: Frequency of malformed or incomplete external inputs hitting the
      boundary.
  business_metrics: []
  gaps:
  - Without validation rejection metrics, abuse and client integration failures are
    easy to miss.
family: design-patterns
---

# Explanation

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

### Relationship To Other Concepts

- Related to [insecure-deserialization](/concepts/insecure-deserialization) because validation is one defensive layer against unsafe payload interpretation.
- Related to [cors](/concepts/cors) and [route-guard](/concepts/route-guard) as adjacent boundary defenses, though validation focuses on payload correctness rather than origin or authorization.

### Boundary

Use `input-validation` when the system explicitly checks external input for shape, type, range, and semantic validity before acting on it.

Do not use it for authorization, escaping, or content negotiation. The key signal is validating incoming data correctness and safety.

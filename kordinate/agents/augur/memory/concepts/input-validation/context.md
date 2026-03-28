## Testing

Verify that all external input is validated at the boundary and rejected inputs produce clear errors.

### Unit Tests

- Submit valid input and assert it passes validation and reaches business logic
- Submit invalid input (missing fields, wrong types, out-of-range values) and assert rejection with field-level error messages
- Test boundary values: empty strings, max-length strings, zero, negative numbers, extremely large numbers

### Injection Tests

- Submit SQL injection payloads and verify parameterized queries prevent execution
- Submit XSS payloads in string fields and confirm output is sanitized or escaped
- Submit command injection strings and verify they are not interpreted by the shell

### Integration Tests

- Send malformed requests (invalid JSON, wrong content type) and verify the API returns 400 with a descriptive error
- Validate that server-side validation rejects input even when client-side validation is bypassed


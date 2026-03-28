## Testing

Verify configuration loading, validation, environment overrides, and hot-reload behavior.

### Unit Tests

- Load config from each supported source (file, env vars, defaults) and assert correct precedence
- Test validation: missing required fields produce clear errors, invalid values are rejected
- Verify type coercion: string env vars are correctly parsed to integers, booleans, etc.

### Integration Tests

- Boot the application with a full config file and verify all components receive their expected settings
- Test hot-reload: change a config value at runtime and verify the application picks it up without restart

### Failure Injection

- Supply a config file with syntax errors and verify the application fails fast with a descriptive message
- Remove a required config source and verify fallback or fail-fast behavior per policy


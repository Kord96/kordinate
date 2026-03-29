---
description: Hardcoded Credentials — testing guidance
type: supplementary
---
## Testing

Verify that no secrets appear in source code, configuration, or version history.

### Unit Tests

- Assert that modules reading credentials pull from environment variables or a secrets manager, never from string literals
- Inject mock credentials via environment and verify the application uses the injected values

### Static Analysis

- Run `trufflehog` or `git-secrets` against the repository and assert zero findings
- Add a CI lint step that greps for high-entropy strings and known secret prefixes (`AKIA`, `sk-`, `ghp_`)
- Validate that `.gitignore` includes `.env`, `*.pem`, and credential file patterns

### Integration Tests

- Deploy to a test environment with secrets injected via secrets manager and verify the application starts and authenticates successfully
- Rotate a credential in the secrets store and confirm the application picks up the new value without a code change

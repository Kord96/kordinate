---
description: Secret Management — testing guidance
type: supplementary
---
# Testing

- Scan the entire codebase and git history for hardcoded secrets using tools like gitleaks or trufflehog
- Test that manifests and config files reference secrets via `secretKeyRef`, never inline `value`
- Verify that CI/CD pipelines do not log or expose secret values in build output (grep build logs)
- Test secret rotation by swapping a credential and confirming the application picks up the new value
- Assert that `.env` files are in `.gitignore` and only `.env.example` with placeholder values is committed
- Test that application startup fails gracefully with a clear error when a required secret is missing
- Verify audit logging captures secret access events (who accessed which secret and when)

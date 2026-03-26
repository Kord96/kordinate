---
description: Secret Management architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
---
# Secret Management

## Recognition

How to identify this pattern in code.

### Signatures

- Vault integration (`hashicorp/vault`, `vault` CLI, `VAULT_ADDR`)
- Sealed secrets or external-secrets operator in Kubernetes
- `pass` store for credential management (`pass insert`, `pass show`)
- KMS integration (AWS KMS, GCP KMS, Azure Key Vault)
- `secretKeyRef` in K8s manifests referencing Secret objects
- Never-hardcoded credentials with rotation policies
- Secret scanning in CI (`gitleaks`, `trufflehog`, `detect-secrets`)
- `.env` files in `.gitignore` with template `.env.example` checked in

### Confidence

- **high** -- Dedicated secret store integration (Vault, external-secrets operator, `pass`) with rotation and audit logging
- **medium** -- Secrets in environment variables or K8s Secrets, not hardcoded but without a dedicated secret management system
- **low** -- Secrets in config files that are gitignored, with no formal rotation or access auditing

## Architecture

Look for secrets never committed to version control, accessed through a dedicated store, with rotation and audit capabilities.

### Review Checklist

- No secrets are hardcoded in source code, manifests, or config files checked into version control
- Secrets are sourced from a dedicated store (`pass`, Vault, external-secrets) at deploy time or runtime
- Secret rotation is possible without code changes or redeployment
- Access to secrets is auditable (who accessed what and when)
- Secret references in manifests use `secretKeyRef`, never inline `value`
- CI/CD pipelines do not log or expose secret values in build output

### Anti-patterns

- Secrets committed to git, even in "private" repositories (they persist in history forever)
- Shared secrets across environments (production credentials in staging)
- No rotation -- secrets unchanged since initial setup with no process to rotate them
- Secrets passed as command-line arguments (visible in process listings and shell history)

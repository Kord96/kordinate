---
description: Hardcoded Credentials anti-pattern
type: anti-pattern
testable: true
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - secret-management
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Hardcoded Credentials

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `password = "..."` or `passwd = "..."` assigned as string literals
- `api_key = "..."` or `apikey = "..."` in source files
- `secret = "..."` or `secret_key = "..."` as inline values
- `token = "sk-..."` or other provider-prefixed token strings
- AWS access keys in source (`AKIA` prefix in string literals)
- `.env` files committed to git (present in tracked files, not in `.gitignore`)
- `private_key` as a string literal or multi-line string in source
- `Authorization: Bearer` with a literal token value in code
- Database connection strings with embedded passwords (`postgresql://user:pass@host`)

### Confidence

- **high** -- literal `AKIA` prefix, `sk-` prefix, or `private_key` block found in tracked source files
- **medium** -- variables named `password`, `secret`, or `api_key` assigned string literals
- **low** -- `.env.example` contains real-looking values, or config files have placeholder secrets that look non-random

## Impact

Credential exposure in version control, enabling unauthorized access once the repository is cloned, forked, or leaked.

### Symptoms

- Secrets visible in git history even after deletion from HEAD
- Automated scanners (GitHub secret scanning, TruffleHog) firing alerts
- Credential rotation requires code changes and redeployment
- Shared repositories expose production credentials to all contributors
- Compromised credentials lead to lateral movement across services

### Remediation

- Move all secrets to environment variables or a secrets manager (`pass`, Vault, AWS Secrets Manager)
- Add `.env`, `*.pem`, and credential files to `.gitignore`
- Run `git-secrets` or `trufflehog` as a pre-commit hook to block commits containing secrets
- Rotate any credentials that have ever appeared in version control
- Reference secrets in Kubernetes manifests as `secretKeyRef`, never as inline `value`

See also: secret-management pattern

### Relationship To Other Concepts

- Related to [secret-management](/concepts/secret-management) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `hardcoded-credentials` when the important observation is this specific recurring architectural failure mode within a backend service, storage, or server-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.

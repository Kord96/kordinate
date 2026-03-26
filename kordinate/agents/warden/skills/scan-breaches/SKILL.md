---
name: scan-breaches
description: Scan repos for hardcoded secrets, PII, and exposed configuration
curated: true
scope: global
---

Scan a project's source code for hardcoded secrets, personally identifiable information, and exposed configuration.

## Arguments

`$ARGUMENTS` — Required: `<path>` (project directory or repo to scan). Optional: `--fix` (route findings to correct destinations).

## Patterns

### Critical (credential)

| Pattern | Example |
|---------|---------|
| API keys | `AKIA...`, `sk-...`, `ghp_...`, `Bearer ...` |
| Tokens | `eyJ...` (JWT), hex strings > 32 chars in assignments |
| Passwords | `password = "..."`, `passwd`, `secret` in assignments |
| Private keys | `BEGIN RSA PRIVATE KEY`, `BEGIN EC PRIVATE KEY` |
| Connection strings | `postgres://user:pass@`, `redis://:pass@` |

### High (PII)

| Pattern | Example |
|---------|---------|
| Email addresses | `user@domain.com` in code (not git config) |
| Phone numbers | Patterns matching international phone formats |

### Medium (hardcoded config)

| Pattern | Example |
|---------|---------|
| IP addresses | `10.x.x.x`, `192.168.x.x`, `100.x.x.x` in code |
| Hardcoded ports | Non-standard ports in source (not config.yaml) |
| Hardcoded hostnames | FQDNs in source (not config.yaml) |

## Procedure

1. **Parse** path from `$ARGUMENTS`. If missing, show usage and exit.
2. **Scan critical** — grep for API key prefixes, JWT patterns, password assignments, private key headers, connection strings. Exclude `.git/`, `node_modules/`, `pass` store paths.
3. **Scan high** — grep for email patterns and phone numbers in source files. Exclude git config, IDENTITY.md author fields, and `package.json` metadata.
4. **Scan medium** — grep for hardcoded IPs and hostnames. Cross-reference against `$KORDINATE_HOME/profile/config.yaml` — IPs that exist in config.yaml are expected; flag those that don't.
5. **Check git history** — search recent commits (last 50) for patterns that were added then removed (secrets that leaked into history).
6. **Report** findings grouped by severity. Show file:line and pattern type, never the actual secret value.
7. **If `--fix`** — for each finding, invoke `/warden:sanitize` to route it to the correct destination.

## Output Format

```
Scan: <path>
Date: <date>

CRITICAL (n findings)
  <file>:<line> — <pattern type> detected

HIGH (n findings)
  <file>:<line> — <pattern type> detected

MEDIUM (n findings)
  <file>:<line> — hardcoded <type>, not in config.yaml

HISTORY (n findings)
  <commit> <file> — <pattern type> added in <date>

Summary: n critical, n high, n medium, n history
```

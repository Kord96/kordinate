---
name: sanitize
description: Classify content as config, credential, or memory and route it to the correct destination.
---

Classify content and route it to the correct destination. `$ARGUMENTS` should include the content to sanitize.

## Types

| Type | Indicators | Destination |
|------|-----------|-------------|
| **Config** | IPs, endpoints, hostnames, domains, ports, namespace names, storage classes | Update Alfred-owned config/profile sources |
| **Credential** | Tokens, passwords, API keys, secrets, auth keys | `pass insert kordinate/<service>/<key>` |
| **Memory** | Facts, observations, patterns, knowledge, decisions | Shared or agent memory |

## Procedure

1. Analyze whether the content contains config, credentials, or memory. A single input may contain all three.
2. Split mixed input into its constituent parts.
3. Route each part to the correct destination.
4. If the input is a Kubernetes manifest file in `manifests/`, run the manifest validation checks below.
5. Report what went where and any validation findings.

## Manifest Validation

Base manifests must contain no environment-specific values. Scan base manifests for:

| Pattern | Severity | Action |
|---------|----------|--------|
| Public domains (FQDNs not ending in `.local`) | ERROR | Move to overlay-generated config |
| `.svc.cluster.local` references | WARN | Prefer deriving from namespace/overlay context |
| IP addresses (not `127.0.0.1` or `0.0.0.0`) | ERROR | Move to config.yaml via overlay |
| Inline config blocks > 5 lines in ConfigMap data | INFO | Consider overlay generation |

### Allowlist

- Placeholder values: `REGISTRY`, `STORAGE_CLASS`, `MUST_BE_SET`, `MUST_BE_SET_BY_OVERLAY`
- Localhost references: `localhost`, `127.0.0.1`, `0.0.0.0`
- Public container image references
- Port numbers in port fields
- `kubernetes.default.svc`

---
name: sanitize
description: Classify content as config, credential, or memory — routes to the correct destination.
curated: true
scope: global
---

Classify content and route it to the right place. $ARGUMENTS should include the content to sanitize.

## Types

| Type | Indicators | Destination |
|------|-----------|-------------|
| **Config** | IPs, endpoints, hostnames, domains, ports, namespace names, storage classes | `$KORDINATE_HOME/profile/config.yaml` |
| **Credential** | Tokens, passwords, API keys, secrets, auth keys | `pass insert kordinate/<service>/<key>` |
| **Memory** | Facts, observations, patterns, knowledge, decisions | `/kord remember` |

## Procedure

1. **Analyze** — does the content contain config, credentials, or memory? A single input may contain all three.
2. **Split** if mixed — "Cluster at 10.95.43.66 has DNS issues with token abc123":
    - Config: IP `10.95.43.66` → `profile/config.yaml`
    - Credential: token `abc123` → `pass`
    - Memory: "DNS issues" → `/kord remember`
3. **Route** each piece to its destination.
4. **Report** what went where.

## Examples

| Input | Classification |
|-------|---------------|
| "Grafana is at grafana.khaledkord.com" | Config — domain goes to config.yaml |
| "The API key for Grafana is sk-abc123" | Credential — goes to pass |
| "Grafana dashboards need to be redeployed after config changes" | Memory — operational knowledge |
| "MinIO at 10.95.43.66:9000 password is kordinate-minio" | Mixed — IP+port to config, password to pass |

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
| **Config** | IPs, endpoints, hostnames, domains, ports, namespace names, storage classes | `/config` to update `profile/config.yaml` |
| **Credential** | Tokens, passwords, API keys, secrets, auth keys | `pass insert kordinate/<service>/<key>` |
| **Memory** | Facts, observations, patterns, knowledge, decisions | `write_memory` tool |

## Procedure

1. **Analyze** — does the content contain config, credentials, or memory? A single input may contain all three.
2. **Split** if mixed — "Cluster at 10.95.43.66 has DNS issues with token abc123":
    - Config: IP `10.95.43.66` → `/config` to update config.yaml
    - Credential: token `abc123` → `pass`
    - Memory: "DNS issues" → `write_memory` tool
3. **Route** each piece to its destination.
4. **Validate manifests** — if the input is a Kubernetes manifest file (`.yaml` in a `manifests/` directory), run the Manifest Validation checks below.
5. **Report** what went where (and any manifest validation findings).

## Examples

| Input | Classification |
|-------|---------------|
| "Grafana is at grafana.khaledkord.com" | Config — domain goes to config.yaml |
| "The API key for Grafana is sk-abc123" | Credential — goes to pass |
| "Grafana dashboards need to be redeployed after config changes" | Memory — operational knowledge |
| "MinIO at 10.95.43.66:9000 password is kordinate-minio" | Mixed — IP+port to config, password to pass |

## Manifest Validation

When sanitize is invoked on Kubernetes manifest files (`.yaml` in `manifests/`), validate that base manifests contain no environment-specific values. Base manifests must be pure templates — overlays fill in real values.

### Detection Rules

Scan base manifests in `$KORDINATE_HOME/agents/charon/skills/infra/manifests/` for:

| Pattern | Severity | Action |
|---------|----------|--------|
| Public domains (FQDNs not ending in `.local`) | ERROR | Must move to overlay-generated ConfigMap |
| `.svc.cluster.local` references | WARN | Should be derived from namespace context in overlays |
| IP addresses (not `127.0.0.1` or `0.0.0.0`) | ERROR | Must come from config.yaml via overlay |
| Inline config blocks > 5 lines in ConfigMap data | INFO | Consider overlay generation |

### Allowlist (safe in base manifests)

- Placeholder values: `REGISTRY`, `STORAGE_CLASS`, `MUST_BE_SET`, `MUST_BE_SET_BY_OVERLAY`
- Localhost references: `localhost`, `127.0.0.1`, `0.0.0.0`
- Container image references (public registries: `grafana/`, `prom/`, `caddy:`, `cloudflare/`, etc.)
- Port numbers in `containerPort`, `port`, `targetPort` fields
- Kubernetes API URLs (`kubernetes.default.svc`)

### Procedure for Manifest Validation

1. Glob for `*.yaml` in `$KORDINATE_HOME/agents/charon/skills/infra/manifests/`
2. For each file, grep for domain patterns, IPs, and `.svc.cluster.local`
3. Filter against the allowlist
4. Cross-reference: if a value from `profile/config.yaml` (`network.*`, `clusters.*.services.*`) appears in a base manifest, flag it
5. Report findings with file:line, severity, and recommendation

# Consultation

## Cache Sources

Directories to hash for cache invalidation — if any change, cached answers are stale:

- `instructions/`
- `memory/static/`
- `memory/dynamic/`
- `manifests/`
- `../../profile/config.yaml`

When consulted (asked a question by another agent or `/consult deployer`), answer about:
- Cluster state — what's running where, pod counts, restart counts, resource usage
- Versions — what container images are deployed, what tags
- Configuration — what ConfigMaps, Secrets, PVCs exist for a service
- Networking — what ports, services, ingresses are configured
- History — recent deployments, rollouts, changes
- Monitoring/observability architecture — data flow, federation, label injection

## How to answer

1. Check `<project-repo>/manifests/` for project layout; get cluster/registry from profile
2. Use `ssh <cluster> kubectl ...` to query live cluster state
3. Reference curated knowledge (infra.md) for cluster topology
4. Answer with specific pod names, versions, and states — the caller needs facts
5. Keep responses under 50 lines

## Monitoring/observability questions

1. The data flow: which Alloy scrapes what, federation paths, label injection
2. Component roles: gateway = standalone cluster observability, master = unified cross-cluster view
3. Master federates from ALL cluster gateways — should not directly scrape pods gateways already collect
4. Reference infra.md for canonical architecture

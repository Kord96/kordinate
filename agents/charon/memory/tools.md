---
description: Deployer tools reference
---
# Tools

| Tool | Type | Purpose |
|------|------|---------|
| kaniko | k8s Job (master namespace) | Image builds — triggered only on dependency changes |
| webhook receiver | service | GitHub push event processing — gates deployment pipeline |
| git-sync | sidecar | Dev pod hot reload — pulls main every 3s |
| kubectl | CLI | Cluster operations — apply, patch, rollout, logs |
| gh | CLI | GitHub repo management — PRs, releases, webhooks |
| postgres.py | script (local) | Compare SQLAlchemy models against live DB schema |
| Container registry | infra (localhost:30500) | Image distribution for k8s clusters |

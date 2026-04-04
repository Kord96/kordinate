---
name: wrap
description: >
  Add the deployment layer to a project — Dockerfile, kustomize manifests,
  vitals, monitoring. Reads augur's design atlas and the infra-atlas contract
  to produce everything needed to build, deploy, and observe a service.
argument-hint: "<project-name>"
---

Add the deployment layer to a project. Reads augur's design atlas and produces Dockerfile, kustomize manifests, vitals container, and monitoring stubs. Then builds, deploys to dev, and registers the project with the webhook receiver.

## Arguments

`$ARGUMENTS` — Required: `<project-name>`.

The project must have a design atlas at `/kord/agents/augur/memory/projects/<project>/design-atlas.json` (produced by augur `/design <project> --patterns`). If the atlas is missing or its `metadata.status` is not `"approved"`, abort with a clear message.

## What It Produces

Pushes these files to the project's GitHub repo:

```
Dockerfile                 dev + prod multi-stage targets
                           - Dev: runtime + deps, serves from git-sync volume, file watcher
                             (nodemon for Node, uvicorn --reload for Python)
                           - Prod: full baked image
                           Layer order: system deps -> app deps (cached) -> app code
kustomize/
  base/
    deployment.yaml        app deployment from atlas + infra-atlas contract
    service.yaml           ClusterIP service
    vitals.yaml            standalone vitals deployment
    kustomization.yaml
vitals/
  Dockerfile               vitals container
  vitals.py                evaluation stub from atlas failure_modes.detection
  config.yaml              evaluation sections
monitoring/
  dashboards/              Grafana JSON stubs from atlas failure_modes.detection
  alerts.yaml              Prometheus rules (includes VitalsMissing meta-alert)
```

## Procedure

### Step 1 — Read context

1. **Design atlas** — `/kord/agents/augur/memory/projects/<project>/design-atlas.json`
   - Verify `metadata.status` is `"approved"`. If not, abort: "Design atlas for <project> is not approved. Run `/design <project> --approve` first."
   - Extract: `stack.languages[0]` (primary language), `components`, `failure_modes`, `external_dependencies`, `flows`, `observability`

2. **Infra atlas** — `/kord/agents/charon/memory/global/infra-atlas.json`
   - Extract: `new_workload_contract` (probes, resources, labels, vitals spec, metrics annotations), `networking.registry`, `observability.metrics`
   - If missing, abort: "Need infra atlas. Run `/survey` first."

3. **Detect language** — from `stack.languages[0]`:
   - `Python` -> python stack (uvicorn, pip/poetry, .py)
   - `TypeScript` or `JavaScript` -> node stack (nodemon, npm/yarn, .ts/.js)
   - Other -> abort with "Unsupported language: <lang>. Wrap currently supports Python and Node."

4. **Resolve repo** — look up the project's GitHub repo URL. Check atlas `metadata` for repo info, or derive from org convention: `gh repo view <owner>/<project> --json url`.

### Step 2 — Generate Dockerfile

Multi-stage Dockerfile with `dev` and `prod` targets. Layer order enforced: system deps, then app deps (cached), then app code.

#### Python

```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

FROM base AS deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM deps AS dev
RUN pip install --no-cache-dir uvicorn[standard] watchfiles
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM deps AS prod
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Node

```dockerfile
FROM node:20-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci --production

FROM deps AS dev
RUN npm install -g nodemon
CMD ["nodemon", "--watch", "/app/src"]

FROM deps AS prod
COPY . .
EXPOSE 3000
CMD ["node", "src/index.js"]
```

Adapt ports and entrypoints from atlas `components` (look for the primary service component). If the atlas specifies a framework (FastAPI, Express, etc.), adjust the CMD accordingly.

### Step 3 — Generate kustomize manifests

Generate `kustomize/base/` from atlas components + infra-atlas `new_workload_contract`.

#### deployment.yaml

App deployment with:
- `metadata.labels.app: <project>` (required by Alloy for metrics/log discovery)
- Probes from contract: `readinessProbe` and `livenessProbe` on `/health`
- Resource requests/limits from contract defaults: `requests: {cpu: 100m, memory: 256Mi}`, `limits: {memory: 1Gi}`
- Prometheus annotations from contract: `prometheus.io/scrape: "true"`, `prometheus.io/port: "<port>"`
- `SIGTERM` graceful shutdown: `terminationGracePeriodSeconds: 30`
- Single replica for dev

Dev variant includes a git-sync sidecar for live code sync:

```yaml
- name: git-sync
  image: registry.k8s.io/git-sync/git-sync:v4.4.1
  args:
    - "--repo=<github-url>"
    - "--period=3s"
    - "--root=/repo"
    - "--link=<project>"
  volumeMounts:
    - name: repo
      mountPath: /repo
```

The app container mounts the same volume and the file watcher picks up changes.

#### service.yaml

ClusterIP service exposing the app port. DNS: `<project>.<namespace>.svc.cluster.local`.

#### vitals.yaml

Standalone vitals deployment (not a sidecar) from contract:
- Image: `REGISTRY/<project>-vitals:latest`
- Port: 9131
- Environment from contract:
  - `PROMETHEUS_URL=http://prometheus.master.svc.cluster.local:9191`
  - `LOKI_URL=http://loki.master.svc.cluster.local:3100`
  - `APP_NAME=<project>`
- Prometheus scrape annotations on port 9131
- Resource requests: `cpu: 50m, memory: 128Mi`

#### kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
  - vitals.yaml
```

### Step 4 — Generate monitoring

Derive alert rules and dashboard stubs from the atlas `failure_modes` array.

#### alerts.yaml

Prometheus rules from `failure_modes`:
- For each failure mode with `detection` signals, create an alert rule:
  - Alert name: derived from the failure mode `id` (kebab-to-PascalCase)
  - `expr`: map detection signals to PromQL (e.g., error rate signals become `rate(http_requests_total{status=~"5..",app="<project>"}[5m]) > 0.05`)
  - `severity`: from the failure mode's `severity` field
  - `annotations.description`: from the failure mode's `trigger` and `impact`
- **VitalsMissing meta-alert** (always included):
  ```yaml
  - alert: VitalsMissing
    expr: absent(vitals_process{app="<project>"})
    for: 5m
    labels:
      severity: warning
    annotations:
      description: "Vitals container for <project> has not reported in 5 minutes"
  ```

#### dashboards/

Grafana JSON stubs, one per unique `detection.concern` category found across failure modes:
- Each dashboard includes panels for the signals in that concern category
- Panels use the project's `app` label for filtering
- Datasource: Prometheus (from infra atlas `observability.metrics`)

### Step 5 — Generate vitals

#### vitals/vitals.py

Evaluation loop stub:
- Imports: `prometheus_client`, `requests`, `time`, `yaml`, `os`
- Reads `config.yaml` for section definitions
- Runs evaluation loop: for each section, runs checks and exposes `vitals_<section>{check="<name>"}` gauges
- Tri-state values: 0=FAIL, 1=WARNING, 2=OK
- Serves metrics on port 9131
- Stubs for each detection concern from atlas `failure_modes`

#### vitals/config.yaml

Sections from `failure_modes.detection.concern` categories, plus the two required sections:
- `process` — always included: checks the app is running, responding to health endpoint
- `deps` — always included: checks external dependencies from atlas `external_dependencies`
- Additional sections from unique concern categories in `failure_modes`

Each section lists its checks with thresholds derived from the failure mode's detection signals.

#### vitals/Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 9131
CMD ["python", "vitals.py"]
```

With a `requirements.txt` containing: `prometheus_client`, `requests`, `pyyaml`.

### Step 6 — Push to repo

1. Clone the project repo (or use existing checkout)
2. Create a `deploy` branch from main
3. Add all generated files: `Dockerfile`, `kustomize/`, `vitals/`, `monitoring/`
4. Commit with message: `"Add deployment layer (Dockerfile, manifests, vitals, monitoring)"`
5. Push the `deploy` branch
6. Create a PR from `deploy` to `main` with a summary of what was added

### Step 7 — Deploy to dev

1. **Build app image** with kaniko:
   ```bash
   kubectl run kaniko-<project> --image=gcr.io/kaniko-project/executor:latest \
     --restart=Never -n master -- \
     --dockerfile=Dockerfile \
     --context=git://<github-url>#refs/heads/deploy \
     --destination=REGISTRY/<project>:latest \
     --target=dev \
     --cache=true \
     --cache-repo=REGISTRY/<project>/cache
   ```
   Wait for the kaniko pod to complete.

2. **Build vitals image** with kaniko:
   ```bash
   kubectl run kaniko-<project>-vitals --image=gcr.io/kaniko-project/executor:latest \
     --restart=Never -n master -- \
     --dockerfile=vitals/Dockerfile \
     --context=git://<github-url>#refs/heads/deploy \
     --destination=REGISTRY/<project>-vitals:latest \
     --cache=true \
     --cache-repo=REGISTRY/<project>-vitals/cache
   ```
   Wait for completion.

3. **Apply manifests**:
   ```bash
   kubectl apply -k kustomize/base/ -n dev
   ```

4. **Verify**:
   ```bash
   kubectl rollout status deployment/<project> -n dev --timeout=120s
   kubectl rollout status deployment/<project>-vitals -n dev --timeout=120s
   ```
   Check pods are Running, readiness probes pass.

### Step 8 — Register with webhook receiver

Add the project to the webhook receiver's watch list so that future pushes trigger automatic builds and deploys:
- Register the GitHub repo with the webhook receiver endpoint
- Configure the webhook to trigger on pushes to `main`, `test`, and `prod` branches
- Verify the webhook registration succeeded

### Step 9 — Report

```
## Wrap: <project>

**Language**: <detected language>
**Repo**: <github url>
**Branch**: deploy (PR #<number>)

### Files added
- Dockerfile (dev + prod targets)
- kustomize/base/ (deployment, service, vitals — N manifests)
- vitals/ (Dockerfile, vitals.py, config.yaml — N sections: <section names>)
- monitoring/ (N alert rules, N dashboards, VitalsMissing meta-alert)

### Deployed to dev
- App: <project> deployment — <status>
- Vitals: <project>-vitals deployment — <status>
- Images: REGISTRY/<project>:latest, REGISTRY/<project>-vitals:latest

### Webhook
- Registered: <status>

Merge the PR to land the deployment layer on main.
```

## Rules

- Authenticate before any operation: use `/authenticate`.
- Never hardcode secrets in manifests — secrets are managed by alfred.
- Layer order in Dockerfiles is mandatory: system deps, app deps (cached), app code.
- Vitals is always a standalone deployment, never a sidecar.
- VitalsMissing meta-alert is always included in alerts.yaml.
- `process` and `deps` sections are always included in vitals config.yaml.
- Resource defaults from the infra-atlas contract are the floor — override upward if the atlas suggests heavier workloads.
- If the design atlas has `metadata.new_infrastructure` entries, warn: "This project requires infrastructure not yet provisioned: <list>. Run `/platform deploy` or provision manually before deploying."

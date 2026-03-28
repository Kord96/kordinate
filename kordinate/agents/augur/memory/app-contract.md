---
description: App Contract
curated: true
scope: global
preloaded: augur
---
# App Contract

> **For your specific app labels and allowed values, see `profile/topology.yaml`.**

Every deployed application must satisfy these requirements:

## Labels

Required pod label:
- `app` — project name that owns this workload

Allowed values are defined in `profile/topology.yaml` under `apps`. Typical categories:
- `<product-app>` — product workload pods
- `<platform-app>` — user-managed shared services that apps depend on (message queues, databases, caches)
- `<system-app>` — system-critical infrastructure (gateway, master, grafana, workstation, node-exporter, KSM). Without these the entire system breaks. Managed by the charon, not subject to the app contract.

Optional pod labels:
- `component` — individual service name (e.g., `classifier`, `kafka`)
- `tier` — operational role (e.g., `ingest`, `process`, `store`)

The `pod` label is automatically injected by Alloy from Kubernetes metadata and serves as the primary service identifier.

## Annotations

Required:
- `prometheus.io/scrape: "true"`
- `prometheus.io/port: "<port>"`

## Observability

Apps follow the observability contract: `/metrics` + stdout JSON + vitals pod.
Gateway collects via Alloy. Master federates metrics via `:9090` /federate. Logs: gateway sidecar writes to MinIO, master puller fetches via `:9000`.

1. **Metrics**: Expose `/metrics` endpoint in Prometheus format
   - Scraped by Gateway Alloy; master federates from gateway Prometheus (:9090/federate)
   - Examples: request rate, error count, queue depth, cache hit ratio

2. **Logs**: Write structured JSON to stdout — tailed locally by Gateway Alloy, pulled by master via MinIO (:9000)
   - Required fields: `level`, `message`
   - Optional fields: `trace_id`, `consumer`, `error`

3. **Health**: Vitals pod evaluates app health via gateway Prometheus queries

## Enforcement

The charon validates the app contract on deployment:
- `app` label must be present with an allowed value
- `/metrics` endpoint must return valid Prometheus format
- Log output must be structured JSON

Apps that do not satisfy the contract are rejected.

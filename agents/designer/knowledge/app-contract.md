# App Contract

Every deployed application must satisfy these requirements:

## Labels

Required pod label:
- `app` — project name that owns this workload

Allowed values:
- `logbd` — pipeline product pods
- `app-infra` — user-managed shared services that apps depend on (kafka, postgres, redis)
- `kord-infra` — system-critical infrastructure (gateway, master, grafana, workstation, node-exporter, KSM). Without these the entire system breaks. Managed by the deployer, not subject to the app contract.

Optional pod labels:
- `component` — individual service name (e.g., `classifier`, `kafka`)
- `tier` — operational role (e.g., `ingest`, `process`, `store`)

The `pod` label is automatically injected by Alloy from Kubernetes metadata and serves as the primary service identifier.

## Annotations

Required:
- `prometheus.io/scrape: "true"`
- `prometheus.io/port: "<port>"`

## Observability

1. **Metrics**: Expose `/metrics` endpoint in Prometheus format
   - Scraped by Alloy from the gateway namespace
   - Examples: request rate, error count, queue depth, cache hit ratio

2. **Logs**: Write structured JSON to stdout — tailed by Alloy via K8s API
   - Required fields: `level`, `message`
   - Optional fields: `trace_id`, `consumer`, `error`

## Enforcement

The deployer validates the app contract on deployment:
- `app` label must be present with an allowed value
- `/metrics` endpoint must return valid Prometheus format
- Log output must be structured JSON

Apps that do not satisfy the contract are rejected.

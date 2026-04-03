---
description: Service Mesh — monitoring guidance
---
## Monitoring

Track sidecar proxy health, mTLS certificate status, and service-to-service traffic quality through the mesh.

### Key Metrics

- `mesh_sidecar_cpu_usage_ratio` (gauge) — sidecar proxy CPU consumption relative to container limits, per pod
- `mesh_sidecar_memory_bytes` (gauge) — sidecar proxy memory usage per pod
- `mesh_mtls_handshake_failures_total` (counter) — mTLS handshake errors indicating certificate or config problems
- `mesh_request_error_rate` (gauge) — 5xx error rate per service pair through the mesh
- `mesh_request_latency_seconds` (histogram) — p50/p95/p99 latency per service pair
- `mesh_control_plane_sync_latency_seconds` (histogram) — time for configuration pushes from control plane to proxies
- `mesh_certificate_expiry_seconds` (gauge) — time remaining before mesh-managed mTLS certificates expire

### Alerts

- Sidecar proxy consuming excessive resources and starving the application container
- mTLS handshake failure rate elevated (certificate expiry or misconfiguration)
- Service pair error rate exceeding acceptable threshold
- Control plane xDS sync errors or disconnected proxies
- mTLS certificate approaching expiry without rotation

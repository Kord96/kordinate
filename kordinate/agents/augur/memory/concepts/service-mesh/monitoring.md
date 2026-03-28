---
description: Service Mesh — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Monitoring

- Track sidecar proxy resource usage (CPU, memory) per pod to detect proxies starving application containers
- Monitor mTLS handshake failure rates — failures indicate certificate expiry or misconfiguration
- Alert on mesh-level error rates (5xx) and latency percentiles (p99) per service pair
- Track control plane health: configuration push latency, connected proxies, xDS sync errors
- Monitor traffic policy enforcement — verify retry and timeout policies are applied as configured
- Dashboard showing service-to-service traffic topology with success rates and latency
- Alert on certificate expiry approaching for mesh-managed mTLS certificates

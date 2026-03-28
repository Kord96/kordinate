# Monitoring

- Track sidecar proxy resource usage (CPU, memory) per pod to detect proxies starving application containers
- Monitor mTLS handshake failure rates — failures indicate certificate expiry or misconfiguration
- Alert on mesh-level error rates (5xx) and latency percentiles (p99) per service pair
- Track control plane health: configuration push latency, connected proxies, xDS sync errors
- Monitor traffic policy enforcement — verify retry and timeout policies are applied as configured
- Dashboard showing service-to-service traffic topology with success rates and latency
- Alert on certificate expiry approaching for mesh-managed mTLS certificates

# Deployment

- Upgrade the mesh control plane before data plane sidecars — control plane must support the new proxy version
- Roll sidecar updates gradually using a canary or rolling restart to avoid fleet-wide proxy issues
- Verify mTLS mode after upgrade — confirm enforcement has not reverted to permissive
- Set sidecar resource limits explicitly in the deployment manifest to prevent proxy resource contention
- Test traffic policies (retries, timeouts, circuit breaking) in staging before promoting to production
- Coordinate namespace-level authorization policy changes with the teams owning affected services
- Validate that sidecar injection is working for new pods after control plane upgrades


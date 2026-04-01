---
description: REST API — monitoring guidance
type: supplementary
---
## Monitoring

Track request volume, latency distribution, and error rates by endpoint and HTTP method.

### Key Metrics

- `http_requests_total` (counter) -- request count by method, endpoint, and status code
- `http_request_duration_seconds` (histogram) -- latency distribution by endpoint
- `http_response_size_bytes` (histogram) -- response payload size by endpoint
- `http_4xx_total` (counter) -- client errors by endpoint (400, 404, 422, 429)
- `http_5xx_total` (counter) -- server errors by endpoint (500, 502, 503)

### Alerts

- 5xx error rate exceeds threshold for any endpoint (server-side failure)
- P99 latency exceeds SLA for a sustained period (performance degradation)
- 429 rate spike on authentication endpoints (possible brute-force or credential stuffing)
- Sudden drop in request volume on a high-traffic endpoint (upstream failure or routing change)

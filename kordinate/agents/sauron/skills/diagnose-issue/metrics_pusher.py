"""
Reference pattern: Prometheus metrics exposition via HTTP server.

Projects use prometheus_client to define metrics and start_http_server
to expose them. Prometheus scrapes via kubernetes pod annotations.

Usage:
    from prometheus_client import Counter, Gauge, Histogram, start_http_server

    # Define metrics
    messages_consumed = Counter("messages_consumed_total", "Messages consumed", ["consumer"])
    flush_duration = Histogram("flush_duration_seconds", "Flush duration", ["consumer"])
    buffer_size = Gauge("buffer_size", "Current buffer size", ["consumer"])

    # Expose on a metrics port (set via prometheus.io/port annotation)
    start_http_server(9100)

    # Update metrics in your code
    messages_consumed.labels(consumer="domain").inc()
    with flush_duration.labels(consumer="domain").time():
        do_flush()
    buffer_size.labels(consumer="domain").set(len(buffer))

In k8s, Prometheus discovers pods via annotations:
    metadata:
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9100"
        prometheus.io/path: "/metrics"   # optional, default /metrics

No push gateway needed — Prometheus scrapes directly.

For the MetricsHook pattern (stoik framework), see stoik's own metrics hook.
"""

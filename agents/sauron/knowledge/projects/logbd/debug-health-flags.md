## Debug Reference: Sentinel Health Flags → Loki Queries

Each row maps a sentinel section + check to what triggers it and the Loki query to diagnose.

### Loki Label Schema

All logBD pods use `app=logbd`. Per-process identity is on the `component` label,
which Alloy relabels to `consumer` in Loki.

- Sentinel: `{consumer="sentinel"}`
- Consumers: `{consumer="message-producer"}`, `{consumer="entity-extraction"}`, `{consumer="graph-domain"}`, etc.
- All logBD: `{app="logbd"}`

Logs are structured JSON (structlog). Filter by event name: `| json | event="<name>"`.

### Start Here

Sentinel logs every status transition:
- `{consumer="sentinel"} |= "health_check_degraded"` — any check going WARN/FAIL (includes section, check, reason)
- `{consumer="sentinel"} |= "health_check_recovered"` — any check returning to OK

Always start here to see which checks degraded and why, then drill into the specific consumer logs below.

---

### Ingestion

| Check | Triggers | Loki Query | Key Events |
|-------|----------|------------|------------|
| `producer` | Port unreachable or slot processing >5m/10m | `{consumer="message-producer"} \|~ "slot_ingestion_error\|slot_ingestion_failed\|slot_zero_published\|nfs_mount_unreachable\|kafka_batch_publish_failed"` | `slot_zero_published` (WARN: parsed>0 but published=0, Kafka issue), `slot_ingestion_error` (ERROR: worker crash), `slow_slot_ingestion` (WARN: >300s), `nfs_mount_unreachable` (ERROR: rawLog NFS down) |
| `keeping_up` | Extraction port down or lag growing | `{consumer="entity-extraction"} \|~ "worker_exited\|all_workers_dead\|some_workers_dead\|extraction_flush_slow"` | `all_workers_dead` (ERROR: all workers crashed), `extraction_flush_slow` (WARN: flush >60s), `worker_exited` (ERROR: worker died with exitcode) |
| `eta` | Consume rate=0 with lag>0 | `{consumer="entity-extraction"} \| json \| level="error"` | If no errors: consumer is simply behind. Check `pipeline_consumed_total` rate in Prometheus instead. Loki alone can't diagnose pure lag. |

**Logging gaps**: Entity extraction silently swallows JSON deserialization errors and per-entity parse failures (IP, URI, email). Only aggregate flush metrics reveal problems.

### Buffers (Graph Store)

| Check | Triggers | Loki Query | Key Events |
|-------|----------|------------|------------|
| `flush_rate` | Consumer has lag but no flushes/consumption in 15m | `{app="logbd", consumer=~"graph-.*"} \|~ "staging_merge_failed\|duckdb_reconnect_failed\|compaction_failed"` | `staging_merge_failed` (ERROR: DuckDB merge exception), `duckdb_reconnect_failed` (ERROR: lost DB connection after 60 retries), `compaction_failed` (ERROR: traffic history compaction error) |
| `flush_latency` | Avg flush >=900s (warn) / >=1800s (fail) | `{app="logbd", consumer=~"graph-.*"} \|~ "flush_complete\|edge_flush\|score_flush"` | These are INFO events with duration fields. Filter `\| json \| duration_s > 300` to find slow flushes. graph-domain and graph-host excluded from sentinel check (DNS enrichment during flush). |

**Note**: Sentinel skips graph-domain and graph-host for latency checks because DNS enrichment legitimately makes flushes slow.

### Enrichment

| Check | Triggers | Loki Query | Key Events |
|-------|----------|------------|------------|
| `dns` | Domain port down or DNS error ratio >10%/30% | `{consumer="graph-domain"} \|= "dns_error_rate_high"` | `dns_error_rate_high` (WARN: batch DNS error ratio exceeds threshold). Individual DNS failures are NOT logged — only the aggregate ratio. |
| `whois` | WHOIS backlog growing fast | `{consumer="graph-domain-whois"} \|~ "whois_enrichment_backlog\|whois_high_failure_rate\|rdap_rate_limited\|rdap_timeout\|rdap_server_error\|whois_lookup_batch_failed"` | `whois_enrichment_backlog` (WARN: stale queue >90% of batch), `whois_high_failure_rate` (WARN: >30% failed), `rdap_rate_limited` (WARN: 429), `rdap_timeout` (WARN) |
| `backlog` | Combined backlog derivative >0 | `{app="logbd", consumer=~"graph-domain.*"} \|~ "enrichment_backlog\|high_failure_rate"` | Check whois, uclt, and ct backlogs individually. Each service has its own `*_enrichment_backlog` and `*_high_failure_rate` events. |
| `spf` | SPF coverage <1%/<0.5% | `{consumer="graph-host"} \|~ "spf_edges_emitted\|txt_resolved"` | `spf_edges_emitted` (INFO: hosts_with_spf, includes, subnets counts). **Logging gap**: DNS failures during SPF resolution are silent — only success is logged. If spf_edges_emitted shows 0 hosts_with_spf, resolution is broken but no error event exists. |

**Also check**: `{consumer="graph-domain-uclt"} |~ "uclt_enrichment_backlog|uclt_high_failure_rate"` and `{consumer="graph-domain-ct"} |~ "ct_rate_limited|ct_query_timeout|ct_high_failure_rate"` for UCLT/CT issues.

### Downloads

| Check | Triggers | Loki Query | Key Events |
|-------|----------|------------|------------|
| `processes` | uri-download or js-render port unreachable | `{app="logbd", consumer=~"uri-download\|js-render"} \| json \| level="error"` | `js_batch_timeout` (ERROR: entire batch >300s), `js_browser_error` (ERROR: browser crash). uri-download errors are WARNING level (`download_failed`). |
| `queue` | Queue growing, download rate=0 | `{app="logbd", consumer=~"uri-download\|js-render"} \|~ "download_failed\|storage_budget_exceeded\|queue_depth_read_failed\|js_render_error\|js_render_phase_timeout"` | `storage_budget_exceeded` (WARN: PVC >80%), `download_failed` (WARN: per-URI failure with error), `js_render_phase_timeout` (WARN: navigation/extraction timeout) |
| `enqueue` | uri-download unreachable | `{consumer="uri-download"} \| json \| level=~"error\|warning"` | If no recent logs at all, process is down. |

### Derived

| Check | Triggers | Loki Query | Key Events |
|-------|----------|------------|------------|
| `service` | derived-refresh port unreachable | `{consumer="derived-refresh"} \| json \| level="error"` | `refresh_cycle_error` (ERROR: cycle exception), `tier_g_failed` (ERROR: Tier G batch failure), `tier_computation_failed` (ERROR: per-tier exception), `refresh_failed` (ERROR: top-level failure) |
| `staleness` | Max staleness >2h/6h or Tier G >7h/12h | `{consumer="derived-refresh"} \|~ "derived_staleness_high\|tier_g_failed\|refresh_skipped_db_locked\|duckdb_open_failed\|duckdb_attach_failed\|bulk_upsert_failed"` | `derived_staleness_high` (WARN: entity >2h stale), `refresh_skipped_db_locked` (WARN: DuckDB locked), `duckdb_open_failed` / `duckdb_attach_failed` (WARN: can't open/attach DB). For Tier G progress: `{consumer="derived-refresh"} \|= "Tier G:"` (uses Python logging, capital G). |

**Note**: Tier G logs use Python `logging` module (not structlog), so messages appear as `"Tier G: ..."` free text rather than structured events.

### Storage

| Check | Triggers | Loki Query | Key Events |
|-------|----------|------------|------------|
| `pvc_usage` | PVC >80%/90% | `{consumer="sentinel"} \|~ "storage_pvc_critical\|storage_pvc_high\|storage_pvc_no_metrics"` | Sentinel logs these directly. To find WHICH DB grew, check Prometheus: `topk(5, pipeline_db_file_size_bytes)`. |
| `retention` | CronJob suspended or stale >26h | `{consumer="sentinel"} \|~ "storage_retention_suspended\|storage_retention_stale\|storage_retention_no_metrics"` | Retention runs inside consumer pods (not a separate service). Check consumer logs for retention events: `{app="logbd"} \|~ "retention_start\|retention_complete\|edge_db_locked\|message_role_db_locked\|derived_db_locked"`. |
| `db_growth` | DB growing >5/10 GB/h | `{consumer="sentinel"} \|~ "storage_db_growth_critical\|storage_db_growth_high"` | Use Prometheus to identify which DB: `topk(5, deriv(pipeline_db_file_size_bytes[1h]))`. |
| `kafka_usage` | Topic >80%/90% of retention | `{consumer="sentinel"} \|~ "storage_kafka_critical\|storage_kafka_high"` | Sentinel logs the worst topic name. Check if topic is not compacting or if production spiked. |

**Note**: Retention scheduler is a CronJob (02:00 UTC daily) that `kubectl exec`s into each consumer pod. Retention logs appear in the consumer's own log stream, not a separate app.

### Dependencies

| Check | Triggers | Loki Query | Key Events |
|-------|----------|------------|------------|
| `redis` | Redis ping failed | `{consumer="sentinel"} \|= "redis_unavailable"` | `redis_unavailable` (WARN: with redis_url, error, consecutive_failures fields). Also check consumer Redis errors: `{app="logbd"} \|~ "redis_connection_error\|redis_timeout\|redis_push_failed"`. |
| `kafka` | Exporter unreachable or 0 brokers | `{consumer="sentinel"} \|~ "kafka_broker_unreachable\|kafka_broker_degraded"` | `kafka_broker_unreachable` (WARN: exporter probe failed), `kafka_broker_degraded` (WARN: exporter up but broker count unavailable). |
| `loki` | /ready endpoint failed | `{consumer="sentinel"} \|= "health_check_degraded" \|= "loki"` | No explicit loki failure event — only visible via health_check_degraded transition log with check="loki". |

### Process-level (cross-cutting)

| Status | Triggers | How to Debug |
|--------|----------|-------------|
| FAIL (0) | Port down + no flushes, or 3+ restarts/hr | **Loki**: `{consumer="<name>"} \| json \| level="error"` for last errors before crash. **Prometheus**: `pipeline_container_restarts_total{container="<name>"}` for restart count. OOM kills are silent in logs — only visible as restart spikes. |
| STUCK (1) | Flush rate=0 with lag>0, not consuming | **Loki**: `{consumer="<name>"} \|~ "duckdb_reconnect_failed\|staging_merge_failed\|db_locked"` for lock/DB issues. **Prometheus**: `rate(pipeline_flush_duration_seconds_count{consumer="<name>"}[30m])` to confirm zero flush rate. No deadlock detection exists. |
| Crash loop | 3+ restarts in 1h | **Sentinel**: `{consumer="sentinel"} \|= "crash_loop_detected"` logs the process name. **Consumer**: check last ERROR before restart in `{consumer="<name>"}`. |

**Logging gaps (cannot debug via Loki alone)**:
- OOM kills: no log event, only visible as `pipeline_container_restarts_total` spike in Prometheus
- Deadlocks: no detection or logging, inferred from flush rate=0 + lag>0
- k8s restart events: in kubelet, not Loki. Use `kubectl describe pod` or Prometheus restart metric.

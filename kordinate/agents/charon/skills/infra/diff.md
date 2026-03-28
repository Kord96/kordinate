# diff

Produce diff files on the target environment — staged data that roll will apply.

## Arguments

`$ARGUMENTS` — Required format: `<project> <source-env> <target-env>` (e.g., `logbd prod test`)

Optional flags:
- `--report-only` — show the diff summary without producing files (read-only).

## Context

Diff files are staged at a well-known location on the target env's pods:
- DuckDB deltas: `/tmp/diff/<table>_delta.parquet` on each consumer pod
- Postgres deltas: `/tmp/diff/<table>_delta.sql` on the postgres pod
- A manifest file: `/tmp/diff/manifest.json` listing all staged files, row counts, and source timestamps

Roll checks for `/tmp/diff/manifest.json` and applies everything listed in it.

## Steps

1. Parse project, source, and target from `$ARGUMENTS`. Discover manifests at `<project-repo>/manifests/` and get cluster info from `profile/config.yaml`.

2. SSH to the cluster. **Inventory both environments**:

   a. **PVC comparison**: list PVCs in both namespaces, compare names and sizes.

   b. **DuckDB tables**: for each consumer pod with a DuckDB PVC, exec into both source and target pods:
      ```
      python3 -c "
      import duckdb
      conn = duckdb.connect('<db_path>', read_only=True)
      tables = conn.execute(\"SELECT table_name FROM information_schema.tables\").fetchall()
      for (t,) in tables:
          row = conn.execute(f'SELECT count(*), max(first_seen_at), min(first_seen_at) FROM {t}').fetchone()
          print(f'{t}: count={row[0]:,} max_ts={row[1]} min_ts={row[2]}')
      conn.close()
      "
      ```

   c. **Postgres**: compare schemas and row counts between source and target.

3. If `--report-only`, print the diff summary and exit.

4. **Produce diff files on target pods**:

   a. **DuckDB deltas**: for each table with a row delta, exec into the SOURCE pod:
      ```
      python3 -c "
      import duckdb, os
      os.makedirs('/tmp/diff', exist_ok=True)
      conn = duckdb.connect('<db_path>', read_only=True)
      conn.execute(\"COPY (SELECT * FROM <table> WHERE first_seen_at > <target_max_ts>) TO '/tmp/diff/<table>_delta.parquet'\")
      conn.close()
      "
      ```
      Then transfer to target pod:
      ```
      kubectl cp <source-pod>:/tmp/diff/<table>_delta.parquet /tmp/<table>_delta.parquet -n <source-ns>
      kubectl exec <target-pod> -n <target-ns> -- mkdir -p /tmp/diff
      kubectl cp /tmp/<table>_delta.parquet <target-pod>:/tmp/diff/<table>_delta.parquet -n <target-ns>
      ```
      Clean up source and local temp files after transfer.

   b. **Postgres deltas**: produce SQL dumps of delta rows:
      ```
      pg_dump -h <source-host> -U <user> -d <db> --data-only --table=<table> \
        --where="created_at > '<target_max_ts>'" > /tmp/diff/<table>_delta.sql
      ```
      Transfer to target postgres pod's `/tmp/diff/`.

5. **Write manifest**: exec into each target pod that has diff files:
   ```
   python3 -c "
   import json, os, glob
   files = glob.glob('/tmp/diff/*_delta.*')
   manifest = {
       'source_env': '<source>',
       'target_env': '<target>',
       'files': [{'path': f, 'size': os.path.getsize(f)} for f in files]
   }
   with open('/tmp/diff/manifest.json', 'w') as f:
       json.dump(manifest, f, indent=2)
   "
   ```

6. **Report**: print diff summary table + list of staged files with sizes.

## Output format

```
## Data Diff: <project> <source> → <target>

### DuckDB Tables
| Component | Table | Source Rows | Target Rows | Delta | Staged File |
|-----------|-------|-----------|------------|-------|-------------|
| text | base_text | 5,200,000 | 3,100,000 | +2,100,000 | base_text_delta.parquet (45MB) |

### Postgres
| Table | Source Rows | Target Rows | Delta | Staged File |
|-------|-----------|------------|-------|-------------|
| emails | 150,000 | 140,000 | +10,000 | emails_delta.sql (2MB) |

### Summary
- Staged 8 diff files across 5 pods
- Total delta: +5.2M rows, ~120MB staged
- Apply with: /deployer:roll <project> <source> <target>
```

## Rules

- Always use read-only connections when querying source data.
- Clean up temp files on the source pod and local machine after transfer.
- Never modify existing data — diff only produces new delta files.
- If target env is stopped, report "target pods not running — start with /deployer:roll first" and exit.
- If no delta exists (environments are in sync), report "no diff" and produce no files.

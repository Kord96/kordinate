---
description: Etl architectural pattern
curated: true
scope: global
---
# ETL/ELT


## Architecture

Look for idempotent loads and clear checkpoint/bookmark tracking.

### Review Checklist

- Extract phase tracks a bookmark (timestamp, offset) for incremental runs
- Transform logic is pure — no side effects, testable in isolation
- Load phase is idempotent (re-running does not create duplicates)
- Failures at any stage produce clear errors and do not leave partial state
- Schema validation happens between extract and transform

### Anti-patterns

- Full re-extract every run when incremental is possible (wastes resources)
- Transform logic embedded in SQL without version control or tests
- No checkpoint — failures require manual restart from scratch
- Silent data loss on transform errors (records dropped without logging)

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO

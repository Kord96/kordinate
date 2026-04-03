---
description: Deployment model — git-sync for code, /roll for promotion, migrations gate schema changes
---
# Deployment Model

## New Projects

Use `/wrap` to scaffold a project. This generates manifests, git-sync config, and dev pod setup.

## Code Changes

Code changes do not need a migration or rebuild — just push to the repo. Dev pods use **git-sync** sidecars that pull main every 3s with a file watcher for hot reload. No manual intervention needed.

**Image rebuilds** are only triggered on dependency changes (package.json, requirements.txt, go.mod, etc.), not on code changes.

## Environment Promotion

Use `/roll` to promote between environments: dev -> test -> prod. See `infra-atlas.json` for environment definitions.

## Schema Migrations

Schema migrations still gate deployments:

1. **Diff branches** — `git diff <deployed>..<new> -- **/models.py **/schema.py`
2. **Detect drift** — if model files changed, use `postgres.py` to compare SQLAlchemy models against live DB
3. **Write migrations** — create scripts in `<repo>/migrations/`
4. **Execute migrations** — run scripts before applying new manifests
5. **Gate on drift** — if unhandled schema changes exist and no migration script, block deployment

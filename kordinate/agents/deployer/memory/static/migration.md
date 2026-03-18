# Migration

Full migration lifecycle for deployments:

1. **Diff branches** — `git diff <deployed>..<new> -- **/models.py **/schema.py`
2. **Detect drift** — if model files changed, use `postgres.py` to compare SQLAlchemy models against live DB
3. **Write migrations** — create scripts in the project repo (e.g. `<repo>/migrations/`)
4. **Execute migrations** — run scripts before applying new manifests
5. **Gate on drift** — if unhandled schema changes exist and no migration script, block deployment

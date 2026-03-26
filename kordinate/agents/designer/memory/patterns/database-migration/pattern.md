---
description: Database Migration architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
---
# Database Migration

## Recognition

How to identify this pattern in code.

### Signatures

- Versioned migration files: numbered or timestamped scripts (`001_create_users.sql`, `V2__add_index.sql`)
- Migration frameworks: `alembic` (Python), `flyway` (Java/JVM), `knex migrate` (Node), `django migrate`, `golang-migrate`, `dbmate`, `liquibase`
- Up/down functions: `def upgrade()` / `def downgrade()`, `exports.up` / `exports.down`
- Migration runner commands: `alembic upgrade head`, `flyway migrate`, `knex migrate:latest`
- `ALTER TABLE`, `CREATE TABLE`, `DROP TABLE` in numbered or versioned scripts
- Schema version tracking table: `alembic_version`, `flyway_schema_history`, `schema_migrations`
- Migration generation commands: `alembic revision --autogenerate`, `knex migrate:make`

### Confidence

- **high** -- migration framework configured with versioned up/down scripts and a schema version tracking table
- **medium** -- numbered SQL files exist in a migrations directory but no framework manages execution order
- **low** -- ad-hoc `ALTER TABLE` statements in deployment scripts without versioning or rollback support

## Architecture

Look for versioned, reversible schema changes managed by a migration framework with a clear execution order and rollback path.

### Review Checklist

- Every schema change is a versioned migration file -- no manual DDL against production
- Migrations are backward-compatible: old application code can run against the new schema during rolling deployments
- Down/rollback migrations are implemented and tested, not left as stubs
- Migrations run in a transaction where the database supports transactional DDL
- Large table migrations use online DDL or batched operations to avoid locking
- Migration execution is idempotent -- running the same migration twice does not fail or corrupt state

### Anti-patterns

- Schema changes applied directly to production without migration files
- Migrations that break backward compatibility (dropping columns still referenced by running code)
- No rollback path -- down migrations are empty or missing entirely
- Coupling data migrations with schema migrations in the same file (mixing DDL and bulk DML)

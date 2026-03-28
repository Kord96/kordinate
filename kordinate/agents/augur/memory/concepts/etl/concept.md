---
description: ETL architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [data]
---
# ETL/ELT


## Recognition

How to identify this pattern in code.

### Signatures

- Airflow `DAG` definitions with operators (`PythonOperator`, `BashOperator`, `SqlOperator`)
- dbt project structure with `models/` directory containing SQL transformations
- Luigi `Task` classes with `requires()` and `output()` methods
- Prefect `@flow` and `@task` decorators defining pipeline steps
- Dagster `@op` and `@job` decorators for pipeline operations
- AWS Glue jobs or crawlers in infrastructure configuration
- `pandas` pipelines with read/transform/write stages (e.g., `read_csv` -> transformations -> `to_sql`)

### Negative signals (not sufficient for detection)

- The acronym `ETL` or word `Extract` alone is NOT the ETL pattern. Look for dedicated pipeline framework imports or explicit extract-transform-load stages.
- Method names like `extractValue()`, `extractField()`, `transformRequest()` are generic naming, not ETL.
- Java: `import` statements, build tool configurations, or archive extraction utilities are not ETL.
- Go: `extract` or `transform` as function names in non-data-pipeline contexts (config parsing, string manipulation) are not ETL.
- Java: Spring Batch `ItemReader`/`ItemProcessor`/`ItemWriter` looks like ETL but is the batch processing pattern. Only flag as ETL if the batch job explicitly implements extract-transform-load stages between different data stores.
- Java: `LoadAccountPort`, `loadData()`, or methods with `load` in the name are NOT ETL unless part of a data pipeline.
- The word `load` in any language (class loading, module loading, config loading, lazy loading) is NOT ETL.
- Go: `Load()`, `Extract()`, `Transform()` methods in non-data-pipeline contexts are generic method names, not ETL.

### Confidence

- **high** -- dedicated pipeline framework (Airflow, dbt, Dagster) with explicit extract, transform, and load stages, checkpoint tracking, and idempotent loads
- **medium** -- scheduled scripts performing data extraction and loading with some checkpoint logic but no formal pipeline framework
- **low** -- ad-hoc data processing scripts that read from one source and write to another without explicit staging, checkpointing, or idempotency guarantees

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

---
description: Data pipeline flow — linear transformation stages from source to sink
type: flow-shape
abstraction: [data, integration]
---
# Data Pipeline

## Recognition

### Signatures

- ETL/ELT patterns: extract → transform → load
- Airflow DAGs, Prefect flows, Dagster pipelines, Luigi tasks
- Spark jobs with `read` → `filter` → `map` → `groupBy` → `write` chain
- dbt models with `ref()` dependencies forming a DAG
- Pandas/Polars DataFrames with chained transformations
- Kafka Streams `topology.addSource().addProcessor().addSink()`
- Step Functions or workflow engine with sequential stages
- Source → staging → cleaned → enriched → target table progression
- Batch job schedulers (cron, k8s CronJob) triggering data processing

### Confidence

- **high** — explicit pipeline framework (Airflow, dbt, Spark) with defined stages and dependencies
- **medium** — sequential data transformations with clear source → sink but no pipeline framework
- **low** — ad-hoc scripts that read, transform, and write data without pipeline structure

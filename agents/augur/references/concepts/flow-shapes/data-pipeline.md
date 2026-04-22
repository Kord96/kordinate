---
kind: concept
name: data-pipeline
signatures: {}
source:
  memory_concept: memory/catalog/concepts/data-pipeline.md
type: flow-shape
abstraction:
- data
- integration
scope: cross-cutting
status: primary
---

# Explanation

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

### Relationship To Other Concepts

- Related to [batch-processing](/concepts/batch-processing) when the pipeline advances in scheduled chunks rather than continuously.
- Related to [etl](/concepts/etl) because many data pipelines implement extract-transform-load stages explicitly.
- Related to [stream-to-store](/concepts/stream-to-store) when one pipeline mode ingests streams continuously into storage or projections.

### Boundary

Use `data-pipeline` when data moves through a deliberate series of transformation stages from one or more sources toward one or more sinks.

Do not use it for any multi-step function. The important signal is staged data movement as an architectural flow.

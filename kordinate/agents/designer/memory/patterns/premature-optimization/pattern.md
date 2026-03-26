---
description: Premature Optimization anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Premature Optimization

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Caching layer introduced before measuring whether latency is actually a problem
- Denormalized tables or materialized views created before hitting scale thresholds
- Complex data structures (tries, bloom filters, skip lists) used for small datasets that fit comfortably in a linear scan
- Hand-rolled serialization or binary protocols for "performance" instead of standard JSON/protobuf
- Micro-benchmarks driving architecture decisions without production traffic profiles

### Confidence

- **high** -- complex optimization infrastructure exists but profiling data shows the optimized path accounts for less than 5% of total latency
- **medium** -- caching, denormalization, or custom data structures present with no accompanying benchmarks or load test results
- **low** -- comments referencing "performance" or "efficiency" on code that handles low-traffic paths or small datasets

## Impact

Unnecessary complexity added without proven need, increasing maintenance cost while delivering negligible benefit.

### Symptoms

- Code is harder to understand because of optimization layers that obscure intent
- Bugs hide in custom serialization or caching invalidation logic
- New features require working around optimization constraints that were never necessary
- Team spends time maintaining cache coherency for data that changes rarely and loads in milliseconds without caching
- Architecture is rigid because premature optimization locked in early design decisions

### Remediation

- Measure first: profile production workloads before introducing any optimization
- Start with the simplest correct implementation and optimize only proven bottlenecks
- Remove caching layers, denormalized tables, or custom data structures that lack supporting performance data
- Document the performance requirement that justifies each optimization with concrete numbers
- Use standard library data structures and serialization formats unless benchmarks prove them insufficient

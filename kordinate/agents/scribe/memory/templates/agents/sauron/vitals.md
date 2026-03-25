# <Project> — Vitals

> **Maintain this document when health checks are added or modified.**

## Architecture

Describe how health checks compose: per-process flags -> section flags -> composite status.
Include the section tree diagram.

## Status Values

Document the tri-state gauge and any project-specific status metrics.

| Value | Meaning | Condition |
|-------|---------|-----------|
| 0 | FAIL | ... |
| 1 | STUCK/WARN | ... |
| 2 | OK | ... |

## Loki Label Schema

Document how to address components in Loki queries for this project.

## Start Here

The first query to run when debugging — typically the vitals's own transition logs.

## Sections

For each health check section, combine thresholds and debug info:

### <Section Name>

**Thresholds**

| Check | OK | WARN | FAIL |
|-------|----|------|------|

**Debug**

| Check | Triggers | Loki Query | Key Events |
|-------|----------|------------|------------|

Notes on logging gaps or special behavior for this section.

## Process-Level (Cross-Cutting)

Generic debugging patterns that apply across all components (FAIL, STUCK, crash loops).

## Logging Gaps

Document what CANNOT be diagnosed via logs alone and requires Prometheus or kubectl.

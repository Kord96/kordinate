---
description: nokrashi-tools library reference
curated: true
scope: global
preloaded: none
---
# nokrashi-tools — Testing Perspective

Code quality checks and test analysis toolkit. This IS sauron's primary testing tool.

## Purpose

Pytest-based standards enforcement + project analysis with coverage, dead code, security, mock quality, and mutation testing.

## Key Components

| Component | Role |
|-----------|------|
| TestSuite | Unified check runner — creates pytest test class for a project |
| analyze_project | Run all analysis tools, return prioritized report |
| GrafanaIntegration | Dashboard panel interval validation |
| extract_metrics_from_promql | Extract metric names from PromQL for coverage checks |

## How to Use

1. Install: `pip install nokrashi-tools`
2. Create `test_standards.py` in the project using TestSuite
3. Run: `pytest test_standards.py -v`
4. Fix violations (don't just report them)

## Validation Workflow

1. Run TestSuite for coding standards
2. Run analyze_project for deeper analysis (coverage gaps, dead code, security)
3. Use GrafanaIntegration to validate dashboard panel query intervals
4. Use extract_metrics_from_promql + Grafana MCP to find unused/missing metrics
5. Fix everything, re-run until green

## Self-Test

```
pytest tests/ -v
```

nokrashi-tools tests itself — no external test framework needed.

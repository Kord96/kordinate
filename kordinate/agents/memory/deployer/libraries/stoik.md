# stoik — Deployment Perspective

Stream-to-store pipeline framework. Used by consumer components.

## Install

```
pip install stoik        # core
pip install stoik[all]   # includes flight deps
```

PyPI: `stoik`. Deploy method: `git-branch` (trusted publishing via GitHub Actions OIDC).

## Components

Projects using stoik typically have multiple consumer components (one per data type/topic) plus a FlightSQL server for query access.

Each consumer runs as a separate k8s Deployment, sharing the same base image.

## Deployment Notes

- All consumers use the same Docker image — component selection via entrypoint/args
- FlightSQL server needs the `stoik[all]` extras (flight dependencies)
- Buffer flush depends on DuckDB — ensure PVC is bound before scaling up
- Consumer lag may spike during rollout restarts — expected, recovers after rebalance

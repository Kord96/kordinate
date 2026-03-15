# klog — Deployment Perspective

Structured logging library. Dependency for all Python services.

## Install

```
pip install klog
```

PyPI: `klog`. Deploy method: `git-branch` (trusted publishing via GitHub Actions OIDC).

## Deployment Notes

- klog is a library dependency, not a standalone service — no pods to manage
- All Python services should include klog in their requirements
- configure_logging must be called at startup for structured JSON output (required for Alloy/Loki ingestion)
- APIPushHandler (if used) needs network access to the target API endpoint — check NetworkPolicy

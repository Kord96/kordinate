---
description: Recommended first-pass bundle splits for Alfred, Charon, Sauron, and Warden
---

# Agent Bundle Migration Plan

This plan applies the shared bundle methodology to the current specialist agents.

## Alfred

Default deployed selection:
- `memory_bundle: operate-direct-v1`
- `skill_bundle: get-store-core-v1`
- `runtime_bundle: direct-action-v1`

First-pass structure:
- `INDEX.yaml`
- `memory/workflow.md`
- `memory/contracts.md`
- `memory/indexes/paths.md`
- `memory/indexes/key-paths.md`
- `bundles/memory/operate-direct-v1.md`
- `bundles/memory/platform-admin-v1.md`
- `bundles/memory/secrets-heavy-v1.md`
- `bundles/skill/get-store-core-v1.md`
- `bundles/skill/validation-core-v1.md`
- `bundles/runtime/direct-action-v1.md`

## Charon

Recommended default deployed selection:
- `memory_bundle: platform-core-v1`
- `skill_bundle: platform-ops-v1`
- `runtime_bundle: ops-default-v1`

Recommended first bundles:
- `bundles/memory/platform-core-v1.md`
- `bundles/memory/operations-core-v1.md`
- `bundles/memory/observability-platform-v1.md`
- `bundles/skill/platform-ops-v1.md`
- `bundles/skill/deployment-lifecycle-v1.md`
- `bundles/skill/bootstrap-v1.md`
- `bundles/runtime/ops-default-v1.json`

## Sauron

Recommended default deployed selection:
- `memory_bundle: observe-core-v1`
- `skill_bundle: monitor-core-v1`
- `runtime_bundle: observe-terse-v1`

Recommended first bundles:
- `bundles/memory/observe-core-v1.md`
- `bundles/memory/dashboard-audit-v1.md`
- `bundles/memory/operate-workflow-v1.md`
- `bundles/skill/monitor-core-v1.md`
- `bundles/skill/design-monitoring-core-v1.md`
- `bundles/runtime/observe-terse-v1.json`

## Warden

Recommended default deployed selection:
- `memory_bundle: core-v1`
- `skill_bundle: core-v1`
- `runtime_bundle: default-v1`

Recommended first bundles:
- `bundles/memory/core-v1.md`
- `bundles/skill/core-v1.md`
- `bundles/skill/validation-v1.md` when a stricter validator profile is needed
- `bundles/runtime/default-v1.md`

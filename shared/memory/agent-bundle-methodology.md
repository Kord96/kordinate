---
description: Standard cross-agent methodology for identity, INDEX manifests, and memory/skill/runtime bundle selection
---

# Agent Bundle Methodology

This document standardizes the Augur-style prompt-surface model for all agents.

Goal:
- keep caller-facing identity stable
- make always-on context explicit
- let deployments select small, named bundles instead of relying on long ad hoc identity files
- avoid drift between runtime seeding, daemon prompt composition, and repo layout

## Model

Every agent should be structured around five layers:

1. `IDENTITY.md`
   Stable role, capabilities, hard rules, and operating style.

2. `INDEX.yaml`
   Declares what is preload, on-demand, or runtime-only.

3. `bundles/memory/`
   Stable domain context and source-of-truth rules that should often be preloaded.

4. `bundles/skill/`
   Reusable procedural guidance for the agent's common workflows.

5. `bundles/runtime/`
   Small runtime-behavior overlays such as output style, verbosity, or execution posture.

Optional domain-specific bundle families are allowed, but the three common bundle directories above should be the default contract for all agents.

## Ownership

### `IDENTITY.md`

`IDENTITY.md` should own:
- role and purpose
- high-level capabilities
- hard safety or delegation rules
- concise response style expectations
- short lifecycle when needed

`IDENTITY.md` should not carry:
- long path catalogs
- detailed source-of-truth matrices
- procedural checklists for common workflows
- large troubleshooting catalogs
- tool inventories unless they are a hard rule

### `bundles/memory/`

Memory bundles should own:
- domain doctrine
- source-of-truth rules
- path and ownership maps
- invariants and update rules
- stable operating context reused across many tasks

### `bundles/skill/`

Skill bundles should own:
- common procedural flow
- step ordering
- validation expectations
- output shape expectations
- when to delegate to another specialist

### `bundles/runtime/`

Runtime bundles should own:
- terse vs detailed response bias
- execution posture such as direct-action or review-first
- reporting format preferences
- model/runtime-specific behavioral constraints

Runtime bundles should stay small. They are not a substitute for memory or skill bundles.

## Runtime Selection

Deployments should be able to select:
- `memory_bundle`
- `skill_bundle`
- `runtime_bundle`

Selection is carried in agent creation metadata and exposed to the runtime through:
- `AGENT_MEMORY_BUNDLE`
- `AGENT_SKILL_BUNDLE`
- `AGENT_RUNTIME_BUNDLE`

`deploy-runtime.sh` generates a deterministic `AGENT.md` from `INDEX.yaml` in the agent runtime home.

`AGENT.md` is the canonical seeded context entrypoint.

`CLAUDE.md` is only a compatibility shim for runtimes that still look for it and should normally contain a single `@AGENT.md` reference.

The daemon should load seeded context from canonical repo/image bundle sources, not duplicated mutable runtime bundle files.

## `INDEX.yaml`

Every specialist agent should add `INDEX.yaml`.

Use it to declare:
- `preload`
  Stable, high-value context intended for deterministic bundle generation.
- `ondemand`
  Detailed skills, catalogs, scripts, or references that should remain available but not always loaded.
- `runtime`
  Mutable state, generated artifacts, and per-run scratch data.

`INDEX.yaml` is the static content manifest. Bundle selection is a deployment/runtime concern layered on top.

## Recommended Migration Order

1. Alfred
   Clear direct-action agent with small domain and immediate payoff from bundle discipline.

2. Charon
   Operational detail is currently too concentrated in identity and memory files.

3. Sauron
   Monitoring doctrine and procedural workflows split cleanly into memory and skill bundles.

4. Warden
   Small, clear security validator that benefits from a compact default profile.

5. Generic
   Add a minimal generic identity and default bundle set once specialist patterns are stable.

## Naming Guidance

Prefer explicit, versioned names:
- `operate-direct-v1`
- `platform-core-v1`
- `monitor-core-v1`
- `default-v1`

Bundle names should describe the behavior or doctrine, not the file format.

## Standard Deployment Defaults

For most agents, the default deployed selection should be:
- one core memory bundle
- one core skill bundle
- one small runtime bundle

Additional bundles should only be selected when the deployment is intentionally specialized.

---
description: Story-based documentation system design — pipeline, schema, ownership decisions (2026-03-29)
curated: true
---

# Story System Design

Decided 2026-03-29. Replaces the old 5-skill pipeline + fixed 4-tab explorer.

## Pipeline

```
/analyze (Augur)
  Phase 1: Detect → atlas.json v3
  Phase 2: Compose → stories/*.yaml
                    ↓
/document (Scribe)
  Reads atlas + stories → visualization decisions → interactive docs
```

## Core Concepts

- **Story**: Augur's core analytical concept — a scoped understanding of one codebase aspect
- **Dimensions**: structure, flows, data, resilience, observations, highlights
- **Stories carry zero visualization hints** — Scribe makes all rendering decisions
- **Atlas**: full structural inventory (v3 JSON) — nodes, edges, state, external deps, concepts, debt, API surface, module graph

## Story Types

| Type | Count | Required dimension |
|------|-------|--------------------|
| structure | 3-5 | structure |
| flow | 2-4 | flows |
| data | 0+ | data |
| resilience | 0+ | resilience |
| highlight | 0+ | highlights |

## Evaluation

- **Groundedness** >= 0.85: % of claims traceable to atlas detection findings
- **Coverage** >= 0.80: % of critical atlas nodes referenced across all stories

## Key Files

**Augur** (w2 worktree, complete):
- `kordinate/agents/augur/skills/analyze/SKILL.md` — unified 14-step procedure
- `kordinate/agents/augur/skills/analyze/augur-output-contract.md` — stable interface for consumers
- `kordinate/agents/augur/skills/analyze/story-schema.md` — story YAML schema
- `kordinate/agents/augur/skills/analyze/schema.md` — atlas.json v3 schema

**Scribe** (w3 worktree, complete):
- `kordinate/agents/scribe/skills/document/SKILL.md` — rewritten for stories + atlas
- `kordinate/agents/scribe/skills/document/explorer-schema.md` — input schema docs

## Breaking Changes

- Augur IDENTITY.md renamed from "designer" to "augur"
- `/analyze` replaces 5 old skills: detect-patterns, map-dependencies, review-api, assess-debt, architect
- Output: atlas.json + stories/*.yaml replaces architecture.yaml + 4 markdown reports
- Scribe /document consumes stories instead of architecture.yaml

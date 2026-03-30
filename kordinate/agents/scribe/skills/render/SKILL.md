---
name: render
description: >
  Render augur's analysis into documentation. Fetches atlas + stories + journeys via kord,
  makes visualization decisions, and generates Astro pages. Use --manifest-only to produce
  just the manifest without Astro output.
argument-hint: "<project> [--manifest-only]"
context: fork
---

Render a project's architecture documentation from augur's analysis output. All input is fetched through kord — scribe never reads augur's files directly.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional: `--manifest-only` to produce manifest.json + storyByNode.json without generating Astro pages.

## Input

All input acquired through kord by delegating to augur:

| Resource | Purpose |
|----------|---------|
| `atlas-schema` | Atlas v4 format definition |
| `story-schema` | Story/journey format definition |
| `atlas` | Structural inventory for the project |
| `stories` | Story files with building blocks |
| `journeys` | Reading paths (getting-started, etc.) |

If atlas is missing, suggest running `/analyze <project>`. Exit.

## Procedure

### 1. Fetch

Fetch all input via kord delegation to augur. Parse atlas JSON, story YAML, journey YAML.

### 2. Build manifest

For each story's building blocks, decide the rendering approach:

**Structures** — by node count:
- 1-3 nodes: `grid`
- 4-8 nodes: `dagre`
- 9+ nodes: `cose-bilkent`

**Flows** — by type:
- `state` or failure cascade: `timeline`
- all others: `sequence`

**Observations** — by content:
- has code snippet: `evidence-card`
- has recommendation: `warning-card`
- otherwise: `compact-card`

**Rationale**: `decision-card`

Write to `<project>/.kord/agents/scribe/output/manifest.json`.

### 3. Build storyByNode index

For each atlas node, find which stories reference it (in structures, flows, observations). Write to `<project>/.kord/agents/scribe/output/storyByNode.json`.

**If `--manifest-only`: stop here and report.**

### 4. Install components

Copy pre-built components from this skill into the docs site:

```bash
mkdir -p $SITE/src/components/kordinate $SITE/src/components/kordinate/lib
cp components/*.astro $SITE/src/components/kordinate/
cp lib/*.ts $SITE/src/components/kordinate/lib/
```

Resolve site location:
1. `$KORDINATE_HOME/../site/` — if exists
2. `site/` in kordinate repo root — if exists
3. Fallback: `<project>/.kord/agents/scribe/output/site/`

### 5. Copy data to site

```bash
mkdir -p $SITE/src/content/docs/<project>
```

Write the fetched atlas, stories, journeys, manifest, and storyByNode to the site content directory.

### 6. Write Astro pages

Each journey becomes one thin page importing JourneyPage component. Atlas page imports AtlasPage component. Read the components from `components/` to understand their props.

### 7. Report

```
## Rendered: <project>

**Manifest**: N stories, N blocks
**storyByNode**: N nodes mapped
**Site**: <path> (if not --manifest-only)
**Pages**: N journey pages + atlas page
```

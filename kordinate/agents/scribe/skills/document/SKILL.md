---
name: document
description: >
  Produce documentation data from augur's analysis. Fetches atlas + stories + journeys
  via kord, validates, makes rendering decisions, and writes manifest.json + storyByNode.json.
  The Astro site consumes these files at build time — no agent involvement in rendering.
argument-hint: "<project>"
context: inherit
---

Produce documentation data files from augur's analysis output. All input is fetched through kord. Output is JSON files that the Astro site auto-consumes at build time.

## Arguments

`$ARGUMENTS` — Required: `<project>` (path to project directory).

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

## Output

All output goes to `<project>/.kord/agents/scribe/output/`:

```
overview.json          — editorial introduction, project context, visual overview
manifest.json          — rendering decisions per story
storyByNode.json       — atlas node ID → story IDs that reference it
```

These files are consumed by the Astro site at build time alongside augur's atlas.json, stories, and journeys.

## Procedure

### 1. Fetch

Fetch all input via kord delegation to augur. Parse atlas JSON, story YAML, journey YAML.

### 2. Generate overview

Scribe's editorial contribution — the layer above augur's code-grounded stories. Read the project's source code (README, docs, key entry points) alongside the atlas to write an overview that orients a newcomer before they see any code.

Write `<project>/.kord/agents/scribe/output/overview.json`:

```json
{
  "introduction": "2-3 sentences max. What this project is and what problem it solves. No code, no jargon.",
  "how_it_works": "3-5 short sentences, one per pipeline stage. Each sentence is one step: 'X happens, then Y, then Z.' Name the groups, not the components. Must be scannable — no paragraphs.",
  "key_decisions": ["One sentence each, max 3-4 decisions. The most important architectural choices."],
  "groups_overview": [
    {
      "id": "<group-id>",
      "name": "<group name>",
      "role": "One sentence — what this group does in plain language, not what components it contains."
    }
  ]
}
```

**Voice:** Write for someone who has never seen the codebase. No `**bold refs**`, no file paths, no function names. Architecture concepts only. This is the "chapter 0" that appears before any story.

**Sources:** Read the project's README.md, any docs/ directory, and augur's atlas purpose + domain_model + groups. The atlas gives you structure; the README gives you intent.

### 3. Validate



Cross-reference check:
- Every node ID in structures exists in atlas
- Every edge from/to exists in the story's nodes
- Every **bold ref** in summaries resolves to an atlas node ID
- Every flow step node/to exists in atlas
- Every observation component exists in atlas
- Every journey story ID exists in stories

### 4. Build manifest

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

### 5. Build storyByNode

For each atlas node, find which stories reference it. Write to `<project>/.kord/agents/scribe/output/storyByNode.json`.

### 6. Report

```
## Documentation: <project>

**Output**: <project>/.kord/agents/scribe/output/
**Manifest**: N stories, N total blocks
**storyByNode**: N nodes mapped
**Coverage**: N of M atlas nodes in stories (N%)
```

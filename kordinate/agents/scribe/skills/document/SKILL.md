---
name: document
description: >
  Produce documentation data from augur's analysis. Fetches atlas + stories + journeys
  via kord, validates cross-references, makes rendering decisions, and writes manifest.json +
  storyByNode.json. Does NOT generate HTML or site files — use /render for that.
argument-hint: "<project>"
context: inherit
---

Produce documentation data files from augur's analysis output. All input is fetched through kord — scribe never reads augur's files directly.

## Arguments

`$ARGUMENTS` — Required: `<project>` (path to project directory).

## Input

All input is acquired through kord by delegating to augur:

| Resource | Required | Purpose |
|----------|----------|---------|
| `schema` | **yes** | Atlas v4 format definition |
| `story-schema` | **yes** | Story/journey format definition |
| `atlas` | **yes** | Structural inventory for the project — abort if missing |
| `stories` | **yes** | Story files with building blocks |
| `journeys` | **yes** | At least getting-started.yaml |

If atlas is missing, suggest running `/analyze <project>`. Exit.

## Output

All output goes to `<project>/.kord/agents/scribe/output/`:

```
manifest.json          — rendering decisions per story
storyByNode.json       — atlas node ID → story IDs that reference it
```

## Procedure

### 1. Fetch and validate

Fetch all input via kord delegation to augur:
- `schema` resource — atlas format definition
- `story-schema` resource — story/journey format definition
- `atlas` resource for the project
- `stories` resource for the project
- `journeys` resource for the project

Validate cross-references:
- Every node ID in structures exists in atlas
- Every edge from/to exists in the story's nodes
- Every **bold ref** in summaries resolves to an atlas node ID
- Every flow step node/to exists in atlas
- Every observation component exists in atlas
- Every journey story ID exists in stories

### 2. Build indices

- **storyByNode**: atlas node ID → story IDs referencing it
- **coverage**: critical atlas nodes appearing in at least one story

### 3. Choose visualizations

For each story's building blocks, decide the rendering approach. Record the decision — don't implement it.

**Structures** — choose by node count:
- 1-3 nodes: `grid`
- 4-8 nodes: `dagre`
- 9+ nodes: `cose-bilkent`

**Flows** — choose by type:
- `state` or failure cascade: `timeline`
- all others: `sequence`

**Observations** — choose by content:
- has code snippet: `evidence-card`
- has recommendation: `warning-card`
- otherwise: `compact-card`

**Rationale**: `decision-card`

### 4. Write manifest.json

Write rendering decisions to `<project>/.kord/agents/scribe/output/manifest.json`.

### 5. Write storyByNode.json

Write the node-to-story index to `<project>/.kord/agents/scribe/output/storyByNode.json`.

### 6. Report

```
## Documentation: <project>

**Output**: <project>/.kord/agents/scribe/output/
**Manifest**: N stories, N total blocks
**Coverage**: N of M atlas nodes in stories (N%)

### Rendering decisions
| Story | Blocks | Decisions |
|-------|--------|-----------|
| ... | ... | ... |
```

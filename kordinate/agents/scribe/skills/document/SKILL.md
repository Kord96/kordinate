---
name: document
description: >
  Produce documentation data from augur's analysis. Reads atlas + stories + journeys,
  validates cross-references, makes rendering decisions, and writes manifest.json +
  storyByNode.json. Does NOT generate HTML or site files — use /render for that.
argument-hint: "<project>"
context: inherit
---

Produce documentation data files from augur's analysis output. Scribe reads the atlas, stories, and journeys, validates everything cross-references correctly, decides how each building block should be visualized, and writes the output as JSON files conforming to [schemas.md](schemas.md).

## Arguments

`$ARGUMENTS` — Required: `<project>` (path to project directory).

## Input

Read from `<project>/.kord/agents/augur/memory/`:

| File | Required | Purpose |
|------|----------|---------|
| `atlas.json` | **yes** | Structural inventory — abort if missing |
| `stories/*.yaml` | **yes** | Story files with building blocks |
| `journeys/*.yaml` | **yes** | At least getting-started.yaml |

If `atlas.json` is missing, suggest running `/analyze <project>`. Exit.

## Output

All output goes to `<project>/.kord/agents/scribe/output/`:

```
manifest.json          — rendering decisions per story
storyByNode.json       — atlas node ID → story IDs that reference it
atlas.json             — copied from augur
stories/*.yaml         — copied from augur
journeys/*.yaml        — copied from augur
```

## Procedure

### 1. Load and validate

Fetch augur's schema definitions via kord to understand the data formats:
- Delegate to augur for `schema` resource (atlas.json v4 format)
- Delegate to augur for `story-schema` resource (story/journey YAML format)

Read `atlas.json`. Read all `stories/*.yaml` and `journeys/*.yaml`. Validate:
- Every node ID in structures exists in atlas
- Every edge from/to exists in the story's nodes
- Every **bold ref** in summaries resolves to an atlas node ID
- Every flow step node/to exists in atlas
- Every observation component exists in atlas
- Every journey story ID exists in stories/

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
- `failure cascade`: `timeline`
- all others: `sequence`

**Observations** — choose by content:
- has code snippet: `evidence-card`
- has recommendation: `warning-card`
- otherwise: `compact-card`

**Rationale**: `decision-card`

### 4. Write manifest.json

Write rendering decisions to `<project>/.kord/agents/scribe/output/manifest.json`. See [schemas.md](schemas.md) for the exact schema.

### 5. Write storyByNode.json

Write the node-to-story index to `<project>/.kord/agents/scribe/output/storyByNode.json`.

### 6. Copy augur data

Copy `atlas.json`, `stories/*.yaml`, and `journeys/*.yaml` from augur's output to scribe's output directory.

### 7. Report

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

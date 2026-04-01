---
name: render
description: >
  Render scribe's documentation data into Astro pages. Reads manifest.json + stories + atlas
  from scribe's output directory and generates pages using pre-built components.
argument-hint: "<project>"
context: fork
---

Generate Astro site pages from scribe's `/document` output. This skill reads the data files (manifest.json, storyByNode.json, atlas.json, stories, journeys) and maps them to pre-built Astro components.

**This skill uses `context: fork`** — it runs in its own context and reads the component files it needs. It does NOT inherit the document skill's context.

## Arguments

`$ARGUMENTS` — Required: `<project>` (path to project directory).

## Input

Read from `<project>/.kord/agents/scribe/output/`:

| File | Required | Purpose |
|------|----------|---------|
| `manifest.json` | **yes** | Rendering decisions from /document |
| `storyByNode.json` | **yes** | Node-to-story index |
| `atlas.json` | **yes** | Structural inventory |
| `stories/*.yaml` | **yes** | Story data |
| `journeys/*.yaml` | **yes** | Journey data |

If `manifest.json` is missing, suggest running `/document <project>` first. Exit.

## Output

Resolve the docs site location:
1. `$KORDINATE_HOME/../site/` — if it exists
2. `site/` in kordinate repo root — if it exists
3. Fallback: `<project>/.kord/agents/scribe/output/site/`

Write Astro pages that import pre-built components and pass them the data.

## Components

Pre-built components in this skill's `components/` directory. Read them to understand their props and rendering logic.

| Component | Props | Purpose |
|-----------|-------|---------|
| `JourneyPage.astro` | project, journeys, storiesByJourney, atlas, rendering | Full explorer: tabs, sidebar, canvas, drawer |
| `StoryCard.astro` | story, atlas, rendering | One story section with all building blocks |
| `GraphBlock.astro` | id, nodes, edges, atlas, structureType | Interactive graph |
| `SequenceDiagram.astro` | id, steps, title | Mermaid sequence diagram |
| `TimelineCard.astro` | title, trigger, severity, cascade, detection, recovery | Failure cascade |
| `ObservationCard.astro` | finding, confidence, component, evidence, tags, recommendation, type | Evidence/warning card |
| `RationaleCard.astro` | decision, context, trade_offs, alternatives | Design decision card |
| `AtlasPage.astro` | project, atlas, storyByNode, stories | Full interactive atlas graph |
| `BottomDrawer.astro` | (none) | Drawer shell for detail panels |

Supporting files in `lib/`:
- `cytoscape-config.ts` — node type colors, shapes, severity colors
- `narrative.ts` — bold-ref parsing, HTML escaping

## Procedure

### 1. Install components

Copy components and lib from this skill into the site:

```bash
mkdir -p $SITE/src/components/kordinate $SITE/src/components/kordinate/lib
cp components/*.astro $SITE/src/components/kordinate/
cp lib/*.ts $SITE/src/components/kordinate/lib/
```

### 2. Copy data to site content

```bash
mkdir -p $SITE/src/content/docs/<project>
cp <project>/.kord/agents/scribe/output/atlas.json $SITE/src/content/docs/<project>/
cp <project>/.kord/agents/scribe/output/manifest.json $SITE/src/content/docs/<project>/
cp <project>/.kord/agents/scribe/output/storyByNode.json $SITE/src/content/docs/<project>/
cp -r <project>/.kord/agents/scribe/output/stories $SITE/src/content/docs/<project>/
cp -r <project>/.kord/agents/scribe/output/journeys $SITE/src/content/docs/<project>/
```

### 3. Write journey pages

Each journey becomes one thin Astro page importing JourneyPage:

```astro
---
import JourneyPage from '../../components/kordinate/JourneyPage.astro';
import atlas from '../../content/docs/<project>/atlas.json';
import manifest from '../../content/docs/<project>/manifest.json';
const journeys = [/* loaded from journeys/*.yaml */];
const storiesByJourney = {/* journeyId → ordered stories */};
---
<JourneyPage project="<project>" journeys={journeys} storiesByJourney={storiesByJourney} atlas={atlas} rendering={manifest} />
```

Output: `$SITE/src/pages/<project>/index.astro` (default journey) + additional journey pages.

### 4. Write atlas page

```astro
---
import AtlasPage from '../../../components/kordinate/AtlasPage.astro';
import atlas from '../../../content/docs/<project>/atlas.json';
import storyByNode from '../../../content/docs/<project>/storyByNode.json';
---
<AtlasPage project="<project>" atlas={atlas} storyByNode={storyByNode} stories={[]} />
```

Output: `$SITE/src/pages/<project>/atlas/index.astro`

### 5. Report

```
## Rendered: <project>

**Site**: <site path>
**Journey pages**: N
**Atlas page**: <path>
**Components installed**: yes
```

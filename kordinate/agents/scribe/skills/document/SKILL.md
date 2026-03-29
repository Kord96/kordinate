---
name: document
description: >
  Render stories into interactive documentation pages. Reads Augur's atlas + stories
  and produces an Astro docs site with per-story pages, an atlas explorer, journey
  navigation, and a facts index. All visualization decisions are Scribe's.
argument-hint: "<project> [--atlas-only]"
curated: true
scope: global
context: fork
---

Render a project's stories and atlas into an interactive documentation site. Scribe makes all visualization decisions — Augur's stories carry analytical content with zero rendering hints.

## Arguments

`$ARGUMENTS` — Required: `<project>` (e.g., `sous-storefront`, `stoik`). Optional: `--atlas-only` to render only the atlas page (skip story pages).

## Input

Read from `<project>/.kord/agents/augur/memory/`:

| File | Required | Purpose |
|------|----------|---------|
| `atlas.json` | **yes** | Full structural inventory — abort if missing |
| `stories/*.yaml` | **yes** (unless `--atlas-only`) | Story files — abort if directory empty |

If `atlas.json` is missing, report and suggest running `/analyze <project>`. Exit.

If stories/ is empty (and not `--atlas-only`), report and suggest running `/analyze <project>` (without `--detect-only`). Exit.

## Procedure

### 1. Load and validate

Read `atlas.json`. Build lookup indices:
- `nodeMap`: node.id → node
- `groupMap`: group.id → group
- `stateMap`: state.id → state
- `failureMap`: failure_modes.id → failure

Read all `stories/*.yaml`. For each story, validate:
- Every `structure.nodes[]` ID exists in atlas
- Every `structure.edges[]` source/target exists in story's nodes
- Every `**bold ref**` in narratives resolves to an atlas node ID
- Every `flows[].steps[].from/to` exists in story's nodes
- Every `data.stores[].readers/writers` exist in story's nodes
- Every `resilience.failures[].cascade[].component` exists in story's nodes
- Every `observations[].component` exists in atlas
- Every `narrative_map` entry covers a real paragraph

Report validation errors and continue with valid stories.

### 2. Build cross-reference indices

- **storyByNode**: atlas node ID → list of stories that reference it
- **storyByStory**: story ID → list of stories that reference it (via prerequisites or observation.related)
- **factIndex**: all observations + highlights across all stories, each tagged with source story ID
- **coverage**: which critical atlas nodes (components + external deps with criticality=critical + state with purpose=source-of-truth) appear in at least one story

### 3. Choose visualizations per story

For each story, examine the dimensions present and decide how to render each one. These are guidelines, not rules — adapt to the content.

**Structure dimension:**

| Content shape | Visualization |
|---------------|---------------|
| 2-4 nodes in a chain | Dagre graph, left-to-right |
| 5-10 nodes with hierarchy | Cose-bilkent graph with parent grouping |
| 10+ nodes | Cose-bilkent with collapsed groups, expand on click |
| 1-2 nodes | No graph — inline description cards |

**Flows dimension:**

| Content shape | Visualization |
|---------------|---------------|
| 2-5 step linear flow | Mermaid sequence diagram |
| 6+ steps or branching | Full-width Mermaid sequence diagram with participant grouping |
| Single request-response | Inline step table (no diagram) |

**Data dimension:**

| Content shape | Visualization |
|---------------|---------------|
| 1 store, 1-2 readers/writers | Inline table |
| 2+ stores or 3+ readers/writers | Cytoscape store graph (barrel nodes, read/write colored edges) |
| Stores across purposes | Store graph with purpose group containers |

**Resilience dimension:**

| Content shape | Visualization |
|---------------|---------------|
| 1 failure, simple cascade | Inline callout card with cascade list |
| 2+ failures or deep cascades | Timeline cards (trigger → cascade → detection → recovery) |

**Observations:**

| Content shape | Visualization |
|---------------|---------------|
| Observation with snippet | Evidence card: finding + syntax-highlighted code + confidence badge |
| Observation without snippet | Compact card: finding + file:line link + confidence badge |
| Gap observation | Warning-styled card with recommendation |

**Highlights:**

Always render as callout cards at the top of the story page. Use severity-style coloring:
- Positive findings (pattern matches, good decisions): blue/green
- Warnings (gaps, missing patterns): amber
- Critical issues: red

### 4. Render story pages

For each story, produce a self-contained Astro page at `<docs-pages-dir>/<project>/stories/<story-id>/index.astro`.

**Page layout:**

```
+------------------------------------------------------------------+
|  [project] / [story title]                     [journey: N of M]  |
+------------------------------------------------------------------+
|                                                                    |
|  [Highlights — callout cards]                                      |
|                                                                    |
|  ## Structure                                                      |
|  [graph/cards]  [narrative with cross-highlighting]                |
|                                                                    |
|  ## How Data Flows                     (only if flows dimension)   |
|  [sequence diagram]  [narrative with step badges]                  |
|                                                                    |
|  ## Where Data Lives                   (only if data dimension)    |
|  [store graph/table]  [narrative]                                  |
|                                                                    |
|  ## What Can Break                     (only if resilience dim)    |
|  [timeline cards/callouts]  [narrative]                            |
|                                                                    |
|  ## What We Found                      (only if observations)      |
|  [evidence cards]                                                  |
|                                                                    |
|  [← Previous story]              [Next story →]                    |
+------------------------------------------------------------------+
```

**Section order**: Highlights → Structure → Flows → Data → Resilience → Observations. Skip sections for dimensions not present in the story.

**Section headings**: Use descriptive headings, not dimension names. "How Data Flows" not "Flows". "What Can Break" not "Resilience". Adapt the heading to the story content — a story about auth might use "Authentication Flow" instead of "How Data Flows".

### 5. Implement cross-highlighting

The core interaction pattern preserved from the current explorer:

**Narrative → Graph:**
- Parse `**bold text**` in narratives into `<span class="node-ref" data-node-id="...">` elements
- On click, highlight the corresponding node in the nearest graph (add `hover-glow` class)
- On hover, show a tooltip with node description

**Narrative → Flow steps (narrative_map):**
- Render step badges (`<span class="step-badge">1–3</span>`) on each paragraph
- On paragraph hover, highlight corresponding rows in the step table
- On step row hover, highlight the paragraph that covers those steps

**Graph → Bottom panel:**
- On node click, show a detail panel: name, type, description, file, patterns, debt, endpoints, observations about this node
- Panel slides up from bottom or appears inline below the graph

### 6. Render the atlas page

Produce `<docs-pages-dir>/<project>/atlas/index.astro`.

This is the full interactive graph — migrated from the current ArchExplorer structure tab. It uses the same Cytoscape.js configuration:

- Cose-bilkent layout with expand/collapse hierarchy
- Node types colored by `typeConfig` (service=blue, external=red, store=amber, etc.)
- Debt rings, pattern badges, tooltips
- Breadcrumb navigation for graph hierarchy
- Zoom, pan, fit-to-screen controls

**New additions for story integration:**
- Hovering a node shows "Referenced in N stories" badge
- Clicking a node shows a detail panel with "Stories about this component" links
- A "Story lens" dropdown: selecting a story highlights only its nodes, dimming the rest
- Coverage indicator: nodes not referenced by any story get a dashed border

### 7. Render the journey index

Produce `<docs-pages-dir>/<project>/index.astro`.

Read journey files from `<project>/.kord/agents/augur/memory/journeys/*.yaml` if they exist. If no journey files, auto-generate a default journey ordered: structure stories → flow stories → data stories → resilience stories → highlight stories.

**Layout:** Cards grouped by journey. Each card shows:
- Story title
- `teaches` summary
- Audience tags as pills
- Dimension icons (which dimensions the story covers)
- Prerequisites shown as "Requires: [story links]"

### 8. Render the facts index

Produce `<docs-pages-dir>/<project>/facts/index.astro`.

Build from the `factIndex` (step 2). Each entry shows:
- Finding text
- Source story (linked)
- Component (linked to atlas)
- Evidence file:line (if available)
- Confidence badge
- Tags as pills

The page includes:
- Text search across findings
- Filter by tag, by story, by observation type, by confidence
- Sort by confidence (default), by component, by story

### 9. Graph rendering strategy

**Build time** (Astro build):
- For each graph block, run Cytoscape layout headless (cose-bilkent or dagre depending on step 3 decision)
- Serialize computed node positions
- Emit a static SVG with correct colors, shapes, edge paths, and labels
- Embed SVG inline in the page

**Runtime** (on interaction):
- When user hovers or clicks the SVG, lazy-load Cytoscape.js + dagre from CDN
- Initialize with pre-computed positions (`layout: { name: 'preset' }`) — instant, no layout cost
- Enable: hover tooltips, click-to-select, node-ref highlighting, detail panel
- Only one graph interactive at a time per page (destroy when scrolled past)

**Mobile** (<768px):
- SVG only, no Cytoscape upgrade
- Pinch-to-zoom on SVGs
- Sequence diagrams: horizontal scroll
- Atlas page: show static overview SVG with "View on desktop for interactive atlas" message

### 10. Path resolution

Resolve docs site location (in order):
1. If `$KORDINATE_HOME/../site/` exists → use it
2. If `site/` exists in the kordinate repo root → use it
3. Fallback: `<project>/.kord/agents/scribe/output/docs/`

Within the resolved docs root:
- Pages: `src/pages/<project>/` (index, atlas/, stories/, facts/)
- Content: `src/content/docs/<project>/` (atlas.json copy, story data)

### 11. Technical requirements

**Astro pages:**
- Self-contained: inline all JS/CSS
- Load Cytoscape.js, dagre layout, and Mermaid from CDN (lazy, on interaction)
- CSS custom properties for theming (dark/light mode)
- Responsive: story pages work on mobile, atlas degrades gracefully

**Node type styling** (carried over):

| Type | Color | Shape |
|------|-------|-------|
| `service` | Blue (#3B82F6) | Rounded rectangle |
| `library` | Slate (#64748B) | Rounded rectangle |
| `worker` | Indigo (#6366F1) | Rounded rectangle |
| `api` | Green (#22C55E) | Rounded rectangle |
| `frontend` | Purple (#A855F7) | Rounded rectangle |
| `cli` | Slate (#64748B) | Diamond |
| `store` | Amber (#F59E0B) | Cylinder |
| `gateway` | Rose (#F43F5E) | Hexagon |
| `broker` | Orange (#F97316) | Hexagon |
| `external` | Red (#EF4444) | Octagon |
| `actor` | Teal (#14B8A6) | Ellipse |

**Severity colors:**
- Critical: Red (#EF4444)
- High: Orange (#F97316)
- Medium: Amber (#F59E0B)
- Low: Green (#22C55E)

**Confidence badges:**
- High: solid green pill
- Medium: outline amber pill
- Low: outline gray pill

### 12. Report

```
## Documentation: <project>

**Atlas page**: <path>
**Story pages**: <path> (N stories)
**Journey index**: <path>
**Facts index**: <path> (N observations indexed)

### Stories rendered
| Story | Type | Dimensions | Visualizations chosen |
|-------|------|------------|----------------------|
| SSR Hydration | flow | structure, flows, data, observations | dagre graph, sequence diagram, inline table, 2 evidence cards |
| Cart Lifecycle | flow | structure, flows, data, resilience | cose-bilkent graph, sequence diagram, store graph, timeline card |
| ... | ... | ... | ... |

### Coverage
- Atlas nodes: N total, M referenced in stories (<percentage>%)
- Undocumented critical nodes: [list or "none"]

### Notes
- <any warnings, validation errors, missing stories>
```

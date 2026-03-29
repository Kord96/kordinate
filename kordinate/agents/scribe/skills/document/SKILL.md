---
name: document
description: >
  Render stories into interactive documentation. Reads Augur's atlas + stories + journeys
  and produces documentation pages. Stories render as short sections within journey pages.
  All visualization decisions are Scribe's.
argument-hint: "<project> [--atlas-only]"
curated: true
scope: global
context: fork
---

Render a project's stories and atlas into interactive documentation. Scribe makes all visualization decisions — stories carry analytical content with zero rendering hints.

Stories are **short sections**, not full pages. A journey page contains its stories as sequential sections. Each story section has a summary and 1-3 visual building blocks.

## Arguments

`$ARGUMENTS` — Required: `<project>` (e.g., `sous-storefront`, `stoik`). Optional: `--atlas-only` to render only the atlas page.

## Input

Read from `<project>/.kord/agents/augur/memory/`:

| File | Required | Purpose |
|------|----------|---------|
| `atlas.json` | **yes** | Full structural inventory — abort if missing |
| `stories/*.yaml` | **yes** (unless `--atlas-only`) | Story files |
| `journeys/*.yaml` | no | Reading paths — auto-generate if missing |

If `atlas.json` is missing, suggest running `/analyze <project>`. Exit.

## Procedure

### 1. Load and validate

Read `atlas.json`. Build lookup indices: `nodeMap`, `groupMap`, `stateMap`, `failureMap`.

Read all `stories/*.yaml`. For each story, validate:
- Every node ID in `structures[].nodes[].id` exists in atlas
- Every edge `from`/`to` exists in story's nodes
- Every `**bold ref**` in summary resolves to an atlas node ID
- Every `flows[].steps[].node` and `.to` exists in atlas
- Every `observations[].component` exists in atlas
- Every `observation_ids` reference points to a defined observation

Read `journeys/*.yaml`. If none exist, auto-generate a default journey from all stories.

### 2. Build indices

- **storyByNode**: atlas node ID → stories referencing it
- **factIndex**: all observations across all stories, tagged with source story
- **coverage**: critical atlas nodes appearing in at least one story

### 3. Choose visualizations per building block

For each story, examine its building blocks and decide rendering. The block `type` field guides the choice — unknown types get generic rendering.

**Structures:**

| Type | Visualization |
|------|---------------|
| `component topology` | Cytoscape graph (dagre or cose-bilkent based on node count) |
| `data lineage` | Cytoscape graph with colored read/write edges |
| `infrastructure` | Cytoscape graph with k8s-style icons |
| `security boundary` | Cytoscape graph with zone shading |
| `module graph` | Compact dependency list or dagre graph |
| _(unknown type)_ | Dagre graph |

Sizing by node count:
- 1-3 nodes: inline diagram, no interactive graph
- 4-8 nodes: small dagre graph
- 9+ nodes: full cose-bilkent with expand/collapse

**Flows:**

| Type | Visualization |
|------|---------------|
| `request path` | Mermaid sequence diagram |
| `data pipeline` | Mermaid sequence diagram |
| `failure cascade` | Timeline card (trigger → cascade steps → detection → recovery) |
| `event chain` | Mermaid sequence diagram |
| `deployment sequence` | Numbered step list |
| `config resolution` | Numbered step list |
| _(unknown type)_ | Mermaid sequence diagram |

**Observations:**
- With code snippet: evidence card (finding + syntax-highlighted code + confidence badge)
- Without snippet: compact card (finding + file:line + confidence badge)
- Gap with recommendation: warning card with action
- Attached to a node/step: rendered inline near that node/step, not in a separate section

**Rationale:**
- Decision card: what was decided + context + trade-offs
- Alternatives shown as dismissed options

### 4. Render journey pages

Each journey becomes **one page**. Stories are sections within it.

Output: `<docs-dir>/<project>/index.astro` (default journey) and `<docs-dir>/<project>/<journey-id>.astro` (additional journeys).

**Page layout:**

```
+------------------------------------------------------------------+
|  [project name]                          [journey selector ▼]     |
+------------------------------------------------------------------+
|                                                                    |
|  ┌─ Story 1: MCP Agent Servers ────────────────────────────────┐  |
|  │  Summary paragraph (50-80 words)                            │  |
|  │                                                              │  |
|  │  [structure graph: 4 nodes]     [observation card]           │  |
|  │                                                              │  |
|  │  [rationale: why Express+MCP]                                │  |
|  └──────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  ┌─ Story 2: Agent Delegation Flow ────────────────────────────┐  |
|  │  Summary paragraph                                          │  |
|  │                                                              │  |
|  │  [sequence diagram: 5 steps]                                │  |
|  │                                                              │  |
|  │  [2 observation cards]                                       │  |
|  └──────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  ┌─ Story 3: ... ──────────────────────────────────────────────┐  |
|  │  ...                                                         │  |
|  └──────────────────────────────────────────────────────────────┘  |
|                                                                    |
+------------------------------------------------------------------+
```

**Story section rendering:**

Each story section contains:
1. **Title** — story title as a heading with anchor ID
2. **Summary** — the prose summary with bold node refs as clickable links
3. **Building blocks** — structures, flows, observations, rationale rendered per step 3
4. Blocks render in order: structures first, then flows, then rationale. Observations render inline where they're attached (via `observation_ids`), with unattached observations at the end.

**Section styling:**
- Each story is a card with a subtle border
- Story sections are separated by whitespace
- Structures and flows take the full card width
- Observation cards are compact (one line: finding + badge + file link)
- Rationale cards are compact (decision + trade-off in two lines)

### 5. Implement interactions

**Bold refs → graph nodes:**
- Parse `**bold text**` in summaries into `<span class="node-ref" data-node-id="...">` elements
- On click, scroll to and highlight the corresponding node in the nearest structure graph
- On hover, show tooltip with node description

**Flow step → sequence diagram:**
- Steps with `observation_ids` show a small badge on the corresponding diagram step

**Story navigation:**
- Sticky table of contents on the side (desktop) listing story titles
- Click to scroll to story section
- Journey selector dropdown switches between journey pages

### 6. Render the atlas page

Output: `<docs-dir>/<project>/atlas/index.astro`

Full interactive Cytoscape graph with:
- Cose-bilkent layout, expand/collapse hierarchy
- Node types colored by typeConfig
- Debt rings, pattern badges, tooltips
- Story overlay: hovering a node shows "In N stories" badge
- Coverage indicator: undocumented nodes get dashed border

### 7. Render the facts index

Output: `<docs-dir>/<project>/facts/index.astro`

Searchable table of all observations across all stories:
- Finding text, source story (linked), component, evidence file:line, confidence badge, tags
- Text search, filter by tag/story/type/confidence

### 8. Path resolution

Resolve docs output location (in order):
1. `$KORDINATE_HOME/../site/` → use it
2. `site/` in kordinate repo root → use it
3. Fallback: `<project>/.kord/agents/scribe/output/docs/`

Within resolved root:
- `src/pages/<project>/index.astro` (default journey)
- `src/pages/<project>/<journey-id>.astro` (additional journeys)
- `src/pages/<project>/atlas/index.astro`
- `src/pages/<project>/facts/index.astro`

### 9. Technical requirements

**Shared across all pages:**
- Self-contained: inline CSS/JS
- CDN: Cytoscape.js + dagre (lazy, on interaction), Mermaid (lazy, on tab visibility)
- CSS custom properties for dark/light mode
- Responsive: stories stack vertically on mobile, atlas degrades to static SVG

**Node type styling:**

| Type | Color | Shape |
|------|-------|-------|
| `service` | Blue (#3B82F6) | Rounded rectangle |
| `library` | Slate (#64748B) | Rounded rectangle |
| `worker` | Indigo (#6366F1) | Rounded rectangle |
| `api` | Green (#22C55E) | Rounded rectangle |
| `frontend` | Purple (#A855F7) | Rounded rectangle |
| `store` | Amber (#F59E0B) | Cylinder |
| `gateway` | Rose (#F43F5E) | Hexagon |
| `broker` | Orange (#F97316) | Hexagon |
| `external` | Red (#EF4444) | Octagon |
| `actor` | Teal (#14B8A6) | Ellipse |

**Severity colors:** Critical=#EF4444, High=#F97316, Medium=#F59E0B, Low=#22C55E

**Confidence badges:** High=solid green, Medium=outline amber, Low=outline gray

### 10. Report

```
## Documentation: <project>

**Default journey**: <path> (N stories)
**Additional journeys**: <list>
**Atlas page**: <path>
**Facts index**: <path> (N observations)

### Stories rendered
| Story | Blocks | Visualizations |
|-------|--------|---------------|
| MCP Agent Servers | 1 structure (4 nodes), 2 observations | dagre graph, evidence cards |
| Agent Delegation | 1 flow (5 steps), 1 rationale | sequence diagram, decision card |

### Coverage
- Atlas nodes: N total, M in stories (<percentage>%)
- Undocumented critical nodes: [list or "none"]
```

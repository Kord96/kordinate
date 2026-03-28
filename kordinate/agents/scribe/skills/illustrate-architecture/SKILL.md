---
name: illustrate-architecture
description: >
  Generate an interactive architecture explorer page from Designer's project analysis.
  Reads architecture.yaml, patterns.md, dependencies.md, api-review.md, and debt-assessment.md
  from project memory, then produces an Astro page with Cytoscape.js graph, narrative sidebar,
  and bottom drawer.
argument-hint: "<project> [--narrative <dir>]"
curated: true
scope: global
---

Generate an interactive architecture explorer page by reading all of Designer's project memory artifacts and producing a self-contained Astro page with a Cytoscape.js graph, a narrative sidebar, and a bottom drawer for detail inspection.

## Arguments

`$ARGUMENTS` — Required: `<project>` (e.g., `logbd`, `stoik`, `sous-storefront`). Optional: `--narrative <dir>` to supply hand-written narrative markdown files instead of auto-generated stubs.

## Procedure

### 1. Parse and locate

Parse project name from `$ARGUMENTS`. Extract `--narrative <dir>` if present.

Locate the project directory by checking paths in order:
- `~/<project>/`
- `~/repos/<project>/`
- `~/test-repos/<project>/`
- If `$ARGUMENTS` starts with `/`, treat it as an absolute path

If not found, report which paths were checked and exit.

### 2. Ensure fresh analysis via kord

Invoke `/kord designer project-analysis <project-path>` to ensure Designer's analyses are up to date. This runs the full analysis suite (detect-patterns, map-dependencies, review-api, assess-debt, architect) with cache-aware skipping.

If the kord returns an error, check whether `architecture.yaml` already exists and proceed with stale data. Report the staleness in the final output.

### 3. Read Designer memories

Read from `<project>/.kord/agents/designer/memory/`:

| File | Required | Purpose |
|------|----------|---------|
| `architecture.yaml` | **yes** | Core structure — abort if missing |
| `patterns.md` | no | Enriches nodes with pattern badges |
| `dependencies.md` | no | Enriches external service nodes |
| `api-review.md` | no | Adds API endpoint mapping to nodes |
| `debt-assessment.md` | no | Adds health coloring per node |

If `architecture.yaml` is missing after the kord attempt, report and suggest running `/designer:architect <project>` directly. Exit.

### 4. Build architecture.json

Transform `architecture.yaml` into the JSON format described in [explorer-schema.md](explorer-schema.md). This is the data file the explorer page consumes.

**Base transform** (from architecture.yaml alone):

- Each **component** becomes a node with: `id`, `label` (from `name`), `type`, `group` (from capabilities or inferred tier), `dependsOn` array
- Each **component with children** gets child nodes nested under `parent`
- Each **depends_on** relationship becomes an edge: `{ source, target, label }`
- Each **external_dependency** becomes a node with `type: "external"` and `group: "external"`
- Each **actor** becomes a node with `type: "actor"` and `group: "actors"`
- Each **data_flow** becomes a flow object with ordered steps
- Each **state** entry becomes a node with `type: "store"` and metadata
- Each **failure_mode** becomes a failure object with affected node IDs and severity
- **capabilities** define the group boundaries for visual clustering

**Enrichments** (from optional files):

- **Pattern badges** (from `patterns.md`): For each detected pattern, find which components it maps to (from the "Where" / "Components" / mapping column). Add a `patterns` array to matching nodes with `{ name, category }`.
- **Debt markers** (from `debt-assessment.md`): For each violation or debt item, map it to affected components. Add a `debt` object to matching nodes with `{ severity, items: [{ title, description }] }`. Severity drives node border coloring: critical = red, high = orange, medium = yellow.
- **API endpoints** (from `api-review.md`): Map handler functions/routes to component nodes. Add an `endpoints` array to matching nodes with `{ method, path, description }`.
- **External deps enrichment** (from `dependencies.md`): Ensure all external services from dependencies.md are represented as external nodes. Add `resilience` metadata (timeout, retry, circuit breaker) and `criticality` to external nodes.

Write `architecture.json` to `<docs-content-dir>/<project>/architecture.json`. See step 7 for path resolution.

### 5. Write narrative

The sidebar narrative is the story that guides readers through the architecture. It is not a bullet-point list — it is **prose that Scribe writes**, using everything learned from the Designer memories.

Write one markdown file per tab into `<docs-content-dir>/<project>/narrative/`:

- **`structure.md`** — The system overview. Open with a 2-3 sentence summary of what the project does and how it's structured. Then one section per capability/module group: what it does, why it exists, how it relates to other groups. Reference component names in bold so the explorer can link them. Mention detected patterns where relevant ("The API layer follows a **hexagonal** architecture — handlers delegate to ports, never touching infrastructure directly."). If debt was detected, weave it in naturally ("The **UserService** has accumulated technical debt — 3 CRITICAL violations around missing circuit breakers.").

- **`flows.md`** — Data flow walkthroughs. One section per flow, written as a narrative: "When a user adds an item to their cart, the **CartDrawer** component dispatches an action to the **cart store**. The store persists to localStorage and triggers a re-render..." Not a numbered list of steps — a story that traces data through the system.

- **`data.md`** — State and storage narrative. Group by purpose (source of truth, cache, derived). Explain what each store holds, who reads it, who writes it, and what consistency guarantees exist.

- **`resilience.md`** — Failure modes narrative. Order by severity. For each: what triggers it, what breaks, what the user sees, and how to recover. Written as scenarios, not tables.

**If `--narrative <dir>` is provided**: read existing markdown files from that directory. Use them as-is for the tabs they cover. For tabs without a file, write new narrative as above.

Each heading in the narrative should use `{#component-id}` syntax to anchor it to a graph node for bidirectional linking. For example: `## API Layer {#api-gateway}`.

### 6. Write the explorer page

Write a self-contained Astro page to `<docs-pages-dir>/<project>/index.astro`.

The page structure:

```
+------------------------------------------------------------------+
|  [project name] Architecture Explorer          [tab1][tab2][tab3] |
+-------------------------------------------+----------------------+
|                                           |                      |
|                                           |  Narrative Sidebar   |
|           Cytoscape.js Graph              |  (tabbed markdown)   |
|           (interactive)                   |                      |
|                                           |  - Structure         |
|                                           |  - Flows             |
|                                           |  - Data              |
|                                           |  - Resilience        |
+-------------------------------------------+----------------------+
|  Bottom Drawer (click a node to inspect)                         |
|  - Component detail, patterns, debt, endpoints, failure modes    |
+------------------------------------------------------------------+
```

**Graph panel** (Cytoscape.js):
- Load `architecture.json` at build time via Astro's content layer or inline as a `<script>` data blob
- Nodes colored by type: service=blue, library=gray, api=green, store=amber, frontend=purple, external=red, actor=teal, worker=indigo
- Debt-affected nodes get a colored border ring (red/orange/yellow by severity)
- Pattern badges shown as small pill labels below node name
- Edges styled by relationship: solid for depends_on, dashed for async/event
- Layout: `dagre` (top-to-bottom) for structural view, `breadthfirst` for flow view
- Click a node to populate the bottom drawer
- Hover shows tooltip with component description
- Zoom, pan, fit-to-screen controls

**Narrative sidebar**:
- Tabbed interface: Structure | Flows | Data | Resilience
- Render the narrative markdown for each tab
- Clicking a component name in the narrative highlights the node in the graph

**Bottom drawer**:
- Hidden by default, slides up on node click
- Shows: component name, description, type, patterns (as pills), debt items (as warnings), API endpoints (as a mini table), failure modes affecting this node, dependencies (in and out)
- Close button to dismiss

**Technical requirements for the Astro page**:
- Self-contained: inline all JS/CSS, load Cytoscape.js and dagre layout from CDN (`https://unpkg.com/cytoscape@3/dist/cytoscape.min.js`, `https://unpkg.com/cytoscape-dagre@2/cytoscape-dagre.js`, `https://unpkg.com/dagre@0.8/dist/dagre.min.js`)
- Use Astro's `<script>` tag for client-side interactivity
- Use CSS custom properties for theming (works with Starlight's dark/light mode)
- Responsive: sidebar collapses to overlay on mobile
- The page should work both in dev mode and as a built static page

### 7. Path resolution for output

The docs site content lives at (resolve in order):
1. If `$KORDINATE_HOME/../site/` exists, use it (PVC layout: `kordinate/site/`)
2. If a `site/` directory exists in the kordinate repo root, use it
3. Otherwise create output at `<project>/.kord/agents/scribe/output/architecture-explorer/`

Within the resolved docs root:
- Pages: `src/pages/<project>/index.astro`
- Content: `src/content/docs/<project>/architecture.json`
- Narrative: `src/content/docs/<project>/narrative/*.md`

If the docs site path does not exist (option 3 fallback), write all files into the project-local output directory and report that the user should copy them to the docs site manually.

### 8. Report

Output a summary:

```
## Architecture Explorer: <project>

**Page**: <path to index.astro>
**Data**: <path to architecture.json>
**Narrative**: <path to narrative dir> (N files)

### Enrichments included
- Patterns: yes/no (N patterns mapped to M nodes)
- Debt: yes/no (N items across M nodes)
- API endpoints: yes/no (N endpoints mapped)
- External deps: yes/no (N services)

### Graph stats
- Nodes: N (components: X, external: Y, actors: Z)
- Edges: N
- Flows: N
- Failure modes: N

### Notes
- <any warnings, stale data notices, missing optional files>
```
